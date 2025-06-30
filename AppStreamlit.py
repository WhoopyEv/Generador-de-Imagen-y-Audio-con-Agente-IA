import streamlit as st
from ControladorGenerador import ControladorAgenteIA
from PIL import Image
import os

# Título de la app
st.set_page_config(page_title="🧠 Generador Multimodal IA", layout="centered")
st.title("🧠 Generador Multimodal con IA")
st.markdown("Genera imágenes y audios desde una descripción en lenguaje natural usando modelos locales.")

# Campo de texto
idea = st.text_area("✍️ Escribe tu idea:", placeholder="Ej: Un dragón dorado en una ciudad futurista y una historia para narrarlo")
ruta_img = "./images/imagen_generada.png"
ruta_audio = "./audios/voz_generada.mp3"
# Botón de generar
if st.button("✨ Generar"):
    if idea.strip() == "":
        st.warning("Por favor, escribe una idea.")
    else:
        # Crear controlador
        controlador = ControladorAgenteIA()
        
        # Ejecutar generación
        with st.spinner("Generando contenido con IA..."):
            modo, texto, prompt= controlador.ejecutar(idea, retornar=True)
        
        # Mostrar resultados
        st.success("¡Generación completada!")

        if modo in ["imagen", "ambos"] and ruta_img and os.path.exists(ruta_img):
            st.subheader("🎨 Imagen generada:")
            st.image(Image.open(ruta_img), use_column_width=True)

        if modo in ["audio", "ambos"] and ruta_audio and os.path.exists(ruta_audio):
            st.subheader("🔊 Audio generado:")
            st.audio(ruta_audio)

        st.code(f"🗣 Texto narrativo:\n{texto}", language="markdown")
        st.code(f"🎨 Prompt visual (EN):\n{prompt}", language="markdown")
