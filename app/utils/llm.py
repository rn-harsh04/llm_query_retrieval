def query_llm(query, context):
    prompt = f"""You are a helpful assistant. Based on the policy document below, answer the user's question.
Context:
{context}

Question: {query}
Provide a concise and accurate answer with explanation."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message["content"]
