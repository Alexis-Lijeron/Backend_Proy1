from fastapi import APIRouter
from app.models.mensajes import MensajeCreate, MensajeOut
from app.crud import mensajes as crud_mensajes

router = APIRouter(prefix="/mensajes", tags=["Mensajes"])

@router.post("/", response_model=MensajeOut)
def insertar_mensaje(mensaje: MensajeCreate):
    id_mensaje = crud_mensajes.insertar_mensaje(
        id_chat=mensaje.id_chat,
        id_contexto=mensaje.id_contexto,
        tipo=mensaje.tipo,
        contenido=mensaje.contenido
    )
    return MensajeOut(id_mensaje=id_mensaje, id_chat=mensaje.id_chat, id_contexto=mensaje.id_contexto, tipo=mensaje.tipo, contenido=mensaje.contenido, fecha=None)
