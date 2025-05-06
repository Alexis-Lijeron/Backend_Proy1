import logging
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class ContextManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    def get_similarity(self, text1: str, text2: str) -> float:
        """Calcula la similitud coseno entre dos textos usando embeddings."""
        emb1 = self.embeddings.embed_query(text1)
        emb2 = self.embeddings.embed_query(text2)
        return cosine_similarity([emb1], [emb2])[0][0]

    def in_context(
        self,
        prev_question: str,
        new_question: str,
        prev_answer: str,
        context_history: str,
    ) -> bool:
        """
        Usa un modelo LLM para determinar si una nueva pregunta está relacionada con el contexto anterior.
        """
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        mensajes = [
            SystemMessage(
                content="Eres un clasificador experto en conversaciones legales. "
                "Determina si la nueva pregunta está relacionada con la pregunta y respuesta previas, considerando el historial de conversación. "
                "Debes tomar en cuenta que las personas a menudo hacen preguntas cortas o usan pronombres cuando continúan con un tema. "
                "Responde solo con 'Relacionado' si la nueva pregunta sigue el tema anterior o pide detalles adicionales, "
                "aunque la redacción sea diferente o resumida. "
                "Responde 'Nuevo tema' si cambia completamente de asunto."
            ),
            HumanMessage(
                content=f"""
    Pregunta anterior: {prev_question}
    Nueva pregunta: {new_question}
    Respuesta previa: {prev_answer}
    Historial de contexto: {context_history}
    """
            ),
        ]
        respuesta = llm.invoke(mensajes)
        logger.info(f"🔍 Evaluando contexto... Resultado del LLM: {respuesta.content}")
        return "relacionado" in respuesta.content.lower()

    """ except Exception as e:
        logger.error(f"⚠️ Error usando el LLM: {str(e)}. Usando embeddings como respaldo.")
        return self.in_context_embeddings(prev_question, new_question, prev_answer)
        respuesta = llm.invoke(mensajes)
        decision = respuesta.content.strip().lower()
        logger.info(f"🔍 Evaluando contexto... Resultado del LLM: {respuesta.content}")
        # return "relacionado" in respuesta.content.lower()
        return decision.startswith("relacionado") """

    def in_context_embeddings(
        self, prev_question: str, new_question: str, prev_answer: str
    ) -> bool:
        """
        Alternativa: Determina si hay contexto usando solo embeddings.
        """
        threshold = 0.8
        sim_questions = self.get_similarity(prev_question, new_question)
        sim_new_to_answer = self.get_similarity(new_question, prev_answer)

        combined_score = (0.6 * sim_questions) + (0.4 * sim_new_to_answer)
        logger.info(
            f"🔢 Similitud preguntas: {sim_questions}, Similitud respuesta: {sim_new_to_answer}, Score combinado: {combined_score}"
        )
        return combined_score >= threshold
