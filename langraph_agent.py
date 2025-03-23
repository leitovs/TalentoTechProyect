from typing import Dict, Optional
from PIL import Image
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import logging

class LangraphAgent:
    def __init__(self, cc: int):
        self.cc = cc  # Placeholder for the conversation context

        llm = AzureChatOpenAI(model="gpt-4o-mini", temperature=0, api_version="2025-01-01-preview")

        class ImageExtractionInput(BaseModel):
            image_path: str = Field(description="Ruta o URL de la imagen del recibo energético del usuario")
            
        class InstallationEstimateInput(BaseModel):
            location: str = Field(description="Ubicación donde se instalarán los paneles (ciudad/región)")
            roof_area: float = Field(description="Área disponible en el techo en metros cuadrados")
            monthly_consumption: float = Field(description="Consumo mensual promedio en kWh")
            budget: float = Field(description="Presupuesto disponible para la instalación en pesos")

        @tool("extract_energy_consumption", args_schema=ImageExtractionInput)
        def extract_energy_consumption(image_path: str) -> str:
            """
            Extrae datos de consumo energético de una imagen de recibo.
            
            Parámetros:
            - image_path: Ruta o URL de la imagen del recibo energético
            
            Retorna:
            - Un objeto con los datos extraídos del consumo energético incluyendo kWh mensuales y dirección
            """
            # Implementation placeholder
            return "He procesado la imagen y extraído: consumo mensual de 350 kWh, dirección: Av. Principal 123, tarifa: $0.18/kWh"

        @tool("estimate_installation_cost", args_schema=InstallationEstimateInput)
        def estimate_installation_cost(location: str, roof_area: float, monthly_consumption: float, budget: float) -> str:
            """
            Calcula el costo estimado y ROI de una instalación de paneles solares.
            
            Parámetros:
            - location: Ubicación donde se instalarán los paneles
            - roof_area: Área disponible en metros cuadrados
            - monthly_consumption: Consumo mensual promedio en kWh
            - budget: Presupuesto disponible para la instalación
            
            Retorna:
            - Detalles sobre la instalación recomendada, costo estimado, ROI y tiempo de amortización
            """
            # Implementation placeholder
            return f"Para una instalación en {location} con {roof_area}m² y consumo de {monthly_consumption}kWh:\n- Costo estimado: ${budget * 0.8}\n- ROI: 15%\n- Amortización: 6 años\n- Capacidad: 4.5kW (12 paneles)"

        tools = [extract_energy_consumption, estimate_installation_cost]

        # # # Define the prompt template for the agent
        prefix = """
        # Consultor Especializado en Energía Solar

        Eres un consultor especializado en instalaciones de paneles solares. Tu objetivo es brindar al usuario información precisa sobre:
        1. Análisis de su consumo energético actual
        2. Recomendaciones personalizadas para instalación de paneles solares
        3. Estimación de costos, retorno de inversión (ROI) y amortización

        ## Flujo de conversación:
        1. Saluda y explica brevemente cómo puedes ayudar
        2. Solicita la imagen del recibo de energía del usuario
        3. Utiliza la herramienta "extract_energy_consumption" para analizar la imagen
        4. Pregunta información adicional necesaria:
        - Ubicación específica (ciudad/región)
        - Área disponible en el techo (metros cuadrados)
        - Presupuesto aproximado
        5. Utiliza la herramienta "estimate_installation_cost" con todos los datos recopilados
        6. Presenta los resultados de manera clara y responde cualquier duda adicional

        ## Notas importantes:
        - Mantén un tono profesional pero amigable
        - Si faltan datos, solicítalos amablemente al usuario
        - Explica los términos técnicos de manera accesible
        - Proporciona siempre recomendaciones basadas en los datos reales del usuario
        - Si no puedes determinar con precisión algún dato, menciona los rangos posibles
        """

        memory = MemorySaver()

        self.agent = create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            prompt=prefix,
        )

    def get_response(self, user_input: str = None, image: Image = None) -> str:
        # Si hay una imagen, procesarla
        if image:
            # Aquí puedes agregar lógica para procesar la imagen
            # Por ahora retornamos una respuesta genérica
            return "He recibido tu imagen. Por favor, cuéntame más sobre tu proyecto de energía solar."
        
        # return "Por favor, proporciona un mensaje o una imagen."
        # Procesar entrada de texto normal
        if user_input:
            answer = self.agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config={"configurable": {"thread_id": self.cc}}, stream_mode = "values")["messages"][-1].content
            logging.info(f"Respuesta del agente: {answer}")
            return answer
