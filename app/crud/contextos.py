from app.core.db_connection import get_connection


def obtener_siguiente_contexto_numero(id_chat: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT COALESCE(MAX(contexto_numero), 0) + 1
            FROM contextos_chat
            WHERE id_chat = %s
            """,
                (id_chat,),
            )
            (siguiente,) = cursor.fetchone()
            return siguiente


def crear_contexto(id_chat: int, descripcion: str = None) -> dict:
    contexto_numero = obtener_siguiente_contexto_numero(id_chat)
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO contextos_chat (id_chat, contexto_numero, descripcion)
            VALUES (%s, %s, %s)
            RETURNING id_contexto, fecha_inicio
            """,
                (id_chat, contexto_numero, descripcion),
            )
            id_contexto, fecha_inicio = cursor.fetchone()
            conn.commit()
            return {
                "id_contexto": id_contexto,
                "contexto_numero": contexto_numero,
                "fecha_inicio": fecha_inicio,
            }


def obtener_contextos_chat(id_chat: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_contexto, id_chat, contexto_numero, descripcion, fecha_inicio
            FROM contextos_chat
            WHERE id_chat = %s
            ORDER BY contexto_numero
            """,
                (id_chat,),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_contexto": r[0],
                    "id_chat": r[1],
                    "contexto_numero": r[2],
                    "descripcion": r[3],
                    "fecha_inicio": r[4],
                }
                for r in resultados
            ]
