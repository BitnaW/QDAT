"""Embedding model abstraction and service."""

from app.embedding.model import EmbeddingModel
from app.embedding.service import EmbeddingService, get_embedding_service

__all__ = ["EmbeddingModel", "EmbeddingService", "get_embedding_service"]
