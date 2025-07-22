from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.image_service import process_image
from fastapi import Request

app = FastAPI()

# 👇 Agrega esto para permitir CORS (acceso desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5174", "http://localhost:8000", "http://localhost:4174", "*"],  # o ["*"] si estás en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test(request: Request):
    print("Origin: ", request.headers.get("origin"))
    print("IP: ", request.client.host if request.client else "No client")
    return {"message": "Hello World"}

@app.post("/transform")
async def transform_image(file: UploadFile = File(...)):
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