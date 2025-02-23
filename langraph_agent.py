from typing import Dict, Optional
from PIL import Image
# from langraph import Graph, node
# from openai import AzureOpenAI
# from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_DEPLOYMENT_NAME

class LangraphAgent:
    def __init__(self):
        self.user_data = {
            "location": None,
            "budget": None,
            "space": None,
            "consumption": None,
            "cost_per_kw": None
        }
        self.current_question = 0
        self.questions = [
            "¿Cuál es tu ubicación específica (dirección, ciudad, departamento)?",
            "¿Cuál es tu presupuesto aproximado para el proyecto solar?",
            "¿Cuánto espacio tienes disponible para el proyecto (en metros cuadrados)?",
            "¿Cuál es tu consumo mensual de energía en kWh?",
            "¿Cuál es el costo por kilowatt en tu región?"
        ]
        
        # Inicializar cliente de Azure OpenAI
        # self.client = AzureOpenAI(
        #     azure_endpoint=AZURE_OPENAI_ENDPOINT,
        #     api_key=AZURE_OPENAI_KEY,
        #     api_version="2023-12-01-preview"
        # )

        # Prompt template para el asistente
        self.system_prompt = """Eres un experto consultor en energía solar. Tu tarea es ayudar a recopilar 
        información importante y proporcionar análisis detallados sobre proyectos solares. Mantén un tono 
        profesional pero amigable, y asegúrate de validar que la información proporcionada sea razonable."""

    def get_llm_response(self, user_input: str, context: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": context},
            {"role": "user", "content": user_input}
        ]
        
        response = self.client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content

    # @node
    def collect_info(self, user_input: str) -> Dict:
        if self.current_question >= len(self.questions):
            return self.predict_solar_roi(self.user_data)
        
        # Validar y procesar la entrada del usuario con GPT-4
        context = f"El usuario está respondiendo: {self.questions[self.current_question]}\nRespuesta: {user_input}"
        validation = self.get_llm_response(user_input, context)
        
        # Procesar la respuesta como antes
        if self.current_question == 0:
            self.user_data["location"] = user_input
        elif self.current_question == 1:
            try:
                self.user_data["budget"] = float(user_input.replace(',', '').replace('$', ''))
            except ValueError:
                return {"response": "Por favor, ingresa un número válido para el presupuesto."}
        elif self.current_question == 2:
            self.user_data["space"] = float(user_input)
        elif self.current_question == 3:
            self.user_data["consumption"] = float(user_input)
        elif self.current_question == 4:
            self.user_data["cost_per_kw"] = float(user_input)

        next_question = self.questions[self.current_question]
        self.current_question += 1
        return {"response": f"{validation}\n\n{next_question}"}

    # @node
    def predict_solar_roi(self, data: Dict) -> Dict:
        # Crear un prompt para el análisis
        analysis_prompt = f"""
        Analiza el siguiente proyecto solar:
        - Ubicación: {data['location']}
        - Presupuesto: ${data['budget']}
        - Espacio disponible: {data['space']} m²
        - Consumo mensual: {data['consumption']} kWh
        - Costo por kW: ${data['cost_per_kw']}
        
        Proporciona un análisis detallado del ROI y recomendaciones.
        """
        
        analysis = self.get_llm_response(analysis_prompt, "")
        
        # Cálculos básicos como antes
        estimated_production = data["space"] * 0.15
        annual_savings = estimated_production * data["cost_per_kw"] * 12
        simple_roi = (data["budget"] / annual_savings) * 100
        
        return {
            "estimated_production": estimated_production,
            "annual_savings": annual_savings,
            "roi_years": simple_roi,
            "message": analysis
        }

    def get_response(self, user_input: str = None, image: Image = None) -> str:
        # Si hay una imagen, procesarla
        if image:
            # Aquí puedes agregar lógica para procesar la imagen
            # Por ahora retornamos una respuesta genérica
            return "He recibido tu imagen. Por favor, cuéntame más sobre tu proyecto de energía solar."
        
        return "Por favor, proporciona un mensaje o una imagen."
        # Procesar entrada de texto normal
        if user_input:
            if all(value is not None for value in self.user_data.values()):
                return self.predict_solar_roi(self.user_data)["message"]
            else:
                return self.collect_info(user_input)["response"]
        
        
