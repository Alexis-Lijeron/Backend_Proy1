from app.core.db_connection import get_connection

def crear_usuario(nombre: str, correo: str = None, contrasena: str = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena)
            VALUES (%s, %s, %s)
            RETURNING id_usuario
            """, (nombre, correo, contrasena))
            (id_usuario,) = cursor.fetchone()
            conn.commit()
            return id_usuario
