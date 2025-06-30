import os
from diffusers import StableDiffusionPipeline
import torch
from dotenv import load_dotenv
from datetime import datetime


class ImagenIA:
    def __init__(self, modelo_id="runwayml/stable-diffusion-v1-5"):
        # Cargar token desde .env
        load_dotenv()
        token = os.getenv("HUGGINGFACE_TOKEN")

        if not token:
            raise ValueError("❌ No se encontró el token de Hugging Face en el archivo .env")

        # Cargar el modelo
        self.pipe = StableDiffusionPipeline.from_pretrained(
            modelo_id,
            use_auth_token=token,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )

        # Enviar a dispositivo adecuado
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = self.pipe.to(self.device)

        # Crear carpeta de salida si no existe
        self.output_dir = "images"
        os.makedirs(self.output_dir, exist_ok=True)

    def generar_imagen(self, prompt: str, nombre_archivo="imagen_generada.png") -> str:
        print(f"🎨 Generando imagen para el prompt: {prompt}")
        imagen = self.pipe(prompt).images[0]

        ruta_guardado = os.path.join(self.output_dir, nombre_archivo)
        imagen.save(ruta_guardado)

        print(f"✅ Imagen guardada en: {ruta_guardado}")
        return ruta_guardado


# === Uso del modelo ===
if __name__ == "__main__":
    generador = ImagenIA()
    prompt = "A golden dragon flying over an ancient temple, Japanese painting style"
    generador.generar_imagen(prompt)
