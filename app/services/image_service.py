import os
import httpx
from io import BytesIO
from PIL import Image, ImageFilter, UnidentifiedImageError
from fastapi import HTTPException, UploadFile
from rembg import remove
from typing import cast


timeout = httpx.Timeout(30.0)  # 30 segundos


async def process_image(file: UploadFile, enhance: bool = True) -> bytes:
    try:
        print("📥 Leyendo archivo del cliente...")
        image_bytes = await file.read()
        print(f"🗂️ Tamaño del archivo recibido: {len(image_bytes)} bytes")

        print("🎯 Iniciando eliminación de fondo con rembg...")
        result_bytes = cast(bytes, remove(image_bytes))
        print(f"✅ Fondo removido - tamaño: {len(result_bytes)} bytes")

        try:
            img = Image.open(BytesIO(result_bytes)).convert("RGBA")
        except UnidentifiedImageError as e:
            print("❌ Error al abrir imagen con Pillow:", e)
            raise HTTPException(status_code=422, detail="La imagen no se pudo decodificar.")

        print(f"🖼️ Dimensiones: {img.size}")

        # Fondo negro si tiene transparencia
        bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
        combined = Image.alpha_composite(bg, img)

        # Escala de grises
        grayscale = combined.convert("L").convert("RGBA")

        if enhance:
            print("✨ Mejorando imagen (resample y sharpen)...")
            new_size = (grayscale.width * 2, grayscale.height * 2)
            grayscale = grayscale.resize(new_size, resample=Image.LANCZOS)
            grayscale = grayscale.filter(ImageFilter.SHARPEN)

        print("💾 Guardando imagen en memoria...")
        output = BytesIO()
        grayscale.save(output, format="PNG", optimize=True)
        output.seek(0)

        print("🚀 Imagen procesada correctamente.")
        return output.read()

    except Exception as e:
        print(f"❌ Error en process_image: {e}")
        raise HTTPException(status_code=500, detail="Error procesando la imagen en el servidor.")
