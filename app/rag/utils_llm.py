from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from typing import Optional
from app.core.config import settings


def generar_descripcion_contexto(
    pregunta: str, pregunta_anterior: Optional[str] = None
) -> str:
    """
    Usa un LLM para generar una descripción breve del nuevo contexto basado en la nueva pregunta y la anterior.
    """
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    prompt = f"""
Quiero que resumas el tema principal de la siguiente pregunta de usuario para usarla como título o descripción de un contexto de conversación.

Pregunta nueva: "{pregunta}"
"""
    if pregunta_anterior:
        prompt += f'Pregunta anterior: "{pregunta_anterior}"\n'

    prompt += "Devuelve solo la descripción breve, sin comillas, máximo 12 palabras."

    mensajes = [
        SystemMessage(
            content="Eres un asistente que genera descripciones breves para temas de conversación."
        ),
        HumanMessage(content=prompt),
    ]

    respuesta = llm.invoke(mensajes)
    return respuesta.content.strip()


def generar_prompt_con_contexto(
    documentos: str, pregunta: str, pregunta_anterior: str, historial: str
) -> str:
    prompt = f"""
Eres un asistente legal experto en normativa de tránsito boliviana. Tu tarea es responder de manera precisa y concreta.

IMPORTANTE:
- Usa solamente la información de los documentos proporcionados.
- Limita la respuesta únicamente al tema de la pregunta actual y el contexto previo.
- No agregues información adicional o general no relacionada directamente.
- Si la información no está presente en los documentos o contexto, indica claramente que no se encontró información relevante.

--- CONTEXTO PREVIO ---
{historial}

--- PREGUNTA ANTERIOR ---
{pregunta_anterior}

--- PREGUNTA ACTUAL ---
{pregunta}

--- DOCUMENTOS RELEVANTES ---
{documentos}

Redacta una respuesta clara, concisa y formal. Si corresponde, incluye referencias a los artículos mencionados.
"""
    return prompt
