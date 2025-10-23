from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import (TEKKEN_CHARS, TEKKEN_RANKS, REGIONS, calculate_stats,
                   calculate_matchup_stats, calculate_player_stats,
                   get_used_characters, get_used_character_stats,
                   get_character_image_url)
# Importar funções do SQLite Database
from database import (init_db, get_all_matches, add_match as db_add_match,
                     get_all_players, add_player as db_add_player,
                     get_player_by_id, clear_all_matches)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar o logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Inicializar o database
init_db()

# adiciona url de imagens ao jinja
app.jinja_env.globals.update(get_character_image_url=get_character_image_url)

# Embrulhar funções à interface antiga
def load_matches():
    """Load all matches from SQLite database"""
    return get_all_matches()

def load_players():
    """Load all players from SQLite database"""
    return get_all_players()


@app.route('/')
def index():
    matches = load_matches()
    stats = calculate_stats(matches)

    return render_template('index.html', matches=matches, stats=stats, chars=TEKKEN_CHARS)


@app.route('/add', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        # Pegar a seleção de personagens
        p1_char = request.form['player1']
        p2_char = request.form['player2']
        winner_char = request.form['winner']

        new_match = {
            "id": int(datetime.now().timestamp() * 1000),
            "timestamp": datetime.now().isoformat(),
            "player1": p1_char,
            "player2": p2_char,
            "winner": winner_char,
            # Manter ambos os formatos para compatibilidade
            "player1_char": p1_char,
            "player2_char": p2_char,
            "winner_char": winner_char
        }

        # Save to database instead of JSON Salvar no database ao invés de JSON
        db_add_match(new_match)
        return redirect(url_for('index'))

    return render_template("add_match.html", chars=TEKKEN_CHARS)




RENDER_PATHS = [
    "static/renders",
    "static/renders/tekken7",
]

def generate_placeholder_image(character_name):
    """Gerar um placeholder para o personagem primeiro"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Criar imagem com cores que combinam
        img = Image.new('RGBA', (200, 200), (30, 30, 40, 255))
        draw = ImageDraw.Draw(img)

        # Desenhar um circulo no fundo
        draw.ellipse([20, 20, 180, 180], fill=(255, 60, 40, 255))

        # Pegar a inicial do personagem
        initial = character_name[0].upper() if character_name else '?'

        # Tenta usar uma fonte, caso o contrário usar a padrão
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()

        # Desenha o texto
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (200 - text_width) // 2
        text_y = (200 - text_height) // 2 - 10

        draw.text((text_x, text_y), initial, fill=(255, 255, 255, 255), font=font)

        # Salvar no static/renders se o diretório existir
        os.makedirs('static/renders', exist_ok=True)
        placeholder_path = os.path.join('static/renders', f'{character_name.lower()}_placeholder.png')
        img.save(placeholder_path, 'PNG')

        return placeholder_path
    except ImportError:
        # Se o PIL não estiver disponível, retornar None
        return None
    except Exception as e:
        # Encontrar erros durante a geração
        logger.error(f"Failed to generate placeholder image for {character_name}: {str(e)}")
        return None

@app.route("/render/<name>")
def get_render(name):
    """
    Serve character render images with intelligent fallback

    Search order:
    1. Look in all configured RENDER_PATHS for the character image
    2. Try with .png extension
    3. Try with .jpg extension
    4. Generate placeholder if PIL is available
    5. Fall back to default.png
    """
    name_lower = name.lower()

    # Tenta encontrar a imagem primeiro
    for path in RENDER_PATHS:
        for ext in ['.png', '.jpg', '.jpeg']:
            filename = name_lower + ext
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                return send_from_directory(path, filename)

    # Tenta gerar o placeholder de forma segura no try-except
    try:
        placeholder = generate_placeholder_image(name)
        if placeholder:
            placeholder_filename = os.path.basename(placeholder)
            placeholder_path = os.path.join('static', 'renders', placeholder_filename)
            if os.path.exists(placeholder_path):
                return send_from_directory('static/renders', placeholder_filename)
    except Exception as e:
        # Log error but continue to fallback Erro no log mas continua realizando fallback
        logger.warning(f"Error generating placeholder for {name}: {e}")

    #  Fallback final para o default.png - funciona sempre
    try:
        return send_from_directory('static/renders', 'default.png')
    except Exception as e:
        logger.error(f"Error serving default.png: {e}")
        abort(404)

@app.route('/players')
def players_list():
    players = load_players()
    matches = load_matches()

    player_rankings = []
    for player in players:
        player_stats = calculate_player_stats(player['id'], matches, players)
        if player_stats:
            player_rankings.append({
                'player': player,
                'stats': player_stats
            })

    # Ordenar por vitórias e depois por taxa de vitória
    player_rankings.sort(key=lambda x: (x['stats']['wins'], float(x['stats']['winrate'].rstrip('%'))), reverse=True)

    return render_template('players.html', player_rankings=player_rankings)


@app.route('/player/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        new_player = {
            'id': request.form['player_id'],
            'name': request.form['name'],
            'main_char': request.form['main_char'],
            'rank': request.form['rank'],
            'region': request.form['region']
        }

        # Verificar se o jogador existe
        existing_player = get_player_by_id(new_player['id'])
        if existing_player:
            logger.warning(f"Attempt to add duplicate player ID: {new_player['id']}")
            return "Player ID already exists!", 400

        # Salvar no database
        db_add_player(new_player)
        return redirect(url_for('players_list'))

    return render_template('add_player.html', chars=TEKKEN_CHARS, ranks=TEKKEN_RANKS, regions=REGIONS)


@app.route('/player/<player_id>')
def player_profile(player_id):
    players = load_players()
    matches = load_matches()

    player = next((p for p in players if p['id'] == player_id), None)
    if not player:
        abort(404)

    stats = calculate_player_stats(player_id, matches, players)

    return render_template('player_profile.html', player=player, stats=stats)


@app.route('/matchups')
def matchups():
    matches = load_matches()
    matchup_stats = calculate_matchup_stats(matches)

    # Ordenar pelas matchups mais jogadas
    matchup_list = list(matchup_stats.values())
    matchup_list.sort(key=lambda x: x['total'], reverse=True)

    return render_template('matchups.html', matchups=matchup_list)


@app.route('/character-stats')
def character_stats():
    # Página de estátiscas dos personagens
    return render_template('character_stats.html')


@app.route('/clear')
def clear_data():
    #  Limpar todas as partidas do database
    clear_all_matches()
    return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    # Retornar dados de apenas personagens usados
    matches = load_matches()

    used_stats = get_used_character_stats(matches)

    # Formato para as tabelas
    char_data = {
        'labels': list(used_stats.keys()),
        'wins': [stats['wins'] for stats in used_stats.values()],
        'matches': [stats['matches'] for stats in used_stats.values()],
        'winrates': [float(stats['winRate'].rstrip('%')) for stats in used_stats.values()]
    }

    return jsonify(char_data)


@app.route('/api/used-characters')
def api_used_characters():
    # Retornar lista dos personagens que foram usados
    matches = load_matches()
    used_chars = get_used_characters(matches)

    return jsonify({
        'total': len(used_chars),
        'characters': used_chars
    })


@app.route('/api/character-usage')
def api_character_usage():
    # Retornar estatisticas de uso dos personagens
    matches = load_matches()
    used_stats = get_used_character_stats(matches)

    usage_data = []
    for char, stats in used_stats.items():
        usage_data.append({
            'character': char,
            'wins': stats['wins'],
            'matches': stats['matches'],
            'usage': stats['usage'],
            'winRate': stats['winRate']
        })

    return jsonify(usage_data)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    logger.info(f"Iniciando Tekken Stats em {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])