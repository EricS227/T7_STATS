from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
import os
from datetime import datetime
from utils import (TEKKEN_CHARS, TEKKEN_RANKS, REGIONS, calculate_stats,
                   calculate_matchup_stats, calculate_player_stats,
                   get_used_characters, get_used_character_stats,
                   get_character_image_url)
# bring in database stuff
from database import (init_db, get_all_matches, add_match as db_add_match,
                     get_all_players, add_player as db_add_player,
                     get_player_by_id, clear_all_matches)

app = Flask(__name__)

# setup the database when we start
init_db()

# make image function available in templates
app.jinja_env.globals.update(get_character_image_url=get_character_image_url)

# quick helpers to load data
def load_matches():
    """grab all matches from the database"""
    return get_all_matches()

def load_players():
    """grab all players from the database"""
    return get_all_players()


@app.route('/')
def index():
    matches = load_matches()
    stats = calculate_stats(matches)

    return render_template('index.html', matches=matches, stats=stats, chars=TEKKEN_CHARS)


@app.route('/add', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        # get what the user picked
        p1_char = request.form['player1']
        p2_char = request.form['player2']
        winner_char = request.form['winner']

        new_match = {
            "id": int(datetime.now().timestamp() * 1000),
            "timestamp": datetime.now().isoformat(),
            "player1": p1_char,
            "player2": p2_char,
            "winner": winner_char,
            # storing it both ways just to be safe
            "player1_char": p1_char,
            "player2_char": p2_char,
            "winner_char": winner_char
        }

        # throw it in the database
        db_add_match(new_match)
        return redirect(url_for('index'))

    return render_template("add_match.html", chars=TEKKEN_CHARS)




# figure out where we're running from so paths work anywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# where to look for character images
RENDER_PATHS = [
    os.path.join(BASE_DIR, "static", "renders"),
    os.path.join(BASE_DIR, "static", "renders", "tekken7"),
    os.path.join(BASE_DIR, "static", "renders", "tekken8")
]

def generate_placeholder_image(character_name):
    """make a quick placeholder if we don't have the actual character image"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # making a 200x200 image with dark colors
        img = Image.new('RGBA', (200, 200), (30, 30, 40, 255))
        draw = ImageDraw.Draw(img)

        # draw a red circle
        draw.ellipse([20, 20, 180, 180], fill=(255, 60, 40, 255))

        # grab the first letter of the character's name
        initial = character_name[0].upper() if character_name else '?'

        # use arial if we can find it, otherwise whatever's default
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()

        # center the text in the circle
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (200 - text_width) // 2
        text_y = (200 - text_height) // 2 - 10

        draw.text((text_x, text_y), initial, fill=(255, 255, 255, 255), font=font)

        # save it to the renders folder
        os.makedirs('static/renders', exist_ok=True)
        placeholder_path = os.path.join('static/renders', f'{character_name.lower()}_placeholder.png')
        img.save(placeholder_path, 'PNG')

        return placeholder_path
    except ImportError:
        # pillow isn't installed
        return None
    except Exception as e:
        # something went wrong
        print(f"Failed to generate placeholder image for {character_name}: {str(e)}")
        return None

@app.route("/render/<name>")
def get_render(name):
    """
    serve up character images - tries a few places and falls back to placeholders

    looks for images in this order:
    1. actual character renders in the folders
    2. tries .png, .jpg, .jpeg extensions
    3. generates a placeholder with the character's initial
    4. worst case just shows the default image
    """
    name_lower = name.lower()

    print(f"\n=== Looking for image: {name} (normalized: {name_lower}) ===")
    print(f"Current working directory: {os.getcwd()}")

    # see if we have an actual image for this character
    for path in RENDER_PATHS:
        for ext in ['.png', '.jpg', '.jpeg']:
            filename = name_lower + ext
            full_path = os.path.join(path, filename)
            abs_full_path = os.path.abspath(full_path)

            print(f"Checking: {full_path}")
            print(f"  Absolute: {abs_full_path}")
            print(f"  Exists: {os.path.exists(abs_full_path)}")

            if os.path.exists(abs_full_path):
                abs_path = os.path.abspath(path)
                print(f"✓ FOUND! Serving {filename} from {abs_path}")
                return send_from_directory(abs_path, filename)

    print(f"No image found in paths, trying placeholder generation...")

    # no image found, let's make a placeholder
    try:
        placeholder = generate_placeholder_image(name)
        if placeholder:
            placeholder_filename = os.path.basename(placeholder)
            placeholder_path = os.path.join('static', 'renders', placeholder_filename)
            print(f"Generated placeholder: {placeholder_path}")
            if os.path.exists(placeholder_path):
                abs_renders = os.path.abspath('static/renders')
                print(f"✓ Serving placeholder: {placeholder_filename}")
                return send_from_directory(abs_renders, placeholder_filename)
    except Exception as e:
        print(f"Error generating placeholder for {name}: {e}")

    # ok nothing worked, just show the default
    print(f"Falling back to default.png")
    try:
        abs_renders = os.path.abspath('static/renders')
        return send_from_directory(abs_renders, 'default.png')
    except Exception as e:
        print(f"Error serving default.png: {e}")
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

    # put the best players at the top
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

        # make sure we don't have this player already
        existing_player = get_player_by_id(new_player['id'])
        if existing_player:
            return "Player ID already exists!", 400

        # all good, add them
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

    # show the most common matchups first
    matchup_list = list(matchup_stats.values())
    matchup_list.sort(key=lambda x: x['total'], reverse=True)

    return render_template('matchups.html', matchups=matchup_list)


@app.route('/character-stats')
def character_stats():
    # just the stats page template
    return render_template('character_stats.html')


@app.route('/clear')
def clear_data():
    # wipe everything and start fresh
    clear_all_matches()
    return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    # send back chart data for the characters that actually got played
    matches = load_matches()

    used_stats = get_used_character_stats(matches)

    # package it up for chart.js
    char_data = {
        'labels': list(used_stats.keys()),
        'wins': [stats['wins'] for stats in used_stats.values()],
        'matches': [stats['matches'] for stats in used_stats.values()],
        'winrates': [float(stats['winRate'].rstrip('%')) for stats in used_stats.values()]
    }

    return jsonify(char_data)


@app.route('/api/used-characters')
def api_used_characters():
    # which characters have seen some action
    matches = load_matches()
    used_chars = get_used_characters(matches)

    return jsonify({
        'total': len(used_chars),
        'characters': used_chars
    })


@app.route('/api/character-usage')
def api_character_usage():
    # detailed usage breakdown
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
    app.run(debug=True)