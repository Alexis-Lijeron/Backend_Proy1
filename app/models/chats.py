from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatCreate(BaseModel):
    titulo: Optional[str]


class ChatOut(BaseModel):
    id_chat: int
    id_usuario: int
    titulo: Optional[str]
    fecha_inicio: datetime

    model_config = {"from_attributes": True}
