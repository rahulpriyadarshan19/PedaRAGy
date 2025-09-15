# backend/app/embeddings/embedding_model.py

from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load SentenceTransformer model at initialization
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = 512

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string and return its embedding as a list.
        """
        emb = self.model.encode([text], max_length=512)
        return emb[0].tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts and return list of embedding vectors.
        """
        embs = self.model.encode(texts, max_length=512)
        return [e.tolist() for e in embs]

# Example usage (for quick test)
if __name__ == "__main__":
    model = EmbeddingModel()
    example_texts = ["This is a test sentence.", "Document embedding is useful."]
    vectors = model.embed_texts(example_texts)
    print("Embeddings:", vectors)
