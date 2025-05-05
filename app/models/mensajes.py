from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base


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

    model_config = {"from_attributes": True}


class Mensaje(Base):
    __tablename__ = "mensajes"

    id_mensaje = Column(Integer, primary_key=True, index=True)
    id_chat = Column(Integer, ForeignKey("chats.id_chat"), nullable=False)
    id_contexto = Column(Integer, ForeignKey("contextos.id_contexto"), nullable=False)
    tipo = Column(String)  # 'pregunta' o 'respuesta'
    contenido = Column(Text)
    fecha = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", backref="mensajes")
    contexto = relationship("Contexto", backref="mensajes")
