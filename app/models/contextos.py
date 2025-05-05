from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


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


class Contexto(Base):
    __tablename__ = "contextos"

    id_contexto = Column(Integer, primary_key=True, index=True)
    id_chat = Column(Integer, ForeignKey("chats.id_chat"), nullable=False)
    contexto_numero = Column(Integer)
    descripcion = Column(String)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", backref="contextos")
