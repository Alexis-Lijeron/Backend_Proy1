from app.core.db_connection import get_connection


def insertar_mensaje(id_chat: int, id_contexto: int, tipo: str, contenido: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO mensajes (id_chat, id_contexto, tipo, contenido)
            VALUES (%s, %s, %s, %s)
            RETURNING id_mensaje
            """,
                (id_chat, id_contexto, tipo, contenido),
            )
            (id_mensaje,) = cursor.fetchone()
            conn.commit()
            return id_mensaje


def guardar_mensaje(id_chat: int, id_contexto: int, tipo: str, contenido: str) -> int:
    """
    Guarda un mensaje en la base de datos y devuelve su ID.
    tipo: 'pregunta' o 'respuesta'
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO mensajes (id_chat, id_contexto, tipo, contenido)
                VALUES (%s, %s, %s, %s)
                RETURNING id_mensaje
            """,
                (id_chat, id_contexto, tipo, contenido),
            )
            id_mensaje = cursor.fetchone()[0]
            conn.commit()
            return id_mensaje
