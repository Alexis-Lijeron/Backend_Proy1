from fastapi import APIRouter, Depends, HTTPException
from app.models.feedbacks import FeedbackCreate, FeedbackOut
from app.crud import feedbacks as crud_feedbacks
from app.crud import mensajes as crud_mensajes
from app.crud import chats as crud_chats
from app.core.auth import verificar_token

router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


@router.post("/", response_model=FeedbackOut)
def insertar_feedback(
    feedback: FeedbackCreate, id_usuario: int = Depends(verificar_token)
):
    # Validar que el mensaje sea del usuario
    mensaje = crud_mensajes.obtener_mensaje_por_id(feedback.id_mensaje)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")
    chat = crud_chats.obtener_chat_por_id(mensaje["id_chat"])
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para dar feedback en este mensaje."
        )

    resultado = crud_feedbacks.insertar_feedback(
        id_mensaje=feedback.id_mensaje,
        puntuacion=feedback.puntuacion,
        comentario=feedback.comentario,
    )

    return FeedbackOut(
        id_feedback=resultado["id_feedback"],
        id_mensaje=feedback.id_mensaje,
        puntuacion=feedback.puntuacion,
        comentario=feedback.comentario,
        fecha=resultado["fecha"],
    )


@router.get("/usuario", response_model=list[FeedbackOut])
def listar_feedbacks_usuario(id_usuario: int = Depends(verificar_token)):
    feedbacks = crud_feedbacks.obtener_feedbacks_usuario(id_usuario)
    return feedbacks


@router.get("/mensaje/{id_mensaje}", response_model=list[FeedbackOut])
def listar_feedbacks_mensaje(
    id_mensaje: int, id_usuario: int = Depends(verificar_token)
):
    mensaje = crud_mensajes.obtener_mensaje_por_id(id_mensaje)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")
    chat = crud_chats.obtener_chat_por_id(mensaje["id_chat"])
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para ver feedbacks de este mensaje."
        )

    feedbacks = crud_feedbacks.obtener_feedbacks_mensaje(id_mensaje)
    return feedbacks
