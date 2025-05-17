from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
import json, os
from utils import TEKKEN_CHARS, calculate_stats

app = Flask(__name__)
DATA_FILE = 'data/matches.json'


def load_matches():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []



def save_matches(matches):
    with open(DATA_FILE, 'w') as f:
        json.dump(matches, f, indent=2)


@app.route('/')

def index():
    matches = load_matches()
    stats = calculate_stats(matches)
    return render_template('index.html', matches=matches, stats=stats, chars=TEKKEN_CHARS, matches=matches)


@app.route('/add', methods=['GET', 'POST'])

def add_match():
    if request.method == 'POST':
        matches = load_matches()
        new_match = {
            "id": int(os.times().elapsed),
            "player1": request.form['player1'],
            "player2": request.form['player2'],
            "winner": request.form['winner']
        }
        matches.append(new_match)
        save_matches(matches)
        return redirect(url_for('index'))
    
    return render_template("add_match.html", chars=TEKKEN_CHARS)




RENDER_PATHS = [
    "static/renders"
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

@app.route('/clear')
def clear_data():
    save_matches([])
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)