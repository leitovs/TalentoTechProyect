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

## Agentes de IA

Este proyecto incorpora agentes de IA utilizando dos enfoques diferentes: Langraph y Azure AI Projects.

### Agente con Langraph

Para crear y ejecutar el agente utilizando Langraph:

1. Instala las dependencias necesarias:
    ```bash
    pip install langgraph langchain-openai pydantic python-dotenv
    ```

2. Configura las variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto
   - Añade las credenciales de Azure OpenAI:
     ```
     AZURE_OPENAI_API_KEY=<tu-api-key>
     AZURE_OPENAI_ENDPOINT=<tu-endpoint>
     AZURE_OPENAI_API_VERSION=2025-01-01-preview
     ```

3. Para ejecutar el agente:
    ```python
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import AzureChatOpenAI
    from langgraph.checkpoint.memory import MemorySaver
    
    # Configura el modelo LLM
    llm = AzureChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0, 
        api_version="2025-01-01-preview"
    )
    
    # Define herramientas y prompt
    # ...
    
    # Crea el agente
    memory = MemorySaver()
    agent = create_react_agent(llm, tools=tools, checkpointer=memory, prompt=prefix)
    
    # Invoca el agente
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "tu_pregunta"}]}, 
        config={"configurable": {"thread_id": "id_unico"}}
    )
    ```

### Agente con Azure AI Projects

Para crear y ejecutar el agente utilizando Azure AI Projects:

1. Instala las dependencias necesarias:
    ```bash
    pip install azure-ai-projects azure-identity python-dotenv
    ```

2. Configura el acceso a Azure:
    ```bash
    # Instala la CLI de Azure si es necesario
    pip install azure-cli
    
    # Inicia sesión en Azure
    az login
    
    # Obtén la cadena de conexión del proyecto
    az ml workspace show -n {project_name} --resource-group {resource_group_name} --query discovery_url
    ```

3. Configura las variables de entorno:
   - Crea o actualiza el archivo `.env` en la raíz del proyecto
   - Añade la cadena de conexión:
     ```
     PROJECT_CONNECTION_STRING="<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
     ```

4. Para crear y ejecutar el agente:
    ```python
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects.models import FunctionTool, ToolSet
    import os
    
    # Crear cliente del proyecto de AI
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )
    
    # Configurar toolset con funciones personalizadas
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    
    # Crear agente
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini", 
        name="mi-agente", 
        instructions="Instrucciones para el agente", 
        toolset=toolset
    )
    
    # Crear hilo y mensaje
    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Tu mensaje aquí"
    )
    
    # Ejecutar el agente
    run = project_client.agents.create_and_process_run(
        thread_id=thread.id, 
        agent_id=agent.id
    )
    ```

Consulta los notebooks en `agent_config/` para ejemplos detallados.
