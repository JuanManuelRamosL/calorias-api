from fastapi import APIRouter, UploadFile, File, HTTPException
import ollama
import shutil
import os
from PIL import Image
import pillow_heif

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/")
async def analyze_image(file: UploadFile = File(...)):
    temp_image_path = f"./temp_{file.filename}"
    converted_image_path = temp_image_path

    try:
        # Guardar archivo
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extension = os.path.splitext(temp_image_path)[1].lower()

        if extension in ['.heic', '.heif', '.webp']:
            image = Image.open(temp_image_path)
            converted_image_path = temp_image_path.replace(extension, ".jpg")
            image = image.convert("RGB")
            image.save(converted_image_path, format="JPEG")
        elif extension not in ['.jpg', '.jpeg', '.png']:
            raise HTTPException(status_code=400, detail="Formato no soportado. Usa JPG, PNG, HEIC, HEIF o WEBP.")

        # Enviar a Ollama
        response = ollama.chat(
            model="llava",
            messages=[
                {
                    "role": "user",
                    "content": "Describe esta imagen brevemente en español:",
                    "images": [converted_image_path]
                }
            ]
        )
        description = response['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {e}")
    finally:
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if converted_image_path != temp_image_path and os.path.exists(converted_image_path):
            os.remove(converted_image_path)

    return {"description": description}
