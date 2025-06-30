import json
import re
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.schema import HumanMessage
from GeneradorImagenes import ImagenIA
from GeneradorAudio import GeneradorAudio


class AnalizadorContenido:
    def __init__(self, llm):
        self.llm = llm

    def clasificar_modo(self, idea: str) -> str:
        prompt = f"""
Un usuario ha proporcionado el siguiente texto para generar contenido con IA.

Clasifica su intención respondiendo solo con UNA de estas tres palabras exactas:
- "imagen" si desea una imagen.
- "audio" si desea una narración.
- "ambos" si desea ambos.

No expliques. Solo responde: imagen, audio o ambos.

Texto del usuario:
{idea}
"""
        respuesta = self.llm([HumanMessage(content=prompt)]).content.strip().lower()
        return respuesta if respuesta in ["imagen", "audio", "ambos"] else "ambos"

    def generar_prompts(self, idea: str) -> tuple:
        prompt = f"""
Convierte esta idea en formato JSON con dos campos:

{{
  "texto_narrativo": "...",
  "prompt_imagen": "..."
}}

Reglas:
- El campo "texto_narrativo" debe estar en **español latinoamericano**, listo para narrarse en voz alta.
- El campo "prompt_imagen" debe estar en inglés, como un prompt visual para Stable Diffusion.

Texto: {idea}
"""

        respuesta = self.llm([HumanMessage(content=prompt)]).content
        bloque = re.findall(r'\{[^{}]*"texto_narrativo"[^{}]*"prompt_imagen"[^{}]*\}', respuesta, re.DOTALL)
        if not bloque:
            raise ValueError("No se encontró JSON válido.")
        datos = json.loads(bloque[0])
        return datos["texto_narrativo"], datos["prompt_imagen"]


class ControladorAgenteIA:
    def __init__(self, url_llm="http://localhost:1234/v1", modelo_llm="local-model"):
        self.llm = ChatOpenAI(
            model_name=modelo_llm,
            openai_api_base=url_llm,
            openai_api_key="not-needed"
        )

        # Instanciar componentes
        self.analizador = AnalizadorContenido(self.llm)
        self.generador_img = ImagenIA()
        self.generador_audio = GeneradorAudio(voz="es-CO-SalomeNeural")

        # Crear herramientas
        self.tools = [
            Tool(
                name="GenerarImagen",
                func=self.generador_img.generar_imagen,
                description="Genera una imagen a partir de un prompt visual en inglés."
            ),
            Tool(
                name="GenerarAudio",
                func=self.generador_audio.ejecutar,
                description="Genera un archivo de audio narrando un texto en español."
            ),
        ]

        # Agente con herramientas
        self.agente = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )

    def construir_instruccion(self, modo: str, texto: str, prompt: str) -> str:
        instrucciones = []
        if modo in ["imagen", "ambos"]:
            instrucciones.append(f'Genera una imagen usando este prompt visual: "{prompt}"')
        if modo in ["audio", "ambos"]:
            instrucciones.append(f'Genera un audio narrando esta historia en español: "{texto}"')
        return "\n".join(instrucciones)

    def ejecutar(self, idea: str, retornar=False):
        modo = self.analizador.clasificar_modo(idea)
        print(f"🧠 Modo detectado: {modo}")

        texto, prompt = self.analizador.generar_prompts(idea)
        print(f"📜 Texto narrativo:\n{texto}")
        print(f"🎨 Prompt visual:\n{prompt}")

        instruccion = self.construir_instruccion(modo, texto, prompt)
        print("\n🚀 Ejecutando acción con el agente...")
        respuesta = self.agente.run(instruccion)
        print("\n🤖 Respuesta del agente:\n", respuesta)

        if retornar:
            return modo, texto, prompt


if __name__ == "__main__":
    controlador = ControladorAgenteIA()
    idea = input("💡 Describe tu idea o petición: ")
    controlador.ejecutar(idea)
