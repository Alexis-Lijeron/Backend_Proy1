from fastapi import APIRouter
from app.models.users import UserCreate, UserOut
from app.crud import users as crud_users

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.post("/", response_model=UserOut)
def crear_usuario(usuario: UserCreate):
    id_usuario = crud_users.crear_usuario(
        nombre=usuario.nombre, correo=usuario.correo, contrasena=usuario.contrasena
    )
    return UserOut(
        id_usuario=id_usuario,
        nombre=usuario.nombre,
        correo=usuario.correo,
        fecha_registro=None,
    )


from app.models.users import UserLogin, UserLoginOut


@router.post("/login", response_model=UserLoginOut)
def login_usuario(user_login: UserLogin):
    usuario = crud_users.verificar_usuario(user_login.correo, user_login.contrasena)
    if usuario:
        return usuario
    else:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
