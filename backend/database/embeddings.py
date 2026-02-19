"""Generate ko-sbert-nli text embeddings and store them in SQLite as pickled BLOBs."""
import sqlite3
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from database import get_connection

MODEL_NAME = "jhgan/ko-sbert-nli"

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_text_embedding(text: str) -> bytes:
    """Generate embedding for a single text query, return pickled bytes."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    vector_np = np.array(vector, dtype=np.float32)
    return pickle.dumps(vector_np)


def generate_embeddings() -> None:
    """Generate 768-dim ko-sbert embeddings for all products."""
    model = _get_model()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()

    print(f"Generating embeddings for {len(products)} products (model: {MODEL_NAME})")

    for p_id, p_name in products:
        vector = model.encode(p_name, normalize_embeddings=True)
        vector_np = np.array(vector, dtype=np.float32)
        blob = sqlite3.Binary(pickle.dumps(vector_np))
        cursor.execute(
            "INSERT OR REPLACE INTO product_embeddings "
            "(product_id, text_embedding) VALUES (?, ?)",
            (p_id, blob),
        )
        if p_id % 50 == 0:
            print(f"  Processed {p_id} products")
            conn.commit()

    conn.commit()
    conn.close()
    print("[OK] Embedding generation completed")


if __name__ == "__main__":
    generate_embeddings()
