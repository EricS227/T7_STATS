from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
import json, os
from datetime import datetime
from utils import (TEKKEN_CHARS, TEKKEN_RANKS, REGIONS, calculate_stats,
                   calculate_matchup_stats, calculate_player_stats,
                   get_used_characters, get_used_character_stats,
                   get_character_image_url)

app = Flask(__name__)
DATA_FILE = 'data/matches.json'
PLAYERS_FILE = 'data/players.json'

# Make get_character_image_url available in all templates
app.jinja_env.globals.update(get_character_image_url=get_character_image_url)


def save_matches(matches):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(matches, f, indent=2)

def load_matches():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_players(players):
    os.makedirs(os.path.dirname(PLAYERS_FILE), exist_ok=True)
    with open(PLAYERS_FILE, 'w') as f:
        json.dump(players, f, indent=2)

def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'r') as f:
            return json.load(f)
    return []


@app.route('/')
def index():
    matches = load_matches()
    stats = calculate_stats(matches)

    return render_template('index.html', matches=matches, stats=stats, chars=TEKKEN_CHARS)


@app.route('/add', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        matches = load_matches()

        # Get character selections directly
        p1_char = request.form['player1']
        p2_char = request.form['player2']
        winner_char = request.form['winner']

        new_match = {
            "id": int(datetime.now().timestamp() * 1000),
            "timestamp": datetime.now().isoformat(),
            "player1": p1_char,
            "player2": p2_char,
            "winner": winner_char,
            # Also add new format for compatibility
            "player1_char": p1_char,
            "player2_char": p2_char,
            "winner_char": winner_char
        }
        matches.append(new_match)
        save_matches(matches)
        return redirect(url_for('index'))

    return render_template("add_match.html", chars=TEKKEN_CHARS)




RENDER_PATHS = [
    "static/renders",
    "static/renders/tekken7",
    "static/renders/tekken8"
]

@app.route("/render/<name>")
def get_render(name):
    name = name.lower() + ".png"

    for path in RENDER_PATHS:
        full_path = os.path.join(path, name)
        if os.path.exists(full_path):
            return send_from_directory(path, name)
        

    return send_from_directory("static/renders", "default.png")

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

    # Sort by wins
    player_rankings.sort(key=lambda x: (x['stats']['wins'], float(x['stats']['winrate'].rstrip('%'))), reverse=True)

    return render_template('players.html', player_rankings=player_rankings)


@app.route('/player/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        players = load_players()

        new_player = {
            'id': request.form['player_id'],
            'name': request.form['name'],
            'main_char': request.form['main_char'],
            'rank': request.form['rank'],
            'region': request.form['region']
        }

        # Check if player ID already exists
        if any(p['id'] == new_player['id'] for p in players):
            return "Player ID already exists!", 400

        players.append(new_player)
        save_players(players)
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

    # Convert to list and sort by total matches
    matchup_list = list(matchup_stats.values())
    matchup_list.sort(key=lambda x: x['total'], reverse=True)

    return render_template('matchups.html', matchups=matchup_list)


@app.route('/character-stats')
def character_stats():
    """Character statistics page with win rates and popularity"""
    return render_template('character_stats.html')


@app.route('/clear')
def clear_data():
    save_matches([])
    return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    """API endpoint for chart data - returns only used characters"""
    matches = load_matches()

    # Use the new function to get only used character stats
    used_stats = get_used_character_stats(matches)

    # Prepare data for charts
    char_data = {
        'labels': list(used_stats.keys()),
        'wins': [stats['wins'] for stats in used_stats.values()],
        'matches': [stats['matches'] for stats in used_stats.values()],
        'winrates': [float(stats['winRate'].rstrip('%')) for stats in used_stats.values()]
    }

    return jsonify(char_data)


@app.route('/api/used-characters')
def api_used_characters():
    """API endpoint that returns list of characters that have been used"""
    matches = load_matches()
    used_chars = get_used_characters(matches)

    return jsonify({
        'total': len(used_chars),
        'characters': used_chars
    })


@app.route('/api/character-usage')
def api_character_usage():
    """API endpoint showing character usage statistics"""
    matches = load_matches()
    used_stats = get_used_character_stats(matches)

    # Format for easy consumption
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