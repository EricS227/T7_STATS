#!/usr/bin/env python3
"""
script de demonstração mostrando como pegar dados só dos personagens que foram usados
roda isso pra ver exemplos de como filtrar dados de personagens
"""

import json
from utils import get_used_characters, get_used_character_stats, calculate_stats

def load_matches():
    """carrega partidas do arquivo JSON"""
    try:
        with open('data/matches.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("AVISO: Nenhuma partida encontrada. Adiciona algumas partidas primeiro!")
        return []

def demo():
    """demonstra diferentes formas de pegar dados dos personagens usados"""

    print("=" * 60)
    print("DEMO: Pegando Dados dos Personagens Usados ao Longo do Tempo")
    print("=" * 60)
    print()

    matches = load_matches()

    if not matches:
        print("Nenhuma partida encontrada. Por favor adiciona algumas partidas primeiro!")
        return

    print(f"Total de partidas no banco: {len(matches)}")
    print()

    # método 1: pega lista de nomes dos personagens usados
    print("=" * 60)
    print("MÉTODO 1: Pegar Lista de Nomes dos Personagens Usados")
    print("=" * 60)

    used_chars = get_used_characters(matches)
    print(f"Total de personagens usados: {len(used_chars)} de 39")
    print(f"Personagens: {', '.join(used_chars)}")
    print()

    # método 2: pega estatísticas só dos personagens usados (ordenado por taxa de vitória)
    print("=" * 60)
    print("MÉTODO 2: Estatísticas dos Personagens Usados (Ordenado por Taxa de Vitória)")
    print("=" * 60)

    used_stats = get_used_character_stats(matches)

    print(f"{'Personagem':<20} {'Vitórias':<8} {'Partidas':<10} {'Taxa Vitória':<10}")
    print("-" * 60)

    for char, stats in used_stats.items():
        print(f"{char:<20} {stats['wins']:<8} {stats['matches']:<10} {stats['winRate']:<10}")

    print()

    # método 3: compara pegando TODAS as estatísticas vs só dos usados
    print("=" * 60)
    print("MÉTODO 3: Comparação - Todas as Stats vs Stats dos Usados")
    print("=" * 60)

    all_stats = calculate_stats(matches)

    unused_count = sum(1 for stats in all_stats.values() if stats['matches'] == 0)
    used_count = sum(1 for stats in all_stats.values() if stats['matches'] > 0)

    print(f"Todos os personagens no banco: 39")
    print(f"  └─ Personagens usados: {used_count}")
    print(f"  └─ Personagens não usados: {unused_count}")
    print()
    print(f"Usando get_used_character_stats(), você filtra {unused_count} personagens não usados!")
    print()

    # método 4: mostra top 5 personagens por taxa de vitória
    print("=" * 60)
    print("MÉTODO 4: Top 5 Personagens por Taxa de Vitória")
    print("=" * 60)

    top_5 = list(used_stats.items())[:5]

    for i, (char, stats) in enumerate(top_5, 1):
        print(f"#{i}. {char:<15} - {stats['winRate']} ({stats['wins']}/{stats['matches']})")

    print()

    # método 5: mostra personagens com pelo menos 5 partidas
    print("=" * 60)
    print("MÉTODO 5: Personagens com Pelo Menos 5 Partidas")
    print("=" * 60)

    frequent_chars = {
        char: stats
        for char, stats in used_stats.items()
        if stats['matches'] >= 5
    }

    if frequent_chars:
        for char, stats in frequent_chars.items():
            print(f"  • {char}: {stats['matches']} partidas, {stats['winRate']} taxa de vitória")
    else:
        print("  Nenhum personagem tem 5+ partidas ainda.")

    print()

    # método 6: mostra personagens com > 60% de taxa de vitória (mínimo 3 partidas)
    print("=" * 60)
    print("MÉTODO 6: Personagens Fortes (>60% Taxa de Vitória, 3+ Partidas)")
    print("=" * 60)

    strong_chars = {
        char: stats
        for char, stats in used_stats.items()
        if float(stats['winRate'].rstrip('%')) > 60.0 and stats['matches'] >= 3
    }

    if strong_chars:
        for char, stats in strong_chars.items():
            print(f"  • {char}: {stats['winRate']} ({stats['wins']}/{stats['matches']})")
    else:
        print("  Nenhum personagem atende os critérios ainda.")

    print()
    print("=" * 60)
    print("Demo Completo!")
    print("=" * 60)


if __name__ == '__main__':
    demo()
