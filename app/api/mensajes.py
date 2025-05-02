from fastapi import APIRouter, Depends, HTTPException
from app.models.mensajes import MensajeCreate, MensajeOut
from app.crud import mensajes as crud_mensajes
from app.crud import chats as crud_chats
from app.core.auth import verificar_token

router = APIRouter(prefix="/mensajes", tags=["Mensajes"])


@router.post("/", response_model=MensajeOut)
def insertar_mensaje(
    mensaje: MensajeCreate, id_usuario: int = Depends(verificar_token)
):
    # Verificar que el chat sea del usuario
    chat = crud_chats.obtener_chat_por_id(mensaje.id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para agregar mensajes en este chat."
        )

    resultado = crud_mensajes.insertar_mensaje(
        id_chat=mensaje.id_chat,
        id_contexto=mensaje.id_contexto,
        tipo=mensaje.tipo,
        contenido=mensaje.contenido,
    )
    return MensajeOut(
        id_mensaje=resultado["id_mensaje"],
        id_chat=mensaje.id_chat,
        id_contexto=mensaje.id_contexto,
        tipo=mensaje.tipo,
        contenido=mensaje.contenido,
        fecha=resultado["fecha"],
    )


@router.get("/{id_chat}/{id_contexto}", response_model=list[MensajeOut])
def obtener_mensajes(
    id_chat: int, id_contexto: int, id_usuario: int = Depends(verificar_token)
):
    chat = crud_chats.obtener_chat_por_id(id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para ver mensajes de este chat/contexto.",
        )

    mensajes = crud_mensajes.obtener_mensajes_contexto(id_chat, id_contexto)
    return mensajes


@router.get("/chat/{id_chat}", response_model=list[MensajeOut])
def obtener_mensajes_chat(id_chat: int, id_usuario: int = Depends(verificar_token)):
    chat = crud_chats.obtener_chat_por_id(id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para ver mensajes de este chat."
        )

    mensajes = crud_mensajes.obtener_mensajes_chat(id_chat)
    return mensajes
