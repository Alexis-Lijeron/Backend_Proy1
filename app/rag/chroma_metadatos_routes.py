from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time

from app.rag.core import RAGSystem

router = APIRouter(prefix="/chroma_metadatos", tags=["Chroma con Metadatos"])

# -------------------- INICIALIZAR RAG CON METADATOS --------------------

rag_system = RAGSystem(
    file_path="datos.txt",
    persist_dir="chroma_db_metadatos",
    chunk_size=500,
    chunk_overlap=50,
)
rag_system.initialize()

# -------------------- MODELOS --------------------


class ChromaSearchRequest(BaseModel):
    pregunta: str
    k: Optional[int] = 5
    documento: Optional[str] = None
    articulo: Optional[str] = None


class ChromaFeedback(BaseModel):
    query: str
    response: str
    rating: int
    comentario: Optional[str] = None
    metadatos: Optional[dict] = None


# -------------------- ENDPOINTS --------------------


@router.post("/search")
def buscar_chroma_metadatos(params: ChromaSearchRequest):
    """Busca chunks relevantes con metadatos."""
    pregunta_filtrada = rag_system.reemplazador.reemplazar_palabras(params.pregunta)

    results = rag_system.search(pregunta_filtrada, k=params.k)

    # Filtrar resultados si se especificó documento o artículo
    resultados_filtrados = []
    for res in results:
        meta = res["metadata"]
        if params.documento and meta.get("documento") != params.documento:
            continue
        if params.articulo and meta.get("articulo") != params.articulo:
            continue
        resultados_filtrados.append(res)

    chunks_usados = resultados_filtrados or results

    respuesta = rag_system.build_response_without_context(
        chunks_usados, pregunta_filtrada
    )

    response_id = hashlib.md5(f"{params.pregunta}-{time.time()}".encode()).hexdigest()

    resultados_con_metadatos = []
    for res in chunks_usados:
        resultados_con_metadatos.append(
            {
                "contenido": res["content"],
                "documento": res["metadata"].get("documento", "No especificado"),
                "capitulo": res["metadata"].get("capitulo", "No especificado"),
                "titulo": res["metadata"].get("titulo", "No especificado"),
                "articulo": res["metadata"].get("articulo", "No especificado"),
            }
        )

    return {
        "pregunta": params.pregunta,
        "respuesta": respuesta,
        "resultados": resultados_con_metadatos,
        "response_id": response_id,
    }


@router.post("/feedback")
def enviar_feedback_metadatos(params: ChromaFeedback):
    """Guardar feedback con metadatos."""
    feedback_id = rag_system.guardar_feedback(
        query=params.query,
        response=params.response,
        rating=params.rating,
        comentario=params.comentario,
        metadatos=params.metadatos,
    )
    return {"mensaje": "Feedback guardado", "id_feedback": feedback_id}
