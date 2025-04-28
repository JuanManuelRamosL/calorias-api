import ollama

# Ruta de la imagen que deseas analizar
image_path = './tu_imagen.jpg'  # Reemplaza con la ruta de tu imagen

# Crear una conversación con el modelo LLaVA
response = ollama.chat(
    model='llava',
    messages=[
        {
            'role': 'user',
            'content': 'Describe esta imagen en español brevemente :',
            'images': ["./images.jpg"]
        }
    ]
)

# Imprimir la respuesta del modelo
print(response['message']['content'])
