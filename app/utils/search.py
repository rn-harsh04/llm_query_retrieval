import time
import requests
from app.config import Config
from pinecone import Pinecone

HUGGINGFACE_API = "https://api-inference.huggingface.co/pipeline/feature-extraction"

class VectorSearch:
    def __init__(self):
        # Pinecone client
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY, timeout=30)
        self.index_name = Config.PINECONE_INDEX_NAME
        retries = 3
        for attempt in range(retries):
            try:
                indexes = self.pc.list_indexes().get("indexes", [])
                if self.index_name not in [i["name"] for i in indexes]:
                    # dimension 384 is typical for MiniLM; adjust if using different embedding model
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
                raise Exception(f"Pinecone init failed: {e}")

        # HF config
        self.hf_model = Config.HF_EMBEDDING_MODEL
        self.hf_key = Config.HF_API_KEY
        if not self.hf_key:
            raise ValueError("HF_API_KEY not set in environment")

    def _hf_embed(self, text: str):
        """Call Hugging Face inference pipeline feature-extraction endpoint to get embeddings."""
        url = f"{HUGGINGFACE_API}/{self.hf_model}"
        headers = {"Authorization": f"Bearer {self.hf_key}"}
        payload = {"inputs": text}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"HF embedding error: {resp.status_code} {resp.text}")
        emb = resp.json()
        # The HF pipeline returns a list (tokens) or a nested structure. Normalize to single vector:
        if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
            # average token vectors if needed
            try:
                # emb is list of token vectors -> average them
                vec = [sum(col) / len(col) for col in zip(*emb)]
                return vec
            except Exception:
                # fallback: if emb is a flat vector
                return emb[0]
        return emb  # assume it's already a vector

    def embed_text(self, text: str):
        return self._hf_embed(text)

    def index_document_stream(self, document_id: str, chunks: list, batch_size: int = 20):
        """Batch up vectors and upsert to Pinecone to avoid holding many vectors in RAM."""
        batch = []
        for i, chunk in enumerate(chunks):
            emb = self.embed_text(chunk)
            batch.append((f"{document_id}_{i}", emb, {"text": chunk}))
            if len(batch) >= batch_size:
                # Upsert expects numpy-like lists; ensure lists
                vectors = [(vid, list(map(float, vec)), meta) for vid, vec, meta in batch]
                self.index.upsert(vectors=vectors)
                batch.clear()
        if batch:
            vectors = [(vid, list(map(float, vec)), meta) for vid, vec, meta in batch]
            self.index.upsert(vectors=vectors)

    def search(self, query_embedding, top_k: int = 5):
        results = self.index.query(vector=list(map(float, query_embedding)), top_k=top_k, include_metadata=True)
        return [match["metadata"]["text"] for match in results["matches"]]
