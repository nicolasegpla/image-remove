from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError, ImageOps
from io import BytesIO
import math
import requests
import os

# Ideal: manejar desde variable de entorno
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

def resize_image_to_025mp(image: Image.Image):
    """Reduce imagen a 0.25 megapíxeles manteniendo aspecto."""
    original_size = image.size
    aspect_ratio = original_size[0] / original_size[1]
    target_pixels = 250_000

    new_width = int(math.sqrt(target_pixels * aspect_ratio))
    new_height = int(new_width / aspect_ratio)

    resized = image.resize((new_width, new_height), Image.LANCZOS)
    return resized, original_size

def restore_size_and_apply_effects(image_bytes: bytes, target_size: tuple[int, int]) -> bytes:
    """Restaura tamaño original, aplica fondo negro y convierte a escala de grises."""
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    # Restaurar tamaño original
    image = image.resize(target_size, Image.LANCZOS)

    # Crear fondo negro y pegar imagen
    black_bg = Image.new("RGBA", image.size, (0, 0, 0, 255))
    black_bg.paste(image, mask=image.split()[3])  # Usar canal alfa como máscara

    # Convertir a escala de grises
    final_image = ImageOps.grayscale(black_bg.convert("RGB"))

    # Convertir a bytes
    output = BytesIO()
    final_image.save(output, format="PNG")
    return output.getvalue()

def process_image_external_pro(file: UploadFile) -> bytes:
    try:
        image = Image.open(file.file)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Archivo inválido. No es una imagen reconocida.")

    resized_image, original_size = resize_image_to_025mp(image)

    # Convertir a bytes para enviar
    buffer = BytesIO()
    resized_image.save(buffer, format="PNG")
    buffer.seek(0)

    # Enviar a remove.bg
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': ('image.png', buffer, 'image/png')},
        data={'size': 'preview'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY},
    )

    if response.status_code != 200:
        print("❌ Remove.bg error:", response.status_code, response.text)
        raise HTTPException(status_code=502, detail="Error al procesar la imagen con Remove.bg")

    # Restaura tamaño, aplica fondo negro y escala de grises
    return restore_size_and_apply_effects(response.content, original_size)
