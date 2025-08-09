from pinecone import Pinecone
from app.config import Config
import time

_model = None

class VectorSearch:
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY, timeout=30)
        self.index_name = Config.PINECONE_INDEX_NAME
        retries = 3
        for attempt in range(retries):
            try:
                indexes = self.pc.list_indexes().get("indexes", [])
                if self.index_name not in [index["name"] for index in indexes]:
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=384,
                        metric="cosine",
                        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
                    )
                self.index = self.pc.Index(self.index_name)
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"Pinecone connection failed: {e}")

    def _get_model(self):
        global _model
        if _model is None:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(Config.EMBEDDING_MODEL)
        return _model

    def embed_text(self, text: str):
        model = self._get_model()
        return model.encode(text, convert_to_numpy=True)

    def index_document(self, document_id: str, chunks: list):
        """Stream embeddings in batches to save memory"""
        batch = []
        for i, chunk in enumerate(chunks):
            emb = self.embed_text(chunk)
            batch.append((f"{document_id}_{i}", emb.tolist(), {"text": chunk}))
            if len(batch) >= 20:
                self.index.upsert(vectors=batch)
                batch.clear()
        if batch:
            self.index.upsert(vectors=batch)

    def search(self, query_embedding, top_k=5):
        results = self.index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True)
        return [match["metadata"]["text"] for match in results["matches"]]
