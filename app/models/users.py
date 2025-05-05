from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base

class UserCreate(BaseModel):
    nombre: str
    correo: Optional[EmailStr]
    contrasena: Optional[str]


class UserOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: Optional[EmailStr]
    fecha_registro: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    nombre: str
    correo: EmailStr


class User(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True)
    contrasena = Column(String)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
