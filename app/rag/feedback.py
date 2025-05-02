from app.core.db_connection import get_connection
from typing import List, Dict, Any, Optional

class FeedbackDBPostgres:
    def save_feedback(self, id_mensaje: int, puntuacion: int, comentario: Optional[str] = None) -> int:
        """Guardar feedback vinculado a un mensaje"""
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

    def get_feedback_by_mensaje(self, id_mensaje: int) -> List[Dict[str, Any]]:
        """Obtener todos los feedbacks de un mensaje"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT id_feedback, puntuacion, comentario, fecha
                FROM feedback
                WHERE id_mensaje = %s
                ORDER BY fecha DESC
                """, (id_mensaje,))
                rows = cursor.fetchall()
                return [
                    {
                        "id_feedback": row[0],
                        "puntuacion": row[1],
                        "comentario": row[2],
                        "fecha": row[3].isoformat() if row[3] else None
                    }
                    for row in rows
                ]

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas globales de feedback"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM feedback")
                total = cursor.fetchone()[0]

                cursor.execute("SELECT AVG(puntuacion) FROM feedback")
                avg_rating = cursor.fetchone()[0] or 0

                cursor.execute("""
                    SELECT puntuacion, COUNT(*) 
                    FROM feedback 
                    GROUP BY puntuacion
                    ORDER BY puntuacion DESC
                """)
                dist = cursor.fetchall()
                rating_distribution = {p: c for p, c in dist}

                return {
                    "total_feedback": total,
                    "average_rating": round(avg_rating, 2),
                    "rating_distribution": rating_distribution
                }
