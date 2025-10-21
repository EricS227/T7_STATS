#!/usr/bin/env python3
"""
script de teste pra verificar se os renders dos personagens tão funcionando
roda enquanto seu app Flask tá rodando
"""

import requests
import sys

def test_render(character_name):
    """testa se o render de um personagem carrega"""
    url = f"http://127.0.0.1:5000/render/{character_name}"

    print(f"Testando: {character_name}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            size = len(response.content)

            print(f"SUCESSO!")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {content_type}")
            print(f"  Tamanho: {size:,} bytes")

            if 'image' in content_type:
                print(f"  Arquivo de imagem servido corretamente!")
            else:
                print(f"  Aviso: Não é um tipo de imagem")

            return True
        else:
            print(f"FALHOU")
            print(f"  Status: {response.status_code}")
            return False

    except requests.exceptions.ConnectionRefusedError:
        print(f"ERRO: Não consegue conectar ao app Flask")
        print(f"  Certifica que o app tá rodando: python tekkenapp.py")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    print("=" * 60)
    print("Teste de Render de Personagens")
    print("=" * 60)
    print()

    # personagens pra testar
    test_characters = [
        'kazuya',
        'jin',
        'devil_jin',
        'paul',
        'bryan'
    ]

    print("Testando renders dos personagens...")
    print()

    results = {}
    for char in test_characters:
        success = test_render(char)
        results[char] = success
        print()

    # resumo
    print("=" * 60)
    print("Resumo")
    print("=" * 60)

    working = [char for char, success in results.items() if success]
    not_working = [char for char, success in results.items() if not success]

    if working:
        print(f"\nFuncionando ({len(working)}):")
        for char in working:
            print(f"  - {char}")

    if not_working:
        print(f"\nNão Funcionando ({len(not_working)}):")
        for char in not_working:
            print(f"  - {char}")
        print(f"\nPra corrigir: Adiciona imagens em static/renders/ ou static/renders/tekken7/")

    if not working and not working:
        print("\nSem resultados - Certifica que o app Flask tá rodando!")

if __name__ == '__main__':
    try:
        import requests
    except ImportError:
        print("Erro: módulo requests não instalado")
        print("Instala com: pip install requests")
        sys.exit(1)

    main()
