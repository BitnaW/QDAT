"""Service the rest of the backend uses to turn text into vectors."""

import math
import os

from app.embedding.model import EmbeddingModel

# Maps a model name to its adapter class. Register new adapters here.
MODEL_REGISTRY: dict[str, type[EmbeddingModel]] = {}


def _normalize(vector: list[float]) -> list[float]:
    """Scale a vector to length 1."""
    length = math.sqrt(sum(x * x for x in vector))
    if length == 0:
        return vector
    return [x / length for x in vector]


class EmbeddingService:
    """Wraps an EmbeddingModel and applies the rules shared by all models."""

    def __init__(self, model: EmbeddingModel) -> None:
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one length-1 vector per text, in input order."""
        if not texts:
            return []
        return [_normalize(v) for v in self._model.encode_documents(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Return a length-1 vector for a search phrase."""
        return _normalize(self._model.encode_query(text))


def get_embedding_service() -> EmbeddingService:
    """Build an EmbeddingService from the QDAT_EMBEDDING_MODEL setting."""
    name = os.environ.get("QDAT_EMBEDDING_MODEL", "")
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown embedding model: {name!r}")
    return EmbeddingService(MODEL_REGISTRY[name]())
