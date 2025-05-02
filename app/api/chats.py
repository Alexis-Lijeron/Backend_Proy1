from fastapi import APIRouter
from app.models.chats import ChatCreate, ChatOut
from app.crud import chats as crud_chats

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=ChatOut)
def crear_chat(chat: ChatCreate):
    id_chat = crud_chats.crear_chat(
        id_usuario=chat.id_usuario,
        titulo=chat.titulo
    )
    return ChatOut(id_chat=id_chat, id_usuario=chat.id_usuario, titulo=chat.titulo, fecha_inicio=None)
