import asyncio
import edge_tts
import os

class GeneradorAudio:
    def __init__(self, voz="es-CO-GonzaloNeural", carpeta_salida="audios"):
        self.voz = voz
        self.carpeta_salida = carpeta_salida
        os.makedirs(self.carpeta_salida, exist_ok=True)

    async def generar(self, texto:str, nombre_archivo="voz_generada.mp3") -> str:
        ruta_completa = os.path.join(self.carpeta_salida, nombre_archivo)
        communicate = edge_tts.Communicate(text=texto, voice=self.voz)
        await communicate.save(ruta_completa)
        print(f"✅ Audio generado: {ruta_completa}")
        return ruta_completa

    def ejecutar(self, texto:str, nombre_archivo="voz_generada.mp3") -> str:
        return asyncio.run(self.generar(texto, nombre_archivo))

if __name__ == "__main__":
    generador = GeneradorAudio(voz="es-CO-SalomeNeural")

    texto = "¡Hola Felipe! Esta es una voz expresiva generada desde Python usando inteligencia artificial."

    ruta = generador.ejecutar(texto, "felipe_voz.mp3")
    print("Ruta devuelta:", ruta)
