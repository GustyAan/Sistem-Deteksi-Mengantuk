"""
Script untuk membuat placeholder logo
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_logo():
    # Buat image 200x200
    img = Image.new('RGB', (200, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # Gambar border
    d.rectangle([0, 0, 199, 199], outline='blue', width=3)
    
    # Tambahkan teks PENS
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    d.text((50, 80), "PENS", fill='blue', font=font)
    d.text((30, 120), "LOGO", fill='darkblue', font=font)
    
    # Simpan
    os.makedirs("app/resources", exist_ok=True)
    img.save("app/resources/logo_pens.png")
    print("Placeholder logo created at app/resources/logo_pens.png")

if __name__ == "__main__":
    create_placeholder_logo()