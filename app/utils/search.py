from pinecone import Pinecone
from app.config import Config
from sentence_transformers import SentenceTransformer
import time

# Load model globally to share memory across requests
model = SentenceTransformer(Config.EMBEDDING_MODEL)

class VectorSearch:
    def __init__(self):
        """Initializes Pinecone for semantic search."""
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
                raise Exception(f"Failed to connect to Pinecone after {retries} attempts: {str(e)}")
        self.model = model  # Use global model

    def index_document(self, document_id: str, chunks: list, embeddings: list):
        """Indexes document chunks with embeddings in Pinecone."""
        vectors = [(f"{document_id}_{i}", embedding.tolist(), {"text": chunk})
                   for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))]
        self.index.upsert(vectors=vectors)

    def search(self, query_embedding: list, top_k: int = 5) -> list:
        """Performs semantic search and returns matching text chunks."""
        results = self.index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True)
        return [match["metadata"]["text"] for match in results["matches"]]

    def embed_text(self, text: str) -> list:
        """Generates embeddings for a text string."""
        return self.model.encode(text, convert_to_numpy=True)