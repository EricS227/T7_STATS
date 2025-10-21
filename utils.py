TEKKEN_CHARS = [
    'Akuma', 'Alisa', 'Asuka', 'Bob', 'Bryan', 'Claudio', 'Devil Jin', 'Dragunov',
    'Eddy', 'Eliza', 'Feng', 'Geese', 'Gigas', 'Heihachi', 'Hwoarang', 'Jack-7', 'Jin',
    'Josie', 'Katarina', 'Kazumi', 'Kazuya', 'King', 'Kuma', 'Lars', 'Law', 'Lee', 'Lei',
    'Leo', 'Lili', 'Lucky Chloe', 'Master Raven', 'Miguel', 'Nina', 'Noctis', 'Paul',
    'Shaheen', 'Steve', 'Xiaoyu', 'Yoshimitsu'
]

TEKKEN_RANKS = [
    'Beginner', '1st Dan', '2nd Dan', '3rd Dan', '4th Dan', '5th Dan', '6th Dan', '7th Dan', '8th Dan', '9th Dan',
    '1st Kyu', '2nd Kyu', '3rd Kyu', '4th Kyu', '5th Kyu', '6th Kyu', '7th Kyu', '8th Kyu', '9th Kyu',
    'Fighter', 'Strategist', 'Combatant', 'Brawler', 'Ranger', 'Cavalry', 'Warrior', 'Assailant', 'Dominator', 'Vanquisher',
    'Destroyer', 'Savior', 'Overlord', 'Genbu', 'Byakko', 'Seiryu', 'Suzaku', 'Mighty Ruler', 'Revered Ruler', 'Divine Ruler',
    'Eternal Ruler', 'Fujin', 'Raijin', 'Yaksa', 'Ryujin', 'Emperor', 'Tekken King', 'Tekken God', 'True Tekken God', 'Tekken God Prime'
]

REGIONS = ['North America', 'Europe', 'Asia', 'South America', 'Oceania', 'Africa', 'Middle East']


def get_character_image_url(character_name):
    # converte o nome do personagem pra formato de URL
    # Jin -> /render/jin, Devil Jin -> /render/devil_jin, etc
    normalized_name = character_name.lower().replace(' ', '_').replace('-', '_')
    return f"/render/{normalized_name}"


def calculate_stats(matches):
    stats = {char: {"wins": 0, "matches": 0, "usage": 0, "winRate": "0%"} for char in TEKKEN_CHARS}

    for match in matches:
        # aceita tanto o formato antigo quanto o novo de partidas
        p1_char = match.get('player1_char', match.get('player1'))
        p2_char = match.get('player2_char', match.get('player2'))
        winner_char = match.get('winner_char', match.get('winner'))

        stats[p1_char]["matches"] += 1
        stats[p2_char]["matches"] += 1
        stats[p1_char]["usage"] += 1
        stats[p2_char]["usage"] += 1

        stats[winner_char]["wins"] += 1

    for char in TEKKEN_CHARS:
        if stats[char]["matches"] > 0:
            win_rate = (stats[char]["wins"] / stats[char]["matches"]) * 100
            stats[char]["winRate"] = f"{win_rate:.1f}%"

    return stats


def calculate_matchup_stats(matches):
    # calcula as taxas de vitória nos confrontos entre personagens
    matchups = {}

    for match in matches:
        p1_char = match.get('player1_char', match.get('player1'))
        p2_char = match.get('player2_char', match.get('player2'))
        winner_char = match.get('winner_char', match.get('winner'))

        # ordena alfabeticamente pra evitar chaves duplicadas
        chars = sorted([p1_char, p2_char])
        key = f"{chars[0]}_vs_{chars[1]}"

        if key not in matchups:
            matchups[key] = {
                'char1': chars[0],
                'char2': chars[1],
                'char1_wins': 0,
                'char2_wins': 0,
                'total': 0
            }

        matchups[key]['total'] += 1

        if winner_char == chars[0]:
            matchups[key]['char1_wins'] += 1
        else:
            matchups[key]['char2_wins'] += 1

    # calcula as porcentagens de vitória
    for key in matchups:
        m = matchups[key]
        if m['total'] > 0:
            m['char1_winrate'] = f"{(m['char1_wins'] / m['total']) * 100:.1f}%"
            m['char2_winrate'] = f"{(m['char2_wins'] / m['total']) * 100:.1f}%"

    return matchups


def calculate_player_stats(player_id, matches, players):
    # calcula as estatísticas de um jogador específico
    player = next((p for p in players if p['id'] == player_id), None)
    if not player:
        return None

    stats = {
        'total_matches': 0,
        'wins': 0,
        'losses': 0,
        'winrate': '0%',
        'character_stats': {},
        'recent_matches': []
    }

    for match in matches:
        p1_id = match.get('player1_id')
        p2_id = match.get('player2_id')
        winner_id = match.get('winner_id')

        if p1_id == player_id or p2_id == player_id:
            stats['total_matches'] += 1

            if winner_id == player_id:
                stats['wins'] += 1
            else:
                stats['losses'] += 1

            # rastreia quais personagens eles usam
            char_used = match.get('player1_char') if p1_id == player_id else match.get('player2_char')
            if char_used not in stats['character_stats']:
                stats['character_stats'][char_used] = {'wins': 0, 'matches': 0}

            stats['character_stats'][char_used]['matches'] += 1
            if winner_id == player_id:
                stats['character_stats'][char_used]['wins'] += 1

            stats['recent_matches'].append(match)

    if stats['total_matches'] > 0:
        stats['winrate'] = f"{(stats['wins'] / stats['total_matches']) * 100:.1f}%"

    # mantém só as últimas 20 partidas
    stats['recent_matches'] = sorted(
        stats['recent_matches'],
        key=lambda x: x.get('timestamp', 0),
        reverse=True
    )[:20]

    return stats


def get_used_characters(matches):
    # pega a lista de personagens que já foram usados
    used_chars = set()

    for match in matches:
        p1_char = match.get('player1_char', match.get('player1'))
        p2_char = match.get('player2_char', match.get('player2'))

        if p1_char:
            used_chars.add(p1_char)
        if p2_char:
            used_chars.add(p2_char)

    return sorted(list(used_chars))


def get_used_character_stats(matches):
    # retorna estatísticas só dos personagens que já foram usados
    all_stats = calculate_stats(matches)

    # filtra personagens com 0 partidas
    used_stats = {
        char: stats
        for char, stats in all_stats.items()
        if stats['matches'] > 0
    }

    # ordena por taxa de vitória e depois por partidas
    sorted_stats = dict(sorted(
        used_stats.items(),
        key=lambda x: (float(x[1]['winRate'].rstrip('%')), x[1]['matches']),
        reverse=True
    ))

    return sorted_stats