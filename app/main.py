import os
os.environ["U2NET_HOME"] = "/app/.u2net"

from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.image_service import process_image
from app.services.image_service_sem import process_image_sem
from app.services.image_service_pro import process_image_pro
from app.services.image_service_external_pro import process_image_external_pro
from fastapi import Request
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from app.core.rate_limit import limiter  # ✅ importar desde el nuevo archivo
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

app = FastAPI()

# 👇 Agrega esto para permitir CORS (acceso desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["*"] si estás en desarrollo
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar SlowAPI middleware y handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    print(f"📥 Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"🔥 Uncaught error: {e}")
        raise


@app.get("/test")
@limiter.limit("5/minute") # ✅ Aplicar límite de 5 requests por minuto
async def test(request: Request):
    print("Origin: ", request.headers.get("origin"))
    print("IP: ", request.client.host if request.client else "No client")
    return {"message": "Hello World"}

from fastapi.responses import StreamingResponse
from io import BytesIO


@app.post("/transform")
@limiter.limit("5/minute")
async def transform_image(request: Request, file: UploadFile = File(...)):
    print("📥 Recibido archivo:", file.filename)
    print("📂 Content-Type:", file.content_type)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")

    try:
        result = await process_image(file)
    except Exception as e:
        print("❌ Error en process_image:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor en process_image.")

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png",
        }
    )

@app.post("/transform_sem")
@limiter.limit("5/minute")
async def transform_image_sem(request: Request, file: UploadFile = File(...)):
    print("📥 Recibido archivo:", file.filename)
    print("📂 Content-Type:", file.content_type)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")

    try:
        result = await process_image_sem(file)
    except Exception as e:
        print("❌ Error en process_image_sem:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor en process_image_sem.")

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png",
        }
    )

@app.post("/transform_pro")
@limiter.limit("5/minute")
async def transform_image_pro(request: Request, file: UploadFile = File(...)):
    print("📥 Recibido archivo:", file.filename)
    print("📂 Content-Type:", file.content_type)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")

    try:
        result = await process_image_pro(file)
    except Exception as e:
        print("❌ Error en process_image_pro:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor en process_image_pro.")

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png",
        }
    )





@app.post("/transform_external_pro")
@limiter.limit("5/minute")
async def transform_image_external_pro(request: Request, file: UploadFile = File(...)):
    print("📥 Recibido archivo:", file.filename)
    print("📂 Content-Type:", file.content_type)

    try:
        # Llamar función síncrona correctamente en un hilo
        result_bytes = await asyncio.to_thread(process_image_external_pro, file)
    except Exception as e:
        print("❌ Error en process_image_external_pro:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor en process_image_external_pro.")
    
    return Response(
        content=result_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png",
        }
    )
