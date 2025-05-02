from fastapi import APIRouter, Depends, HTTPException
from app.models.contextos import ContextoCreate, ContextoOut
from app.crud import contextos as crud_contextos
from app.crud import chats as crud_chats
from app.core.auth import verificar_token

router = APIRouter(prefix="/contextos", tags=["Contextos"])


@router.post("/", response_model=ContextoOut)
def crear_contexto(
    contexto: ContextoCreate, id_usuario: int = Depends(verificar_token)
):
    # Verificar que el chat sea del usuario
    chat = crud_chats.obtener_chat_por_id(contexto.id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para agregar contexto en este chat."
        )

    resultado = crud_contextos.crear_contexto(
        id_chat=contexto.id_chat, descripcion=contexto.descripcion
    )
    return ContextoOut(
        id_contexto=resultado["id_contexto"],
        id_chat=contexto.id_chat,
        contexto_numero=resultado["contexto_numero"],
        descripcion=contexto.descripcion,
        fecha_inicio=resultado["fecha_inicio"],
    )


@router.get("/{id_chat}", response_model=list[ContextoOut])
def obtener_contextos(id_chat: int, id_usuario: int = Depends(verificar_token)):
    chat = crud_chats.obtener_chat_por_id(id_chat)
    if not chat or chat["id_usuario"] != id_usuario:
        raise HTTPException(
            status_code=403, detail="No autorizado para ver contextos de este chat."
        )

    contextos = crud_contextos.obtener_contextos_chat(id_chat)
    return contextos
