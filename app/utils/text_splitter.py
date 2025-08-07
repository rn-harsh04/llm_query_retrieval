from typing import List

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """Splits text into chunks with specified size and overlap."""
    if not text:
        return []
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks