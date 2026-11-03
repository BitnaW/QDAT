"""Request and response models for the QDAT HTTP API."""

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class DocumentSummary(BaseModel):
    id: str
    filename: str
    character_count: int
    sentence_count: int


class DocumentDetail(DocumentSummary):
    text: str


class SearchHit(BaseModel):
    document_id: str
    filename: str
    text: str
    start_char: int
    end_char: int
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchHit]
