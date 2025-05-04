from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time

from app.rag.core import RAGSystem

router = APIRouter(prefix="/chroma", tags=["Chroma Simple"])

# Inicializamos el RAG (usa la misma base Chroma que todo el sistema)
rag_system = RAGSystem(
    file_path="datos.txt",
    persist_dir="chroma_db",
    chunk_size=500,
    chunk_overlap=50,
    modo_feedback="sqlite",
)
rag_system.initialize()

# -------------------- MODELOS --------------------


class ChromaSearchRequest(BaseModel):
    pregunta: str
    k: Optional[int] = 5  # Cantidad de chunks


class ChromaFeedbackRequest(BaseModel):
    query: str
    response: str
    rating: int  # 1 a 5
    comentario: Optional[str] = None


# -------------------- ENDPOINTS --------------------


@router.post("/search1")
def buscar_chroma(params: ChromaSearchRequest):
    """Hace una búsqueda simple en Chroma y responde con los chunks más relevantes."""
    pregunta_filtrada = rag_system.reemplazador.reemplazar_palabras(params.pregunta)

    results = rag_system.search(pregunta_filtrada, k=params.k)

    # Generar respuesta combinada
    respuesta = rag_system.build_response_without_context(results, pregunta_filtrada)

    response_id = hashlib.md5(f"{params.pregunta}-{time.time()}".encode()).hexdigest()

    return {
        "pregunta": params.pregunta,
        "respuesta": respuesta,
        "resultados": results,
        "response_id": response_id,
    }


@router.post("/feedback1")
def guardar_feedback_simple(fb: ChromaFeedbackRequest):
    """Guarda feedback simple sin vincularlo a un mensaje/chat/contexto."""
    try:
        id_feedback = rag_system.feedback_db.save_feedback(
            query=fb.query,
            response=fb.response,
            rating=fb.rating,
            comentario=fb.comentario or "Feedback sin mensaje asociado.",
        )
        return {"status": "success", "id_feedback": id_feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/listar")
def listar_feedbacks(limit: int = 50):
    """Devuelve los feedbacks guardados (máximo 50 por defecto)."""
    try:
        conn = rag_system.feedback_db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT query, response, rating, comentario, timestamp
            FROM feedback
            ORDER BY timestamp DESC
            LIMIT %s
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        feedbacks = []
        for row in rows:
            feedbacks.append(
                {
                    "pregunta": row[0],
                    "respuesta": row[1],
                    "puntuacion": row[2],
                    "comentario": row[3],
                    "fecha": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {"cantidad": len(feedbacks), "feedbacks": feedbacks}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar feedbacks: {str(e)}"
        )
