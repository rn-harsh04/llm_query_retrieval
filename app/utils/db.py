import psycopg2
import os
from app.config import Config

class Database:
    def __init__(self):
        # Use DATABASE_URL from Render environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        self.conn = psycopg2.connect(database_url)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                document_id TEXT,
                chunk_text TEXT,
                embedding VECTOR(384)
            )
        """)
        self.conn.commit()

    def store_chunks(self, document_id: str, chunks: list, embeddings: list):
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.cursor.execute(
                "INSERT INTO document_chunks (document_id, chunk_text, embedding) VALUES (%s, %s, %s)",
                (f"{document_id}_{i}", chunk, embedding.tolist())
            )
        self.conn.commit()

    def get_chunks(self, document_id: str):
        self.cursor.execute("SELECT chunk_text FROM document_chunks WHERE document_id LIKE %s", (f"{document_id}%",))
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        self.cursor.close()
        self.conn.close()

db = Database()