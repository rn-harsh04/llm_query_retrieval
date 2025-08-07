def search_top_k(query, k=3):
    query_embedding = get_embedding(query)
    D, I = index.search(np.array([query_embedding]).astype("float32"), k)
    return [doc_chunks[i] for i in I[0]]
