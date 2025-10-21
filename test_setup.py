"""
script de teste rápido pra verificar a configuração do SQLite e do sistema de renders
"""

import os
import sys

# corrige a codificação do console do Windows pra emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def test_database():
    """testa a funcionalidade do banco de dados"""
    print("=" * 60)
    print("TESTANDO BANCO DE DADOS")
    print("=" * 60)

    try:
        from database import get_all_matches, get_all_players, init_db

        # verifica se o banco existe
        db_path = 'data/tekken_stats.db'
        if not os.path.exists(db_path):
            print("ERRO: Arquivo do banco não encontrado")
            print(f"   Esperado: {db_path}")
            return False

        print(f"OK: Arquivo do banco existe: {db_path}")

        # tenta pegar as partidas
        matches = get_all_matches()
        print(f"OK: Carregou {len(matches)} partidas com sucesso")

        # tenta pegar os jogadores
        players = get_all_players()
        print(f"OK: Carregou {len(players)} jogadores com sucesso")

        # mostra dados de exemplo
        if matches:
            print("\nDados de exemplo de partida:")
            match = matches[0]
            print(f"   {match['player1_char']} vs {match['player2_char']}")
            print(f"   Vencedor: {match['winner_char']}")

        return True

    except Exception as e:
        print(f"ERRO: Teste do banco falhou: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_renders():
    """testa o sistema de renders"""
    print("\n" + "=" * 60)
    print("TESTANDO SISTEMA DE RENDERS")
    print("=" * 60)

    # verifica se o diretório de renders existe
    renders_dir = 'static/renders'
    if not os.path.exists(renders_dir):
        print(f"ERRO: Diretório de renders não encontrado: {renders_dir}")
        return False

    print(f"OK: Diretório de renders existe: {renders_dir}")

    # verifica se tem default.png
    default_path = os.path.join(renders_dir, 'default.png')
    if os.path.exists(default_path):
        print(f"OK: Imagem padrão encontrada: {default_path}")
    else:
        print(f"AVISO: Imagem padrão não encontrada (roda create_default_image.py)")

    # lista as imagens de personagens existentes
    images = [f for f in os.listdir(renders_dir)
              if f.endswith(('.png', '.jpg', '.jpeg')) and f != 'default.png']

    if images:
        print(f"OK: Encontrou {len(images)} imagens de personagens:")
        for img in images[:5]:  # mostra as primeiras 5
            print(f"   - {img}")
        if len(images) > 5:
            print(f"   ... e mais {len(images) - 5}")
    else:
        print("AVISO: Nenhuma imagem de personagem encontrada")
        print("   Adiciona imagens no diretório static/renders/")

    # testa a geração de placeholder
    try:
        from PIL import Image
        print("OK: Pillow instalado - geração automática de placeholder disponível")
    except ImportError:
        print("AVISO: Pillow não instalado - placeholders automáticos desabilitados")
        print("   Instala com: pip install Pillow")

    return True


def test_flask_app():
    """testa se o app Flask pode ser importado"""
    print("\n" + "=" * 60)
    print("TESTANDO APP FLASK")
    print("=" * 60)

    try:
        import tekkenapp
        print("OK: App Flask importado com sucesso")

        # verifica se a instância do Flask existe
        if hasattr(tekkenapp, 'app'):
            print("OK: Instância do app Flask criada")
        else:
            print("ERRO: Instância do app Flask não encontrada")
            return False

        return True

    except Exception as e:
        print(f"ERRO: Teste do app Flask falhou: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """roda todos os testes"""
    print("\nTEKKEN STATS - VERIFICAÇÃO DE CONFIGURAÇÃO\n")

    results = {
        'Banco de Dados': test_database(),
        'Renders': test_renders(),
        'App Flask': test_flask_app()
    }

    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASSOU" if passed else "FALHOU"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("TODOS OS TESTES PASSARAM!")
        print("\nSua configuração tá completa! Pra iniciar o app:")
        print("  python tekkenapp.py")
        print("\nDepois acessa: http://127.0.0.1:5000")
    else:
        print("ALGUNS TESTES FALHARAM")
        print("\nPor favor corrige os problemas acima antes de rodar o app.")

    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
