from pydantic import BaseModel
from datetime import datetime

class MensajeCreate(BaseModel):
    id_chat: int
    id_contexto: int
    tipo: str  # 'pregunta' o 'respuesta'
    contenido: str

class MensajeOut(BaseModel):
    id_mensaje: int
    id_chat: int
    id_contexto: int
    tipo: str
    contenido: str
    fecha: datetime

    model_config = {
        "from_attributes": True
    }
