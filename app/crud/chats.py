from app.core.db_connection import get_connection

def crear_chat(id_usuario: int, titulo: str = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO chats (id_usuario, titulo)
            VALUES (%s, %s)
            RETURNING id_chat
            """, (id_usuario, titulo))
            (id_chat,) = cursor.fetchone()
            conn.commit()
            return id_chat
