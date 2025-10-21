"""
cria uma imagem padrão de placeholder pros personagens sem render
roda uma vez pra criar o arquivo default.png
"""

import os

def create_default_image():
    """cria uma imagem padrão de placeholder"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # cria o diretório de renders
        os.makedirs('static/renders', exist_ok=True)

        # cria a imagem com as cores do tema Tekken
        img = Image.new('RGBA', (200, 200), (30, 30, 40, 255))
        draw = ImageDraw.Draw(img)

        # desenha o círculo de fundo
        draw.ellipse([20, 20, 180, 180], fill=(100, 100, 120, 255))

        # desenha o ponto de interrogação
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()

        # desenha o texto
        text = "?"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (200 - text_width) // 2
        text_y = (200 - text_height) // 2 - 10

        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

        # salva
        output_path = 'static/renders/default.png'
        img.save(output_path, 'PNG')
        print(f"Imagem padrão criada em {output_path}")
        return True

    except ImportError:
        print("PIL/Pillow não instalado. Criando fallback SVG...")

        # cria um SVG simples como alternativa
        svg_content = '''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="80" fill="#64647c"/>
  <text x="100" y="140" font-size="100" text-anchor="middle" fill="white" font-family="Arial">?</text>
</svg>'''

        os.makedirs('static/renders', exist_ok=True)
        with open('static/renders/default.svg', 'w') as f:
            f.write(svg_content)
        print("Imagem default.svg criada (formato SVG)")
        print("Pra suporte PNG, instala o Pillow: pip install Pillow")
        return False

if __name__ == '__main__':
    print("Criando imagem padrão de placeholder...")
    create_default_image()
    print("Pronto!")
