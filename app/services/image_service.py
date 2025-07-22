import httpx
from io import BytesIO
from PIL import Image, ImageFilter
from fastapi import HTTPException, UploadFile
import os
from rembg import remove
from typing import cast




timeout = httpx.Timeout(30.0)  # 30 segundos


async def process_image(file: UploadFile, enhance: bool = True) -> bytes:
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

    # 🔍 6. Mejora de calidad (opcional)
    if enhance:
        # Escalar al 2x usando LANCZOS (calidad)
        new_size = (grayscale.width * 2, grayscale.height * 2)
        grayscale = grayscale.resize(new_size, resample=Image.LANCZOS)

        # Aplicar filtro de nitidez
        grayscale = grayscale.filter(ImageFilter.SHARPEN)
    
    # 5. Guardar en memoria
    output = BytesIO()
    grayscale.save(output, format="PNG", optimize=True)
    output.seek(0)

    return output.read()