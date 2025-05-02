from app.core.db_connection import get_connection

def obtener_siguiente_contexto_numero(id_chat: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT COALESCE(MAX(contexto_numero), 0) + 1
            FROM contextos_chat
            WHERE id_chat = %s
            """, (id_chat,))
            (siguiente,) = cursor.fetchone()
            return siguiente

def crear_contexto(id_chat: int, descripcion: str = None) -> int:
    contexto_numero = obtener_siguiente_contexto_numero(id_chat)
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO contextos_chat (id_chat, contexto_numero, descripcion)
            VALUES (%s, %s, %s)
            RETURNING id_contexto
            """, (id_chat, contexto_numero, descripcion))
            (id_contexto,) = cursor.fetchone()
            conn.commit()
            return id_contexto
