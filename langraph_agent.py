from typing import Dict, Optional
from PIL import Image
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import logging
from tools import BillAnalyzer
import os

class LangraphAgent:
    def __init__(self, cc: int):
        self.cc = cc  # Placeholder for the conversation context
        self.disclaimer_acepted = False  # Placeholder for the disclaimer
        doc_endpoint = os.getenv("AZURE_DOCUMENT_ENDPOINT")
        doc_key = os.getenv("AZURE_DOCUMENT_KEY")

        self.bill = BillAnalyzer(doc_endpoint, doc_key)
        self.file_bts = None
        llm = AzureChatOpenAI(model="gpt-4o-mini", temperature=0, api_version="2025-01-01-preview")

        class FileExtractionInput(BaseModel):
            file_bytes: bytes = Field(description="Archivo PDF del recibo energético file_bytes ")
            
        class InstallationEstimateInput(BaseModel):
            location: str = Field(description="Ubicación donde se instalarán los paneles (ciudad/región)")
            roof_area: float = Field(description="Área disponible en el techo en metros cuadrados")
            monthly_consumption: float = Field(description="Consumo mensual promedio en kWh")
            budget: float = Field(description="Presupuesto disponible para la instalación en pesos")

        class DisclaimerInput(BaseModel):
            operation: str = Field(description="Indica la operacion sobre los términos y condiciones del servicio. Valores esperados: '?', 'si', 'no'")

        @tool("extract_energy_consumption", args_schema=FileExtractionInput)
        def extract_energy_consumption(file_bytes: bytes) -> str:
            """
            Extrae datos de consumo energético de un archivo PDF de recibo.
            
            Parámetros:
            - image_path: Ruta o URL del archivo PRF del recibo energético
            
            Retorna:
            - Un objeto con los datos extraídos del consumo energético incluyendo kWh mensuales y dirección
            """
            print("------------------------------------------------------")
            result = self.bill.get_result_layout_bytes(self.file_bts,save_result=False)

            #print("hola, estoy en extract_energy_consumption")
            #print("se debe implementar el contenido de la tool ****************")   
            # Implementation placeholder
            #return "He procesado la imagen y extraído: consumo mensual de 350 kWh, dirección: Av. Principal 123, tarifa: $0.18/kWh"
            print(result)
            #return result
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

        @tool("disclaimer", args_schema=DisclaimerInput)
        def disclaimer(operation:str) -> dict:
            """
            Gestiona el proceso de descargo de responsabilidad.
            Esta función está diseñada para gestionar el paso de descargo de responsabilidad en el flujo de conversación.
            Según la respuesta del usuario, genera un diccionario que contiene el tipo, el texto y el estado del descargo de responsabilidad. Esta funcionalidad también puede activar acciones adicionales si es necesario.

            Args:
                acepted (str): La respuesta del usuario al descargo de responsabilidad. Los valores esperados son "?" "si" o "no".

            Devuelve:
                dict: Un diccionario que contiene las siguientes claves:
                    - "type" (str): Indica el tipo de respuesta, siempre establecida como "disclaimer".
                    - "text" (str): El texto del descargo de responsabilidad si el usuario no acepta ("no"), o una cadena vacía si acepta ("si").
                    - "status" (str): La respuesta del usuario ("si" o "no").
            """

            # esta funcionalidad se plantea como un tool ya que es un paso importante en el flujo de la conversación
            # de tal manera que des aquí se podrían desencadenar acciones adicionales si se desea
            d_response = {}
            d_response["type"] = "disclaimer"

            if operation == "?":
                d_response["text"] = """
                        # Aviso Legal

                        El uso de esta plataforma implica la aceptación expresa por parte del usuario para el tratamiento de los datos personales sensibles que puedan estar contenidos en las facturas de servicios públicos ingresadas al sistema. Dichos datos serán utilizados exclusivamente para los fines específicos establecidos por la plataforma y de acuerdo con la normativa aplicable en materia de protección de datos personales.\n\n
                        La plataforma no asume responsabilidad alguna por la veracidad, exactitud o integridad de los datos proporcionados en las facturas. La responsabilidad sobre el contenido de dichos datos recae únicamente en los emisores de las facturas y/o en los usuarios que las ingresen al sistema.\n\n
                        La plataforma y su agente de IA no asumen responsabilidad por los daños o perjuicios derivados del uso indebido de la información procesada mediante IA. \n\n
                        El usuario declara haber leído y comprendido este aviso legal y otorga su consentimiento expreso para el tratamiento de datos personales, en los términos establecidos. (para una información completa acerca de los términos y condiciones, favor dirigirse a la **sección: Aviso Legal**) \n\n
                """
                d_response["status"] = ""
            elif operation == "si":
                d_response["text"] = ""
                d_response["status"] = "True"
                self.disclaimer_acepted = True  # Actualiza el estado de aceptación del disclaimer
            elif operation == "no":
                d_response["text"] = ""
                d_response["status"] = "False"

            return d_response
        
        tools = [extract_energy_consumption, estimate_installation_cost, disclaimer]

        # # # Define the prompt template for the agent
        prefix = """
        # Consultor Especializado en Energía Solar

        Eres un consultor especializado en instalaciones de paneles solares. Tu objetivo es brindar al usuario información precisa sobre:
        1. Análisis de su consumo energético actual
        2. Recomendaciones personalizadas para instalación de paneles solares
        3. Estimación de costos, retorno de inversión (ROI) y amortización

        ## Flujo de conversación:
        1. Saluda y explica brevemente cómo puedes ayudar
        2. Pregunta al usuario si tiene conocimentos acerca de la politica de tratamiento de datos.indicale al usuario que si responde si estará aceptando los términos y condiciones de uso del servicio.
        -Si el usuario responde que no, entonces llama a la tool "disclaimer" utilizando acepted="?" como parametro. usa la propiedad "text" de la respuesta respuesta y enviala al usuario.
        3. espera la respuesta del usuario. 
        -Si el usuario responde no entonces llama a la tool "disclaimer" y muestra la respuesta al usuario.
        -Si el usuario responde que acepta los términos y condiciones de uso del servicio, entonces llama a la tool "disclaimer" y envia una respuesta al usuario
        -no puedes avanzar en la conversacion sin la acptacion de parte del usuario.
        4. Solicita el recibo de energía del usuario en formato PDF
        5. esperar a que el usuario cargue el archivo. 
        5. Si el usuario ingresa un archivo llamar a la tool "extract_energy_consumption" con el parametro "file_bytes" para analizar el archivo.
        6. Pregunta información adicional necesaria:
        - Ubicación específica (ciudad/región)
        - Área disponible en el techo (metros cuadrados)
        - Presupuesto aproximado
        7. Utiliza la herramienta "estimate_installation_cost" con todos los datos recopilados
        8. Presenta los resultados de manera clara y responde cualquier duda adicional

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

    def get_response(self, user_input: str = None, file_bytes: bytes = None) -> str:
        # Si hay una archivo, procesarla
        if file_bytes:
            # Aquí puedes agregar lógica para procesar el archivo PDF
            self.file_bts=file_bytes
            answer = self.agent.invoke({"messages": [{"role": "user", "content": user_input, "file_bytes":file_bytes}]}, config={"configurable": {"thread_id": self.cc}}, stream_mode = "values")["messages"][-1].content
            logging.info(f"Respuesta del agente: {answer}")
            return answer
        

        # Procesar entrada de texto normal
        if user_input:
            answer = self.agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config={"configurable": {"thread_id": self.cc}}, stream_mode = "values")["messages"][-1].content
            logging.info(f"Respuesta del agente: {answer}")
            return answer
        
    def get_disclaimer(self)->bool:
        """
        Devuelve el estado de aceptación del disclaimer.
        
        Returns:
            bool: True si el disclaimer ha sido aceptado, False en caso contrario.
        """
        return self.disclaimer_acepted