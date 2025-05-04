import logging
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from app.rag.feedback import FeedbackDBPostgres

logger = logging.getLogger(__name__)


class PromptBuilder:
    def __init__(self):
        self.feedback_db = FeedbackDBPostgres()

    def procesar_con_contexto(
        self, results: str, pregunta: str, anterior: str, historial: str
    ) -> str:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key="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",
        )

        # Opcional: podrías traer feedback relacionado con el mensaje anterior
        # En esta versión lo dejo comentado por si lo quieres usar en el futuro
        # similares = self.feedback_db.get_feedback_by_mensaje(anterior)

        prompt = f"""
Eres un experto en normativa de tránsito boliviana.

Contexto:
\"\"\"{results}\"\"\"

Pregunta actual:
\"{pregunta}\"

Pregunta anterior:
\"{anterior}\"

Instrucciones:
1. Sé conciso (máximo 150 palabras)
2. Cita artículos si es posible
3. Basado solo en el texto proporcionado
4. Tono profesional
5. Usa el historial si aporta valor

Historial resumido:
{historial}
"""
        respuesta = llm.invoke(prompt).content
        logger.info("✅ Respuesta generada con contexto.")
        return respuesta

    def procesar_sin_contexto(
        self, results: List[Dict[str, Any]], pregunta: str
    ) -> str:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key="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",
        )

        contenido = "\n\n".join([r["content"] for r in results])

        prompt = f"""
Eres un experto en normativa de tránsito boliviana.

Contexto:
\"\"\"{contenido}\"\"\"

Pregunta:
\"{pregunta}\"

Instrucciones:
1. Sé conciso (máximo 150 palabras)
2. Cita artículos si es posible
3. Basado solo en el texto proporcionado
4. Tono profesional
"""
        respuesta = llm.invoke(prompt).content
        logger.info("✅ Respuesta generada sin contexto.")
        return respuesta
