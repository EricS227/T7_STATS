"""
SQLite database module for Tekken Stats Tracker
Handles all database operations for matches and players
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os

DATABASE_PATH = 'data/tekken_stats.db'

def get_db_connection():
    """Create and return a database connection"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create matches table
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

    # Create players table
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

    # Create index for faster queries
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

# ==================== MATCH OPERATIONS ====================

def add_match(match_data: Dict) -> int:
    """
    Add a new match to the database

    Args:
        match_data: Dictionary with keys: player1, player2, winner,
                   player1_char, player2_char, winner_char

    Returns:
        The ID of the newly created match
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generate timestamp if not provided
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
    """
    Retrieve all matches from the database

    Returns:
        List of match dictionaries
    """
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
    """Get a specific match by ID"""
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
    """Delete a match by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM matches WHERE id = ?', (match_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted

def clear_all_matches():
    """Delete all matches from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM matches')

    conn.commit()
    conn.close()

# ==================== PLAYER OPERATIONS ====================

def add_player(player_data: Dict) -> str:
    """
    Add a new player to the database

    Args:
        player_data: Dictionary with keys: id, name, main_char, rank, region

    Returns:
        The ID of the newly created player
    """
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
    """
    Retrieve all players from the database

    Returns:
        List of player dictionaries
    """
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
    """Get a specific player by ID"""
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
    """Update a player's information"""
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
    """Delete a player by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted

# ==================== STATISTICS QUERIES ====================

def get_character_stats() -> List[Tuple[str, int, int]]:
    """
    Get aggregated statistics for each character

    Returns:
        List of tuples: (character_name, total_matches, total_wins)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all characters that have played
    cursor.execute('''
        SELECT DISTINCT player1_char as character FROM matches
        UNION
        SELECT DISTINCT player2_char as character FROM matches
    ''')

    characters = [row['character'] for row in cursor.fetchall()]

    stats = []
    for char in characters:
        # Count matches
        cursor.execute('''
            SELECT COUNT(*) as count FROM matches
            WHERE player1_char = ? OR player2_char = ?
        ''', (char, char))
        matches = cursor.fetchone()['count']

        # Count wins
        cursor.execute('''
            SELECT COUNT(*) as count FROM matches
            WHERE winner_char = ?
        ''', (char,))
        wins = cursor.fetchone()['count']

        stats.append((char, matches, wins))

    conn.close()
    return stats

def get_matchup_stats(char1: str, char2: str) -> Dict:
    """
    Get head-to-head statistics between two characters

    Returns:
        Dictionary with char1_wins, char2_wins, total_matches
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Count wins for char1
    cursor.execute('''
        SELECT COUNT(*) as count FROM matches
        WHERE ((player1_char = ? AND player2_char = ?) OR
               (player1_char = ? AND player2_char = ?))
          AND winner_char = ?
    ''', (char1, char2, char2, char1, char1))
    char1_wins = cursor.fetchone()['count']

    # Count wins for char2
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

# ==================== MIGRATION FUNCTIONS ====================

def import_from_json(matches_file: str = 'data/matches.json',
                     players_file: str = 'data/players.json'):
    """
    Import data from existing JSON files into SQLite database

    Args:
        matches_file: Path to matches.json
        players_file: Path to players.json
    """
    # Initialize database first
    init_db()

    # Import matches
    if os.path.exists(matches_file):
        with open(matches_file, 'r') as f:
            matches = json.load(f)

        print(f"Importing {len(matches)} matches...")
        imported = 0
        import time
        for i, match in enumerate(matches):
            try:
                # Handle both old and new JSON formats
                # Old format: player1, player2, winner (no _char suffix)
                # New format: player1, player2, winner + player1_char, player2_char, winner_char

                # Generate unique ID if missing or duplicate (id=0)
                match_id = match.get('id', 0)
                if match_id == 0 or match_id is None:
                    match_id = int(time.time() * 1000) + i  # Ensure unique IDs

                match_data = {
                    'id': match_id,
                    'timestamp': match.get('timestamp', datetime.now().isoformat()),
                    'player1': match.get('player1', ''),
                    'player2': match.get('player2', ''),
                    'winner': match.get('winner', ''),
                    # Use _char fields if present, otherwise use base fields (for backwards compatibility)
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

    # Import players
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
    # Initialize database when run directly
    print("Initializing database...")
    init_db()
    print("Database setup complete!")

    # Optionally import from JSON
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--import':
        print("\nImporting data from JSON files...")
        import_from_json()
