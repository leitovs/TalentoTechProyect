import streamlit as st
from langraph_agent import LangraphAgent
import io
from PIL import Image
from dotenv import load_dotenv
load_dotenv(override=True)

# Inicializar el agente si no existe
if 'agent' not in st.session_state:
    st.session_state.agent = LangraphAgent(cc="123456")
    st.session_state.messages = []

st.title("Consultor de Energía Solar")

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict) and message["content"]["type"] == "image":
            st.image(message["content"]["data"], caption="Imagen subida", use_container_width=True)
        else:
            st.write(message["content"])

# Agregar contenedor para chat input y botón
chat_container = st.container()

# Input de chat con botón de carga integrado
user_input = st.chat_input("Tu respuesta:", key="chat_input")

# File uploader con etiqueta descriptiva
uploaded_file = st.file_uploader(
    "Subir imagen para análisis", 
    type=['png', 'jpg', 'jpeg'], 
    key="file_uploader", 
    label_visibility="collapsed"
)

if uploaded_file:
    image = Image.open(uploaded_file)
    with st.chat_message("user"):
        st.image(image, caption="Imagen subida", use_container_width=True)
    response = st.session_state.agent.get_response(image=image)
    st.session_state.messages.append({"role": "user", "content": {"type": "image", "data": image}})
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if user_input:
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Obtener y mostrar respuesta del agente
    response = st.session_state.agent.get_response(user_input)
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
