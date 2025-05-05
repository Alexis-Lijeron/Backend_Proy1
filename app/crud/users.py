from datetime import datetime
import bcrypt
from app.core.db_connection import get_connection


def crear_usuario(nombre: str, correo: str = None, contrasena: str = None):
    if contrasena:
        contrasena_hashed = bcrypt.hashpw(
            contrasena.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
    else:
        contrasena_hashed = None

    fecha_registro = datetime.utcnow()  # 👈 asignar aquí

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO usuarios (nombre, correo, contrasena, fecha_registro)
            VALUES (%s, %s, %s, %s)
            RETURNING id_usuario, fecha_registro
            """,
                (nombre, correo, contrasena_hashed, fecha_registro),
            )
            id_usuario, fecha_registro = cursor.fetchone()
            conn.commit()
            return {"id_usuario": id_usuario, "fecha_registro": fecha_registro}


def verificar_usuario(correo: str, contrasena: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_usuario, nombre, correo, contrasena
            FROM usuarios
            WHERE correo = %s
            """,
                (correo,),
            )
            resultado = cursor.fetchone()
            if resultado:
                id_usuario, nombre, correo, contrasena_hashed = resultado
                if contrasena_hashed and bcrypt.checkpw(
                    contrasena.encode("utf-8"), contrasena_hashed.encode("utf-8")
                ):
                    return {
                        "id_usuario": id_usuario,
                        "nombre": nombre,
                        "correo": correo,
                    }
    return None


def obtener_usuario_por_id(id_usuario: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_usuario, nombre, correo, fecha_registro
            FROM usuarios
            WHERE id_usuario = %s
            """,
                (id_usuario,),
            )
            resultado = cursor.fetchone()
            if resultado:
                return {
                    "id_usuario": resultado[0],
                    "nombre": resultado[1],
                    "correo": resultado[2],
                    "fecha_registro": resultado[3],
                }
            return None
