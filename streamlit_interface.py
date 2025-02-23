import streamlit as st
from langraph_agent import LangraphAgent
import io
from PIL import Image

# Inicializar el agente si no existe
if 'agent' not in st.session_state:
    st.session_state.agent = LangraphAgent()
    st.session_state.messages = []

st.title("Consultor de Energía Solar")

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Campo de entrada para el usuario
user_input = st.chat_input("Tu respuesta:")

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
