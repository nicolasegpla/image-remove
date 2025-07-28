from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.image_service import process_image
from fastapi import Request

from fastapi.middleware.cors import CORSMiddleware
from app.core.rate_limit import limiter  # ✅ importar desde el nuevo archivo
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

app = FastAPI()

# 👇 Agrega esto para permitir CORS (acceso desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5174", "http://localhost:8000", "http://localhost:4174", "http://localhost:5173", "https://buildtix.site"],  # o ["*"] si estás en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar SlowAPI middleware y handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.get("/test")
@limiter.limit("5/minute") # ✅ Aplicar límite de 5 requests por minuto
async def test(request: Request):
    print("Origin: ", request.headers.get("origin"))
    print("IP: ", request.client.host if request.client else "No client")
    return {"message": "Hello World"}

@app.post("/transform")
@limiter.limit("5/minute") # ✅ Aplicar límite de 5 requests por minuto
async def transform_image(request: Request, file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")
    result = await process_image(file)

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png",
            "Access-Control-Allow-Origin": "http://localhost:5174",  # 👈 Esto es clave
            "Access-Control-Allow-Credentials": "true"
        }
    )