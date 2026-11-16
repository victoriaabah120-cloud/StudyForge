import numpy as np
from sentence_transformers import SentenceTransformer

_model = None

# Temporary in-memory storage: document_id -> filename, chunks, embeddings.
# It is cleared whenever the server restarts. We'll move it to Supabase later.
DOCUMENTS = {}


def get_model():
    """Load the embedding model once, the first time it is needed."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into pieces of about chunk_size characters.

    Each chunk repeats the last `overlap` characters of the previous one,
    so a sentence cut at the edge still appears whole in one chunk.
    """
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step

    return chunks


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of texts into a list of number-vectors."""
    return get_model().encode(texts, normalize_embeddings=True)


def add_document(doc_id: str, filename: str, chunks: list[str]) -> None:
    """Embed all chunks and keep them in memory under doc_id."""
    DOCUMENTS[doc_id] = {
        "filename": filename,
        "chunks": chunks,
        "embeddings": embed_texts(chunks),
    }


def search(doc_id: str, question: str, top_k: int = 3):
    """Return the top_k chunks most similar to the question, or None if doc_id is unknown."""
    doc = DOCUMENTS.get(doc_id)
    if doc is None:
        return None

    question_vector = embed_texts([question])[0]
    scores = doc["embeddings"] @ question_vector
    best = np.argsort(scores)[::-1][:top_k]

    return [
        {"chunk": doc["chunks"][i], "score": round(float(scores[i]), 3)}
        for i in best
    ]