"""Abstract base class that every embedding model adapter implements."""

from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """Interface for an embedding model.

    Adapters return raw vectors only. Ordering and normalization are
    handled by EmbeddingService.
    """

    @abstractmethod
    def encode_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one raw vector per text, in the same order."""

    @abstractmethod
    def encode_query(self, text: str) -> list[float]:
        """Return one raw vector for a search phrase."""
