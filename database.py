"""
módulo SQLite pro Tekken Stats Tracker
cuida de todas as operações de banco de dados pra partidas e jogadores
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os

DATABASE_PATH = 'data/tekken_stats.db'

def get_db_connection():
    """cria e retorna uma conexão com o banco"""
    # garante que o diretório existe
    os.makedirs('data', exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # retorna as linhas como dicionários
    return conn

def init_db():
    """inicializa o banco com as tabelas necessárias"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # cria tabela de partidas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            player1 TEXT NOT NULL,
            player2 TEXT NOT NULL,
            winner TEXT NOT NULL,
            player1_char TEXT NOT NULL,
            player2_char TEXT NOT NULL,
            winner_char TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # cria tabela de jogadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            main_char TEXT,
            rank TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # cria índices pra consultas mais rápidas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_matches_timestamp
        ON matches(timestamp)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_matches_characters
        ON matches(player1_char, player2_char)
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")

# ==================== OPERAÇÕES DE PARTIDA ====================

def add_match(match_data: Dict) -> int:
    """adiciona uma nova partida no banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # gera timestamp se não tiver
    timestamp = match_data.get('timestamp', datetime.now().isoformat())
    match_id = match_data.get('id', int(datetime.now().timestamp() * 1000))

    cursor.execute('''
        INSERT INTO matches (id, timestamp, player1, player2, winner,
                           player1_char, player2_char, winner_char)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        match_id,
        timestamp,
        match_data['player1'],
        match_data['player2'],
        match_data['winner'],
        match_data['player1_char'],
        match_data['player2_char'],
        match_data['winner_char']
    ))

    conn.commit()
    last_id = cursor.lastrowid
    conn.close()

    return last_id

def get_all_matches() -> List[Dict]:
    """pega todas as partidas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, timestamp, player1, player2, winner,
               player1_char, player2_char, winner_char
        FROM matches
        ORDER BY timestamp DESC
    ''')

    matches = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return matches

def get_match_by_id(match_id: int) -> Optional[Dict]:
    """pega uma partida específica pelo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, timestamp, player1, player2, winner,
               player1_char, player2_char, winner_char
        FROM matches
        WHERE id = ?
    ''', (match_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def delete_match(match_id: int) -> bool:
    """deleta uma partida pelo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM matches WHERE id = ?', (match_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted

def clear_all_matches():
    """apaga todas as partidas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM matches')

    conn.commit()
    conn.close()

# ==================== OPERAÇÕES DE JOGADOR ====================

def add_player(player_data: Dict) -> str:
    """adiciona um novo jogador no banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO players (id, name, main_char, rank, region)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        player_data['id'],
        player_data['name'],
        player_data.get('main_char', ''),
        player_data.get('rank', ''),
        player_data.get('region', '')
    ))

    conn.commit()
    player_id = player_data['id']
    conn.close()

    return player_id

def get_all_players() -> List[Dict]:
    """pega todos os jogadores do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, main_char, rank, region
        FROM players
        ORDER BY name
    ''')

    players = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return players

def get_player_by_id(player_id: str) -> Optional[Dict]:
    """pega um jogador específico pelo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, main_char, rank, region
        FROM players
        WHERE id = ?
    ''', (player_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None

def update_player(player_id: str, player_data: Dict) -> bool:
    """atualiza as informações de um jogador"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE players
        SET name = ?, main_char = ?, rank = ?, region = ?
        WHERE id = ?
    ''', (
        player_data['name'],
        player_data.get('main_char', ''),
        player_data.get('rank', ''),
        player_data.get('region', ''),
        player_id
    ))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return updated

def delete_player(player_id: str) -> bool:
    """deleta um jogador pelo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted

# ==================== CONSULTAS DE ESTATÍSTICAS ====================

def get_character_stats() -> List[Tuple[str, int, int]]:
    """pega estatísticas agregadas de cada personagem"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # pega todos os personagens que jogaram
    cursor.execute('''
        SELECT DISTINCT player1_char as character FROM matches
        UNION
        SELECT DISTINCT player2_char as character FROM matches
    ''')

    characters = [row['character'] for row in cursor.fetchall()]

    stats = []
    for char in characters:
        # conta as partidas
        cursor.execute('''
            SELECT COUNT(*) as count FROM matches
            WHERE player1_char = ? OR player2_char = ?
        ''', (char, char))
        matches = cursor.fetchone()['count']

        # conta as vitórias
        cursor.execute('''
            SELECT COUNT(*) as count FROM matches
            WHERE winner_char = ?
        ''', (char,))
        wins = cursor.fetchone()['count']

        stats.append((char, matches, wins))

    conn.close()
    return stats

def get_matchup_stats(char1: str, char2: str) -> Dict:
    """pega estatísticas de confronto direto entre dois personagens"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # conta vitórias do char1
    cursor.execute('''
        SELECT COUNT(*) as count FROM matches
        WHERE ((player1_char = ? AND player2_char = ?) OR
               (player1_char = ? AND player2_char = ?))
          AND winner_char = ?
    ''', (char1, char2, char2, char1, char1))
    char1_wins = cursor.fetchone()['count']

    # conta vitórias do char2
    cursor.execute('''
        SELECT COUNT(*) as count FROM matches
        WHERE ((player1_char = ? AND player2_char = ?) OR
               (player1_char = ? AND player2_char = ?))
          AND winner_char = ?
    ''', (char1, char2, char2, char1, char2))
    char2_wins = cursor.fetchone()['count']

    conn.close()

    return {
        'char1_wins': char1_wins,
        'char2_wins': char2_wins,
        'total_matches': char1_wins + char2_wins
    }

# ==================== FUNÇÕES DE MIGRAÇÃO ====================

def import_from_json(matches_file: str = 'data/matches.json',
                     players_file: str = 'data/players.json'):
    """importa dados dos arquivos JSON antigos pro banco SQLite"""
    # inicializa o banco primeiro
    init_db()

    # importa partidas
    if os.path.exists(matches_file):
        with open(matches_file, 'r') as f:
            matches = json.load(f)

        print(f"Importing {len(matches)} matches...")
        imported = 0
        import time
        for i, match in enumerate(matches):
            try:
                # lida com formato antigo e novo do JSON
                # formato antigo: player1, player2, winner (sem sufixo _char)
                # formato novo: player1, player2, winner + player1_char, player2_char, winner_char

                # gera ID único se estiver faltando ou duplicado (id=0)
                match_id = match.get('id', 0)
                if match_id == 0 or match_id is None:
                    match_id = int(time.time() * 1000) + i  # garante IDs únicos

                match_data = {
                    'id': match_id,
                    'timestamp': match.get('timestamp', datetime.now().isoformat()),
                    'player1': match.get('player1', ''),
                    'player2': match.get('player2', ''),
                    'winner': match.get('winner', ''),
                    # usa campos _char se existir, senão usa os campos base (pra compatibilidade)
                    'player1_char': match.get('player1_char', match.get('player1', '')),
                    'player2_char': match.get('player2_char', match.get('player2', '')),
                    'winner_char': match.get('winner_char', match.get('winner', ''))
                }

                add_match(match_data)
                imported += 1
            except Exception as e:
                print(f"Error importing match {match.get('id')}: {e}")

        print(f"Successfully imported {imported} matches")
    else:
        print(f"No matches file found at {matches_file}")

    # importa jogadores
    if os.path.exists(players_file):
        with open(players_file, 'r') as f:
            players = json.load(f)

        print(f"Importing {len(players)} players...")
        for player in players:
            try:
                add_player(player)
            except Exception as e:
                print(f"Error importing player {player.get('id')}: {e}")

        print(f"Successfully imported {len(players)} players")
    else:
        print(f"No players file found at {players_file}")

if __name__ == '__main__':
    # inicializa o banco quando rodar direto
    print("Initializing database...")
    init_db()
    print("Database setup complete!")

    # opcionalmente importa do JSON
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--import':
        print("\nImporting data from JSON files...")
        import_from_json()
