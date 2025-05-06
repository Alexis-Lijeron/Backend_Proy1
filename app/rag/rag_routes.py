from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time

from app.rag.core import RAGSystem
from app.crud.mensajes import insertar_mensaje, obtener_mensajes_contexto
from app.crud.contextos import crear_contexto
from app.rag.utils_llm import generar_descripcion_contexto

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
    mensajes_contexto = obtener_mensajes_contexto(
        id_chat=params.id_chat, id_contexto=params.id_contexto
    )
    historial_reducido = []
    N = 5  # últimas 5 interacciones
    for mensaje in mensajes_contexto[-N * 2 :]:
        rol = "Persona" if mensaje["tipo"] == "pregunta" else "Asistente"
        historial_reducido.append(f"{rol}: {mensaje['contenido']}")

    if historial_reducido:
        query = pregunta_filtrada + " " + " ".join(historial_reducido)
    else:
        query = pregunta_filtrada

    historial_texto = "\n\n".join(historial_reducido)

    # ------- Generar respuesta -------
    es_contexto = True
    if len(mensajes_contexto) > 0:
        ultima_pregunta = next(
            (
                m["contenido"]
                for m in reversed(mensajes_contexto)
                if m["tipo"] == "pregunta"
            ),
            "",
        )
        es_contexto = rag_system.is_related_context(
            ultima_pregunta, pregunta_filtrada, "", historial_texto
        )
    else:
        ultima_pregunta = ""
        es_contexto = True  # No hay historial, se asume que es mismo contexto

    id_contexto_usado = params.id_contexto
    if not es_contexto:
        descripcion_contexto = generar_descripcion_contexto(pregunta=params.pregunta)
        nuevo_id_contexto = crear_contexto(
            id_chat=params.id_chat, descripcion=descripcion_contexto
        )
        id_contexto_usado = nuevo_id_contexto["id_contexto"]
    # ------- Guardar pregunta y respuesta -------
    # Generar respuesta
    results = rag_system.search(query, k=params.k)
    combined_content = "\n\n".join([item["content"] for item in results])
    respuesta = rag_system.build_response_with_context(
        combined_content,
        pregunta_filtrada,
        ultima_pregunta if len(mensajes_contexto) > 0 else "",
        historial_texto,
    )

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
        "id_contexto_usado": id_contexto_usado,
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


@router.post("/public_search")
def buscar_respuesta_publica(params: SearchRequest):
    """
    Versión sin autenticación. Usa siempre el historial acumulado.
    """
    pregunta_filtrada = rag_system.reemplazador.reemplazar_palabras(params.pregunta)

    # Armar el contexto acumulado (historial + nueva pregunta)
    contexto_completo = "\n".join(params.historial or [])
    contexto_completo += f"\nPregunta actual: {pregunta_filtrada}"

    # Buscar con ese contexto acumulado
    results = rag_system.search(contexto_completo, k=params.k)

    # Generar respuesta SIN clasificador de contexto
    respuesta = rag_system.build_response_without_context(results, pregunta_filtrada)

    response_id = hashlib.md5(f"{params.pregunta}-{time.time()}".encode()).hexdigest()

    return {
        "pregunta": params.pregunta,
        "respuesta": respuesta,
        "resultados": results,
        "response_id": response_id,
    }
