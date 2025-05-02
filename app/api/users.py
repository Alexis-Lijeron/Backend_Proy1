from fastapi import APIRouter
from app.models.users import UserCreate, UserOut
from app.crud import users as crud_users

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.post("/", response_model=UserOut)
def crear_usuario(usuario: UserCreate):
    id_usuario = crud_users.crear_usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        contrasena=usuario.contrasena
    )
    return UserOut(id_usuario=id_usuario, nombre=usuario.nombre, correo=usuario.correo, fecha_registro=None)
