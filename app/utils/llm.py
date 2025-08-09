from openai import OpenAI
from app.config import Config

class LLMProcessor:
    def __init__(self):
        self.client = OpenAI(
            base_url=Config.OPENROUTER_BASE_URL,
            api_key=Config.OPENROUTER_API_KEY
        )

    def parse_query(self, query: str, context: str) -> str:
        prompt = f"""
You are an expert in insurance policy analysis. Given the following context from a policy document and a user query, provide a precise and accurate answer. Ensure the response is clear, concise, and includes a rationale for the answer.

Context: {context}

Query: {query}

Answer:
"""
        try:
            completion = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "HTTP-Referer": Config.SITE_URL,
                    "X-Title": Config.SITE_NAME
                },
                extra_body={}
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM processing failed: {str(e)}")
