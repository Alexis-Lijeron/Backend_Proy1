from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContextoCreate(BaseModel):
    id_chat: int
    descripcion: Optional[str]


class ContextoOut(BaseModel):
    id_contexto: int
    id_chat: int
    contexto_numero: int
    descripcion: Optional[str]
    fecha_inicio: datetime

    model_config = {"from_attributes": True}
