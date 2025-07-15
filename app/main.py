from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from app.services.image_service import process_image

app = FastAPI()

@app.post("/transform")
async def transform_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes.")
    result = await process_image(file)
    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=processed.png"
        }
    )