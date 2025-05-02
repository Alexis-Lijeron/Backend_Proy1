from app.rag.embeddings import EmbeddingManager
from app.rag.context_manager import ContextManager
from app.rag.prompt_builder import PromptBuilder
from app.rag.feedback import FeedbackDBPostgres
from app.rag.filtros import ContextCache, filtro_palabras

class RAGSystem:
    def __init__(self, file_path: str, persist_dir: str = "chroma_db", chunk_size: int = 500, chunk_overlap: int = 50):
        self.embeddings = EmbeddingManager(file_path, persist_dir, chunk_size, chunk_overlap)
        self.context_manager = ContextManager()
        self.prompt_builder = PromptBuilder()
        self.feedback_db = FeedbackDBPostgres()
        self.cache = ContextCache()
        self.reemplazador = filtro_palabras()

    def initialize(self):
        self.embeddings.initialize()

    def search(self, query: str, k: int = 5):
        return self.embeddings.search(query, k)

    def is_related_context(self, prev_question, new_question, prev_answer, context_history):
        return self.context_manager.in_context(prev_question, new_question, prev_answer, context_history)

    def build_response_with_context(self, results, pregunta, anterior, historial):
        return self.prompt_builder.procesar_con_contexto(results, pregunta, anterior, historial)

    def build_response_without_context(self, results, pregunta):
        return self.prompt_builder.procesar_sin_contexto(results, pregunta)
