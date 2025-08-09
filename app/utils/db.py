import psycopg2
import os

class Database:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not set")
        self.conn = psycopg2.connect(database_url)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                document_id TEXT,
                chunk_text TEXT,
                embedding DOUBLE PRECISION[]
            )
        """)
        self.conn.commit()

    def store_chunk(self, doc_id: str, chunk: str, embedding):
        self.cursor.execute(
            "INSERT INTO document_chunks (document_id, chunk_text, embedding) VALUES (%s, %s, %s)",
            (doc_id, chunk, list(map(float, embedding)))
        )
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

def get_db():
    return Database()
