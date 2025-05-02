from fastapi import APIRouter
from app.models.contextos import ContextoCreate, ContextoOut
from app.crud import contextos as crud_contextos

router = APIRouter(prefix="/contextos", tags=["Contextos"])

@router.post("/", response_model=ContextoOut)
def crear_contexto(contexto: ContextoCreate):
    id_contexto = crud_contextos.creaar_contexto(
        id_chat=contexto.id_chat,
        descripcion=contexto.descripcion
    )
    return ContextoOut(id_contexto=id_contexto, id_chat=contexto.id_chat, contexto_numero=None, descripcion=contexto.descripcion, fecha_inicio=None)
