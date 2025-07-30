import httpx
from io import BytesIO
from PIL import Image, ImageFilter, UnidentifiedImageError
from fastapi import HTTPException, UploadFile
from rembg import remove, new_session
from typing import cast

# Crear la sesión con el modelo más preciso
session = new_session(model_name="isnet-general-use")
timeout = httpx.Timeout(30.0)

MAX_SIZE = 2048

def resize_input(image: Image.Image) -> Image.Image:
    if max(image.size) > MAX_SIZE:
        image.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    return image

def preprocess_blur(image: Image.Image) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(radius=1))

def refine_alpha(image: Image.Image, low=30, high=200) -> Image.Image:
    r, g, b, a = image.split()
    a = a.point(lambda p: 0 if p < low else 255 if p > high else int(255 * (p - low) / (high - low)))
    return Image.merge("RGBA", (r, g, b, a))

def apply_black_background(image: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", image.size, (0, 0, 0, 255))
    return Image.alpha_composite(bg, image)

async def process_image_pro(file: UploadFile, enhance: bool = True) -> bytes:
    try:
        print("📥 Leyendo archivo del cliente...")
        image_bytes = await file.read()
        print(f"🗂️ Tamaño del archivo recibido: {len(image_bytes)} bytes")

        input_image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        input_image = resize_input(input_image)
        input_image = preprocess_blur(input_image)

        print("🎯 Ejecutando rembg con modelo isnet...")
        input_bytes = BytesIO()
        input_image.save(input_bytes, format="PNG")  # Convertimos a PNG válido
        input_bytes = input_bytes.getvalue()

        result_bytes = cast(bytes, remove(input_bytes, session=session))

        try:
            img = Image.open(BytesIO(result_bytes)).convert("RGBA")
        except UnidentifiedImageError as e:
            print("❌ Error al abrir imagen con Pillow:", e)
            raise HTTPException(status_code=422, detail="La imagen no se pudo decodificar.")

        img = refine_alpha(img)
        img = apply_black_background(img)
        img = img.convert("L").convert("RGBA")  # Escala de grises con canal alpha

        if enhance:
            new_size = (img.width * 2, img.height * 2)
            img = img.resize(new_size, resample=Image.LANCZOS)
            img = img.filter(ImageFilter.SHARPEN)

        output_buffer = BytesIO()
        img.save(output_buffer, format="PNG")
        return output_buffer.getvalue()

    except HTTPException as e:
        print(f"❌ Error en process_image_pro: {e.status_code}: {e.detail}")
        raise e
    except Exception as e:
        print("❌ Error general:", e)
        raise HTTPException(status_code=500, detail="Error interno al procesar la imagen.")
