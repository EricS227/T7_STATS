TEKKEN_CHARS = [
    'Akuma', 'Alisa', 'Asuka', 'Bob', 'Bryan', 'Claudio', 'Devil Jin', 'Dragunov',
    'Eddy', 'Eliza', 'Feng', 'Geese', 'Gigas', 'Heihachi', 'Hwoarang', 'Jack-7', 'Jin',
    'Josie', 'Katarina', 'Kazumi', 'Kazuya', 'King', 'Kuma', 'Lars', 'Law', 'Lee', 'Lei',
    'Leo', 'Lili', 'Lucky Chloe', 'Master Raven', 'Miguel', 'Nina', 'Noctis', 'Paul',
    'Shaheen', 'Steve', 'Xiaoyu', 'Yoshimitsu'
]


def calculate_stats(matches):
    stats = {char: {"wins": 0, "matches": 0, "usage": 0, "winRate": "0"} for char in TEKKEN_CHARS}

    for match in matches:
        p1 = match['player1']
        p2 = match['player2']
        winner = match['winner']


        stats[p1]["matches"] += 1
        stats[p2]["matches"] += 1
        stats[p1]["usage"] += 1
        stats[p2]["usage"] += 1

        stats[winner]["wins"] += 1

    for char in TEKKEN_CHARS:
        if stats[char]["matches"] > 0:
            win_rate = (stats[char]["wins"] / stats[char]["matches"]) * 100
            stats[char]["winRate"] = f"{win_rate:.1f}"

    return stats