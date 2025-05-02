from app.core.db_connection import get_connection


def crear_usuario(nombre: str, correo: str = None, contrasena: str = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO usuarios (nombre, correo, contrasena)
            VALUES (%s, %s, %s)
            RETURNING id_usuario
            """,
                (nombre, correo, contrasena),
            )
            (id_usuario,) = cursor.fetchone()
            conn.commit()
            return id_usuario


def verificar_usuario(correo: str, contrasena: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_usuario, nombre, correo
            FROM usuarios
            WHERE correo = %s AND contrasena = %s
            """,
                (correo, contrasena),
            )
            resultado = cursor.fetchone()
            if resultado:
                id_usuario, nombre, correo = resultado
                return {"id_usuario": id_usuario, "nombre": nombre, "correo": correo}
            return None
