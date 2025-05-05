from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class ChatCreate(BaseModel):
    titulo: Optional[str]


class ChatOut(BaseModel):
    id_chat: int
    id_usuario: int
    titulo: Optional[str]
    fecha_inicio: datetime

    model_config = {"from_attributes": True}


class Chat(Base):
    __tablename__ = "chats"

    id_chat = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    titulo = Column(String)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("User", backref="chats")
