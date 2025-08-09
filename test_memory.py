from memory_profiler import profile
from app.utils.search import VectorSearch

@profile
def test_load():
    vs = VectorSearch()
    print("Loaded VectorSearch")

test_load()