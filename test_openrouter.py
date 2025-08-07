from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)
completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[{"role": "user", "content": "What is the meaning of life?"}],
    extra_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "LLM Query Retrieval"
    },
    extra_body={}
)
print(completion.choices[0].message.content)