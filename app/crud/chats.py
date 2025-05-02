from app.core.db_connection import get_connection


def crear_chat(id_usuario: int, titulo: str = None) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO chats (id_usuario, titulo)
            VALUES (%s, %s)
            RETURNING id_chat, fecha_inicio
            """,
                (id_usuario, titulo),
            )
            id_chat, fecha_inicio = cursor.fetchone()
            conn.commit()
            return {"id_chat": id_chat, "fecha_inicio": fecha_inicio}


def obtener_chats_usuario(id_usuario: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_chat, id_usuario, titulo, fecha_inicio
            FROM chats
            WHERE id_usuario = %s
            ORDER BY fecha_inicio DESC
            """,
                (id_usuario,),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_chat": r[0],
                    "id_usuario": r[1],
                    "titulo": r[2],
                    "fecha_inicio": r[3],
                }
                for r in resultados
            ]


def obtener_chat_por_id(id_chat: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_chat, id_usuario, titulo, fecha_inicio
            FROM chats
            WHERE id_chat = %s
            """,
                (id_chat,),
            )
            r = cursor.fetchone()
            if r:
                return {
                    "id_chat": r[0],
                    "id_usuario": r[1],
                    "titulo": r[2],
                    "fecha_inicio": r[3],
                }
            return None


def eliminar_chat(id_chat: int, id_usuario: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            DELETE FROM chats
            WHERE id_chat = %s AND id_usuario = %s
            """,
                (id_chat, id_usuario),
            )
            filas_afectadas = cursor.rowcount
            conn.commit()
            return filas_afectadas > 0
