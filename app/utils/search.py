import os
import requests

class VectorSearch:
    def __init__(self):
        self.hf_api_key = os.getenv("HF_API_KEY")
        self.model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        self.headers = {"Authorization": f"Bearer {self.hf_api_key}"}

    def embed(self, text: str):
        payload = {"inputs": text}
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=20)
        if response.status_code != 200:
            raise Exception(f"HF API error {response.status_code}: {response.text}")
        return response.json()
