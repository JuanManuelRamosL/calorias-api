from fastapi import FastAPI, UploadFile, File, HTTPException
import ollama
import shutil
import os
from PIL import Image
import pillow_heif

app = FastAPI()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Guardar la imagen temporalmente
    temp_image_path = f"./temp_{file.filename}"

    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convertir a JPG si es necesario
    converted_image_path = temp_image_path
    try:
        extension = os.path.splitext(temp_image_path)[1].lower()

        if extension in ['.heic', '.heif', '.webp']:
            # Si es HEIC/HEIF/WEBP lo abrimos y lo convertimos a JPG
            image = Image.open(temp_image_path)
            converted_image_path = temp_image_path.replace(extension, ".jpg")
            image = image.convert("RGB")  # Muy importante para eliminar transparencias de webp
            image.save(converted_image_path, format="JPEG")
        elif extension not in ['.jpg', '.jpeg', '.png']:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Usa JPG, PNG, HEIC, HEIF o WEBP.")

        # Enviar la imagen ya procesada al modelo
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
        # Borramos los archivos temporales
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if converted_image_path != temp_image_path and os.path.exists(converted_image_path):
            os.remove(converted_image_path)

    return {"description": description}

#ollama pull llava
#pip install ollama
