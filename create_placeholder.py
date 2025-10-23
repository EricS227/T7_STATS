"""
script simples pra criar imagens de placeholder pros personagens do Tekken 7
roda isso se você ainda não tem os renders dos personagens

Como usar:
    python create_placeholder.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder(character_name, output_path):
    """cria uma imagem simples de placeholder pra um personagem"""

    # cria a imagem
    size = (512, 512)
    img = Image.new('RGBA', size, (26, 26, 26, 255))  # fundo escuro
    draw = ImageDraw.Draw(img)

    # desenha círculos tipo gradiente
    for i in range(5):
        radius = 250 - i * 40
        color = (255, 60, 40, 50 - i * 8)
        draw.ellipse([
            (256 - radius, 256 - radius),
            (256 + radius, 256 + radius)
        ], fill=color)

    # pega a primeira letra
    initial = character_name[0].upper()

    # tenta carregar a fonte, se não rolar usa a padrão
    try:
        font = ImageFont.truetype("arial.ttf", 200)
    except:
        font = ImageFont.load_default()

    # desenha a inicial do personagem
    text_bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2 - 20

    # desenha o texto com contorno
    outline_color = (255, 60, 40, 255)
    for offset in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((text_x + offset[0], text_y + offset[1]), initial,
                 font=font, fill=outline_color)

    draw.text((text_x, text_y), initial, font=font, fill=(255, 255, 255, 255))

    # desenha o nome do personagem embaixo
    try:
        name_font = ImageFont.truetype("arial.ttf", 32)
    except:
        name_font = ImageFont.load_default()

    name_bbox = draw.textbbox((0, 0), character_name, font=name_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (size[0] - name_width) // 2

    draw.text((name_x, 420), character_name, font=name_font, fill=(255, 167, 38, 255))

    # salva a imagem
    img.save(output_path, 'PNG')
    print(f"✓ Criado: {output_path}")


def main():
    """cria imagens de placeholder pra todos os personagens"""

    from utils import TEKKEN_CHARS

    # cria o diretório se não existir
    output_dir = "static/renders"
    os.makedirs(output_dir, exist_ok=True)

    print("Criando imagens de placeholder pros personagens...")
    print(f"Diretório de saída: {output_dir}")
    print()

    # cria placeholders pra todos os personagens
    for char in TEKKEN_CHARS:
        # converte o nome do personagem pro nome do arquivo
        filename = char.lower().replace(' ', '_').replace('-', '_') + '.png'
        output_path = os.path.join(output_dir, filename)

        # pula se o arquivo já existir
        if os.path.exists(output_path):
            print(f" Pulado: {filename} (já existe)")
            continue

        create_placeholder(char, output_path)

    # cria default.png
    default_path = os.path.join(output_dir, 'default.png')
    if not os.path.exists(default_path):
        create_placeholder('?', default_path)
        print()
        print(f"✓ Imagem padrão de fallback criada")

    print()
    print("=" * 50)
    print("✅ Pronto! Imagens de placeholder criadas.")
    print(f"📁 Localização: {os.path.abspath(output_dir)}")
    print()
    print("💡 Dica: Substitua esses placeholders com renders reais")
    print("   dos personagens pra ficar mais bonito!")
    print()
    print("📖 Veja CHARACTER_IMAGES_GUIDE.md pra detalhes sobre")
    print("   como adicionar renders reais dos personagens.")


if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("❌ Erro: PIL (Pillow) não instalado.")
        print()
        print("Instala com:")
        print("  pip install Pillow")
        print()
        print("Ou roda o app sem gerar placeholders.")
        print("O app funciona de boa só com texto.")
