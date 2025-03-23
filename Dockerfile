# Usar una imagen base de Python
FROM public.ecr.aws/docker/library/python:3.13.2-slim-bookworm

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Establecer variable de entorno para desarrollo
ENV STREAMLIT_SERVER_RUN_ON_SAVE=true
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE="auto"

# Exponer el puerto
EXPOSE 8501

# Comando para ejecutar la aplicación de Streamlit
CMD ["streamlit", "run", "streamlit_interface.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true", "browser.gatherUsageStats=false"]
