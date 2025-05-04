from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time

from app.rag.core import RAGSystem
from app.crud.mensajes import insertar_mensaje
from app.crud.contextos import crear_contexto  

router = APIRouter(prefix="/rag", tags=["RAG"])

# Inicializar RAG
rag_system = RAGSystem(
    file_path="datos.txt",
    persist_dir="chroma_db",
    chunk_size=500,
    chunk_overlap=50,
)
rag_system.initialize()

# -------- MODELOS --------


class SearchRequest(BaseModel):
    pregunta: str
    k: Optional[int] = 5
    old_question: Optional[str] = ""
    old_response: Optional[str] = ""
    historial: Optional[List[str]] = []
    id_usuario: Optional[int] = None
    id_chat: Optional[int] = None
    id_contexto: Optional[int] = None


class FeedbackRequest(BaseModel):
    id_mensaje: int
    puntuacion: int
    comentario: Optional[str] = None


# -------- ENDPOINTS --------


@router.post("/search")
def buscar_respuesta(params: SearchRequest):
    """
    Busca una respuesta usando RAG.
    Si cambia el contexto, automáticamente crea un nuevo contexto.
    Guarda la pregunta y respuesta en la base.
    """
    if not params.id_chat:
        raise HTTPException(status_code=400, detail="Se requiere id_chat.")

    if not params.id_contexto:
        raise HTTPException(status_code=400, detail="Se requiere id_contexto.")

    pregunta_filtrada = rag_system.reemplazador.reemplazar_palabras(params.pregunta)
    historial_texto = "\n\n".join(params.historial)

    results = rag_system.search(pregunta_filtrada, k=params.k)

    hay_contexto = params.old_question and params.old_response
    es_contexto = False

    if hay_contexto:
        es_contexto = rag_system.is_related_context(
            params.old_question, pregunta_filtrada, params.old_response, historial_texto
        )

    # ------- Cambio automático de contexto -------
    id_contexto_usado = params.id_contexto

    if not es_contexto:
        # Crear automáticamente un nuevo contexto
        try:
            nuevo_id_contexto = crear_contexto(
                id_chat=params.id_chat,
                descripcion="Nuevo contexto creado automáticamente por cambio de tema",
            )
            id_contexto_usado = nuevo_id_contexto
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al crear nuevo contexto: {str(e)}"
            )

    # ------- Generar respuesta -------
    if es_contexto:
        combined_content = "\n\n".join([item["content"] for item in results])
        respuesta = rag_system.build_response_with_context(
            combined_content, pregunta_filtrada, params.old_question, historial_texto
        )
    else:
        respuesta = rag_system.build_response_without_context(
            results, pregunta_filtrada
        )

    # ------- Guardar pregunta y respuesta -------
    try:
        id_mensaje_pregunta = insertar_mensaje(
            id_chat=params.id_chat,
            id_contexto=id_contexto_usado,
            tipo="pregunta",
            contenido=params.pregunta,
        )
        id_mensaje_respuesta = insertar_mensaje(
            id_chat=params.id_chat,
            id_contexto=id_contexto_usado,
            tipo="respuesta",
            contenido=respuesta,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al guardar los mensajes: {str(e)}"
        )

    response_id = hashlib.md5(f"{params.pregunta}-{time.time()}".encode()).hexdigest()

    return {
        "pregunta": params.pregunta,
        "respuesta": respuesta,
        "resultados": results,
        "es_contexto": es_contexto,
        "response_id": response_id,
        "id_mensaje_pregunta": id_mensaje_pregunta,
        "id_mensaje_respuesta": id_mensaje_respuesta,
        "id_contexto_usado": id_contexto_usado,  # 👈 Muy importante, devuelve el contexto que se usó (puede ser uno nuevo)
    }


@router.post("/feedback")
def guardar_feedback(feedback: FeedbackRequest):
    """
    Guarda una puntuación del usuario sobre una respuesta.
    """
    try:
        id_feedback = rag_system.feedback_db.save_feedback(
            id_mensaje=feedback.id_mensaje,
            puntuacion=feedback.puntuacion,
            comentario=feedback.comentario,
        )
        return {"status": "success", "id_feedback": id_feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats")
def estadisticas_feedback():
    """
    Muestra estadísticas del feedback.
    """
    stats = rag_system.feedback_db.get_feedback_stats()
    return stats
