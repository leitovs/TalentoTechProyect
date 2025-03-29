import streamlit as st
from langraph_agent import LangraphAgent
import io
#from PIL import Image
from dotenv import load_dotenv
load_dotenv(override=True)


st.title("Bienvenido a EnergIA  🌞.🤖.⚡.🏠")
st.caption("Chatbot relacionado con la energía solar y su uso urbano")


# Inicializar el agente si no existe
if 'agent' not in st.session_state:
    st.session_state.agent = LangraphAgent(cc="123456")
    st.session_state.messages = []


# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict) and message["content"]["type"] == "bytes":
            #st.image(message["content"]["data"], caption="Imagen subida", use_container_width=True)
            st.write("Archivo Cargado...")
        else:
            st.write(message["content"])

# Agregar contenedor para chat input y botón
chat_container = st.container()

# Input de chat con botón de carga integrado
user_input = st.chat_input("Tu respuesta:", key="chat_input")


if user_input:
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Obtener y mostrar respuesta del agente
    response = st.session_state.agent.get_response(user_input)
    disclaimer = st.session_state.agent.get_disclaimer()

    if 'disclaimer' not in st.session_state and disclaimer:
        st.session_state.disclaimer = disclaimer
        
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


# File uploader con etiqueta descriptiva
if 'disclaimer' in st.session_state:
    uploaded_file = st.file_uploader(
        "Subir el archivo para análisis", 
        #type=['png', 'jpg', 'jpeg','pdf'],
        type=['pdf'], 
        key="file_uploader", 
        label_visibility="collapsed"
    )

    if uploaded_file:
        with st.chat_message("user"):
            #check if the file is an EMP billing receipt
            if uploaded_file.type == 'application/pdf':
                st.write("Archivo PDF subido")
                fbytes =  uploaded_file.read()
                response = st.session_state.agent.get_response(user_input="Archivo PDF subido",file_bytes=fbytes)
                st.session_state.messages.append({"role": "user", "content": {"type": "bytes", "data": fbytes}})
            else:
                st.write("Debe subir un pdf con el recibo de energía eléctrica")

        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})    