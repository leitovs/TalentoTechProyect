# Proyecto de Streamlit

Este proyecto utiliza Streamlit para crear una interfaz de usuario interactiva.

## Requisitos

- Python 3.12
- Las dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2. Construye la imagen de Docker:
    ```bash
    docker build -t streamlit-app .
    ```

3. Ejecuta el contenedor de Docker:
    ```bash
    docker run -p 8501:8501 streamlit-app
    ```

4. Abre tu navegador web y ve a `http://localhost:8501` para ver la aplicación.

## Desarrollo

Para desarrollar y probar la aplicación localmente sin Docker:

1. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

2. Ejecuta la aplicación de Streamlit:
    ```bash
    streamlit run streamlit_interface.py
    ```

3. Abre tu navegador web y ve a `http://localhost:8501` para ver la aplicación.

## Desarrollo con Hot Reload

Para desarrollar con hot reload, puedes usar cualquiera de estas opciones:

1. **Usando Docker con volumen montado:**
    ```bash
    docker run -p 8501:8501 -v $(pwd):/app streamlit-app
    ```

2. **Desarrollo local con hot reload:**
    ```bash
    streamlit run streamlit_interface.py --server.runOnSave=true
    ```

Los cambios en el código se reflejarán automáticamente en la interfaz web.

**Nota:** Asegúrate de que la variable de entorno `STREAMLIT_SERVER_RUN_ON_SAVE` esté configurada como `true`.
