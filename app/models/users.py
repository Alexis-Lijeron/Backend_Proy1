from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


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


class UserLoginOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
