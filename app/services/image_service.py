import httpx
from io import BytesIO
from PIL import Image
from fastapi import HTTPException, UploadFile
import os
from rembg import remove
from typing import cast




timeout = httpx.Timeout(30.0)  # 30 segundos


async def process_image(file: UploadFile) -> bytes:
    # Leer imagen original como bytes
    image_bytes = await file.read()

    # Quitar fondo con rembg
    result_bytes = cast(bytes, remove(image_bytes))

    # 2. Cargar imagen sin fondo en formato RGBA
    img = Image.open(BytesIO(result_bytes)).convert("RGBA")

    # 3. Agregar fondo negro (si hay transparencia)
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    combined = Image.alpha_composite(bg, img)

    # 4. Convertir a escala de grises
    grayscale = combined.convert("L").convert("RGBA")
    
    # 5. Guardar en memoria
    output = BytesIO()
    grayscale.save(output, format="PNG", optimize=True)
    output.seek(0)

    return output.read()