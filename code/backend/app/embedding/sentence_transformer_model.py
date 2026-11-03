"""Embedding model adapter backed by the sentence-transformers library."""

from app.embedding.model import EmbeddingModel

MODEL_NAME = "all-MiniLM-L6-v2"


class SentenceTransformerModel(EmbeddingModel):
    """Embeds text with a pre-trained sentence-transformers model."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        # Imported here so the library only loads when this adapter is used.
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def encode_text_units(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()

    def encode_query(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()
