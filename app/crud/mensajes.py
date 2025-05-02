from app.core.db_connection import get_connection


def insertar_mensaje(id_chat: int, id_contexto: int, tipo: str, contenido: str) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO mensajes (id_chat, id_contexto, tipo, contenido)
            VALUES (%s, %s, %s, %s)
            RETURNING id_mensaje, fecha
            """,
                (id_chat, id_contexto, tipo, contenido),
            )
            id_mensaje, fecha = cursor.fetchone()
            conn.commit()
            return {"id_mensaje": id_mensaje, "fecha": fecha}


def obtener_mensajes_contexto(id_chat: int, id_contexto: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_mensaje, id_chat, id_contexto, tipo, contenido, fecha
            FROM mensajes
            WHERE id_chat = %s AND id_contexto = %s
            ORDER BY fecha
            """,
                (id_chat, id_contexto),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_mensaje": r[0],
                    "id_chat": r[1],
                    "id_contexto": r[2],
                    "tipo": r[3],
                    "contenido": r[4],
                    "fecha": r[5],
                }
                for r in resultados
            ]


def obtener_mensajes_chat(id_chat: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_mensaje, id_chat, id_contexto, tipo, contenido, fecha
            FROM mensajes
            WHERE id_chat = %s
            ORDER BY fecha
            """,
                (id_chat,),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_mensaje": r[0],
                    "id_chat": r[1],
                    "id_contexto": r[2],
                    "tipo": r[3],
                    "contenido": r[4],
                    "fecha": r[5],
                }
                for r in resultados
            ]


def obtener_mensaje_por_id(id_mensaje: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_mensaje, id_chat, id_contexto, tipo, contenido, fecha
            FROM mensajes
            WHERE id_mensaje = %s
            """,
                (id_mensaje,),
            )
            resultado = cursor.fetchone()
            if resultado:
                return {
                    "id_mensaje": resultado[0],
                    "id_chat": resultado[1],
                    "id_contexto": resultado[2],
                    "tipo": resultado[3],
                    "contenido": resultado[4],
                    "fecha": resultado[5],
                }
            return None
