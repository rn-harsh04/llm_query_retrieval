def format_to_json(query, answer):
    return {
        "query": query,
        "answer": answer,
        "explanation": "Based on semantic match and context",
    }
