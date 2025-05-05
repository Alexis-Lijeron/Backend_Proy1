from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base


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

    model_config = {"from_attributes": True}


class Feedback(Base):
    __tablename__ = "feedbacks"

    id_feedback = Column(Integer, primary_key=True, index=True)
    id_mensaje = Column(Integer, ForeignKey("mensajes.id_mensaje"), nullable=False)
    puntuacion = Column(Integer)
    comentario = Column(Text)
    fecha = Column(DateTime, default=datetime.utcnow)

    mensaje = relationship("Mensaje", backref="feedbacks")
