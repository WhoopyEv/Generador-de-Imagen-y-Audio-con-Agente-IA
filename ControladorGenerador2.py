""""
 ESTA ES UNA VERSIÓN ANTERIOR DEL CÓDIGO, DONDE 
 NO INCORPORABA AGENTES NI TOOLS DE LANGCHAIN.
"""

import json
import re
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from GeneradorImagenes import ImagenIA
from GeneradorAudio import GeneradorAudio


class ControladorGeneradorIA:
    def __init__(self, url_llm="http://localhost:1234/v1", modelo_llm="local-model"):
        self.llm = ChatOpenAI(
            model_name=modelo_llm,
            openai_api_base=url_llm,
            openai_api_key="not-needed"
        )
        self.generador_img = ImagenIA()
        self.generador_audio = GeneradorAudio(voz="es-CO-SalomeNeural")

    def clasificar_modo(self, idea: str) -> str:
        mensaje = (
            f"""
            Un usuario ha dado el siguiente texto para generar contenido con IA multimodal.

            Clasifica la intención respondiendo solo con una de estas tres palabras exactas:
            - "imagen" si solo quiere una imagen.
            - "audio" si solo quiere escuchar una narración.
            - "ambos" si desea tanto imagen como narración en audio.

            No expliques tu respuesta. Solo escribe una palabra: imagen, audio o ambos.

            Texto del usuario:
            {idea}
           """
        )
        respuesta = self.llm([HumanMessage(content=mensaje)]).content.strip().lower()
        if respuesta not in ["audio", "imagen", "ambos"]:
            print(f"⚠️ Respuesta inesperada: {respuesta}. Se usará 'ambos' por defecto.")
            return "ambos"
        return respuesta

    def generar_prompts(self, idea: str) -> tuple:
        mensaje = f"""
Convierte esta idea en dos salidas separadas en formato JSON, así:

{{
  "texto_narrativo": "...",
  "prompt_imagen": "..."
}}

- "texto_narrativo": debe ser un pequeño relato o descripción en español, amigable para leer en voz alta.
- "prompt_imagen": debe ser un prompt visual en inglés, estilo Stable Diffusion.

Texto: {idea}
"""
        respuesta = self.llm([HumanMessage(content=mensaje)]).content
        print("🧾 Respuesta cruda del modelo:\n", respuesta)  # Útil para debug

        # Extraer primer bloque JSON válido con expresión regular
        coincidencias = re.findall(r'\{[^{}]*"texto_narrativo"[^{}]*"prompt_imagen"[^{}]*\}', respuesta, re.DOTALL)

        if not coincidencias:
            raise ValueError("❌ No se encontró un bloque JSON válido en la respuesta del modelo")

        try:
            datos = json.loads(coincidencias[0])
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Error al parsear JSON: {e}\nTexto recibido:\n{coincidencias[0]}")

        return datos["texto_narrativo"], datos["prompt_imagen"]

    def ejecutar(self, idea: str):
        modo = self.clasificar_modo(idea)
        texto, prompt = self.generar_prompts(idea)

        print(f"\n🗣️ Texto narrativo:\n{texto}\n")
        print(f"🖼️ Prompt visual:\n{prompt}\n")

        if modo in ["imagen", "ambos"]:
            self.generador_img.generar_imagen(prompt)

        if modo in ["audio", "ambos"]:
            self.generador_audio.ejecutar(texto, "voz_ia.mp3")

    def ejecutar_con_retorno(self, idea: str) -> tuple:
        modo = self.clasificar_modo(idea)
        texto, prompt = self.generar_prompts(idea)

        ruta_img = ruta_audio = None

        if modo in ["imagen", "ambos"]:
            ruta_img = self.generador_img.generar_imagen(prompt)

        if modo in ["audio", "ambos"]:
            ruta_audio = self.generador_audio.ejecutar(texto)

        return modo, texto, prompt, ruta_img, ruta_audio


if __name__ == "__main__":
    controlador = ControladorGeneradorIA()
    idea = input("🧠 Escribe tu idea o descripción: ")
    controlador.ejecutar(idea)