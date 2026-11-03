"""In-memory store of embedded sentences. Nothing is saved between runs."""

import uuid
from dataclasses import dataclass

from app.parser import Sentence


@dataclass(frozen=True)
class StoredDocument:
    """An uploaded document and its sentences."""

    id: str
    filename: str
    text: str
    sentences: list[Sentence]


@dataclass(frozen=True)
class SearchResult:
    """A stored sentence that matched a search, with its similarity score."""

    document_id: str
    filename: str
    text: str
    start_char: int
    end_char: int
    similarity: float


class SentenceStore:
    """Holds embedded sentences and finds the ones closest to a query vector."""

    def __init__(self) -> None:
        self._documents: dict[str, StoredDocument] = {}
        self._vectors: dict[str, list[list[float]]] = {}

    def add_document(
        self,
        filename: str,
        text: str,
        sentences: list[Sentence],
        vectors: list[list[float]],
    ) -> StoredDocument:
        """Store a document with one vector per sentence, in order."""
        if len(sentences) != len(vectors):
            raise ValueError("Each sentence needs exactly one vector")
        document = StoredDocument(uuid.uuid4().hex, filename, text, sentences)
        self._documents[document.id] = document
        self._vectors[document.id] = vectors
        return document

    def list_documents(self) -> list[StoredDocument]:
        """Return every stored document in upload order."""
        return list(self._documents.values())

    def get_document(self, document_id: str) -> StoredDocument | None:
        """Return one document, or None if the id is unknown."""
        return self._documents.get(document_id)

    def search(self, query_vector: list[float], top_k: int) -> list[SearchResult]:
        """Return the top_k sentences most similar to the query vector.

        Vectors are length 1, so the dot product equals cosine similarity.
        """
        scored: list[SearchResult] = []
        for document in self._documents.values():
            vectors = self._vectors[document.id]
            for sentence, vector in zip(document.sentences, vectors):
                similarity = sum(a * b for a, b in zip(query_vector, vector))
                scored.append(
                    SearchResult(
                        document.id,
                        document.filename,
                        sentence.text,
                        sentence.start_char,
                        sentence.end_char,
                        similarity,
                    )
                )
        scored.sort(key=lambda result: result.similarity, reverse=True)
        return scored[:top_k]
