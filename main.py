""" from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ollama
import shutil
import os
from PIL import Image
import pillow_heif

# Crear la aplicación FastAPI
app = FastAPI()

# Habilitar CORS
origins = [
    "http://localhost:8081",  # Agrega la URL de tu front-end React Native
    "http://127.0.0.1:8081",  # O también localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir solicitudes de estas direcciones
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

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

    return {"description": description} """
#ollama pull llava
#pip install ollama
#uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, users, meals
from database import Base, engine

#Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["http://localhost:8081", "http://127.0.0.1:8081"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(analyze.router)
app.include_router(users.router)
app.include_router(meals.router)
