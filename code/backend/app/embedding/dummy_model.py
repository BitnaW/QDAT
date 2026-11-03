"""Dummy embedding model used to check that the service calls an adapter."""

from app.embedding.model import EmbeddingModel


class DummyEmbeddingModel(EmbeddingModel):
    """Prints which method was called and returns fixed vectors."""

    def encode_text_units(self, texts: list[str]) -> list[list[float]]:
        print(f"DummyEmbeddingModel.encode_text_units called with {len(texts)} text(s)")
        return [[3.0, 4.0] for _ in texts]

    def encode_query(self, text: str) -> list[float]:
        print(f"DummyEmbeddingModel.encode_query called with {text!r}")
        return [0.0, 2.0]
