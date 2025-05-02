from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    id_mensaje: int
    puntuacion: int
    comentario: Optional[str]

class FeedbackOut(BaseModel):
    id_feedback: int
    id_mensaje: int
    puntuacion: int
    comentario: Optional[str]
    fecha: datetime

    model_config = {
        "from_attributes": True
    }
