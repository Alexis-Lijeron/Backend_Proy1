from app.core.db_connection import get_connection

def insertar_feedback(id_mensaje: int, puntuacion: int, comentario: str = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO feedback (id_mensaje, puntuacion, comentario)
            VALUES (%s, %s, %s)
            RETURNING id_feedback
            """, (id_mensaje, puntuacion, comentario))
            (id_feedback,) = cursor.fetchone()
            conn.commit()
            return id_feedback
