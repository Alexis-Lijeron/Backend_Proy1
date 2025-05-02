from fastapi import APIRouter, Depends, HTTPException
from app.models.chats import ChatCreate, ChatOut
from app.crud import chats as crud_chats
from app.core.auth import verificar_token

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatOut)
def crear_chat(chat: ChatCreate, id_usuario: int = Depends(verificar_token)):
    resultado = crud_chats.crear_chat(id_usuario=id_usuario, titulo=chat.titulo)
    return ChatOut(
        id_chat=resultado["id_chat"],
        id_usuario=id_usuario,
        titulo=chat.titulo,
        fecha_inicio=resultado["fecha_inicio"],
    )


@router.get("/", response_model=list[ChatOut])
def listar_chats(id_usuario: int = Depends(verificar_token)):
    chats = crud_chats.obtener_chats_usuario(id_usuario)
    return chats


@router.get("/{id_chat}", response_model=ChatOut)
def obtener_chat(id_chat: int, id_usuario: int = Depends(verificar_token)):
    chat = crud_chats.obtener_chat_por_id(id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=404, detail="Chat no encontrado o no autorizado"
        )
    return chat


@router.delete("/{id_chat}")
def eliminar_chat(id_chat: int, id_usuario: int = Depends(verificar_token)):
    eliminado = crud_chats.eliminar_chat(id_chat, id_usuario)
    if eliminado:
        return {"mensaje": "Chat eliminado exitosamente"}
    else:
        raise HTTPException(
            status_code=404, detail="Chat no encontrado o no autorizado"
        )
