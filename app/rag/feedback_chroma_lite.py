import sqlite3
import os


class FeedbackDBChromaLite:
    def __init__(self, db_path="feedback_chroma.db"):
        self.db_path = db_path
        self._crear_tabla()

    def _crear_tabla(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                rating INTEGER,
                comentario TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()

    def save_feedback(self, query, response, rating, comentario):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO feedback (query, response, rating, comentario)
            VALUES (?, ?, ?, ?)
        """,
            (query, response, rating, comentario),
        )

        conn.commit()
        feedback_id = cursor.lastrowid
        conn.close()

        return feedback_id

    def get_connection(self):
        return sqlite3.connect(self.db_path)
