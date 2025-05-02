from app.core.db_connection import get_connection


def insertar_feedback(id_mensaje: int, puntuacion: int, comentario: str = None) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO feedback (id_mensaje, puntuacion, comentario)
            VALUES (%s, %s, %s)
            RETURNING id_feedback, fecha
            """,
                (id_mensaje, puntuacion, comentario),
            )
            id_feedback, fecha = cursor.fetchone()
            conn.commit()
            return {"id_feedback": id_feedback, "fecha": fecha}


def obtener_feedbacks_usuario(id_usuario: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT f.id_feedback, f.id_mensaje, f.puntuacion, f.comentario, f.fecha
            FROM feedback f
            JOIN mensajes m ON f.id_mensaje = m.id_mensaje
            JOIN chats c ON m.id_chat = c.id_chat
            WHERE c.id_usuario = %s
            ORDER BY f.fecha DESC
            """,
                (id_usuario,),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_feedback": r[0],
                    "id_mensaje": r[1],
                    "puntuacion": r[2],
                    "comentario": r[3],
                    "fecha": r[4],
                }
                for r in resultados
            ]


def obtener_feedbacks_mensaje(id_mensaje: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT id_feedback, id_mensaje, puntuacion, comentario, fecha
            FROM feedback
            WHERE id_mensaje = %s
            ORDER BY fecha DESC
            """,
                (id_mensaje,),
            )
            resultados = cursor.fetchall()
            return [
                {
                    "id_feedback": r[0],
                    "id_mensaje": r[1],
                    "puntuacion": r[2],
                    "comentario": r[3],
                    "fecha": r[4],
                }
                for r in resultados
            ]
