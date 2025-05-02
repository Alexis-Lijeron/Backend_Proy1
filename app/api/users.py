from fastapi import APIRouter, HTTPException, Depends
from app.models.users import UserCreate, UserOut, UserLogin, TokenData
from app.crud import users as crud_users
from app.core import auth

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.post("/", response_model=UserOut)
def crear_usuario(usuario: UserCreate):
    resultado = crud_users.crear_usuario(
        nombre=usuario.nombre, correo=usuario.correo, contrasena=usuario.contrasena
    )
    return UserOut(
        id_usuario=resultado["id_usuario"],
        nombre=usuario.nombre,
        correo=usuario.correo,
        fecha_registro=resultado["fecha_registro"],
    )


@router.post("/login", response_model=TokenData)
def login_usuario(user_login: UserLogin):
    usuario = crud_users.verificar_usuario(user_login.correo, user_login.contrasena)
    if usuario:
        token = auth.crear_token({"id_usuario": usuario["id_usuario"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
        }
    else:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")


@router.get("/me", response_model=UserOut)
def obtener_mi_usuario(id_usuario: int = Depends(auth.verificar_token)):
    usuario = crud_users.obtener_usuario_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
