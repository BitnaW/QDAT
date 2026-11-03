"""HTTP API entry point for the QDAT backend."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.embedding import get_embedding_service
from app.parser import (
    EmptyDocumentError,
    UnsupportedFileTypeError,
    parse_document,
)
from app.schemas import (
    DocumentDetail,
    DocumentSummary,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from app.search import SentenceStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the embedding model and create the sentence store once at startup."""
    os.environ.setdefault("QDAT_EMBEDDING_MODEL", "minilm")
    app.state.embedding_service = get_embedding_service()
    app.state.store = SentenceStore()
    yield


app = FastAPI(title="QDAT Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Return a simple response used to verify the backend is running."""
    return {"status": "ok", "message": "QDAT backend is running"}


@app.post("/api/documents/parse")
async def parse_uploaded_document(file: UploadFile = File(...)) -> dict:
    """Load an uploaded document and return every sentence with its offsets.

    Supports .txt, .md, .pdf and .docx. Offsets point into the extracted
    text so results can later be linked back to their source location.
    """
    data = await file.read()
    filename = file.filename or "upload"
    try:
        text, sentences = parse_document(filename, data)
    except UnsupportedFileTypeError as err:
        raise HTTPException(status_code=415, detail=str(err)) from err
    except EmptyDocumentError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    return {
        "filename": filename,
        "character_count": len(text),
        "sentence_count": len(sentences),
        "sentences": [
            {
                "index": s.index,
                "text": s.text,
                "start_char": s.start_char,
                "end_char": s.end_char,
            }
            for s in sentences
        ],
    }


@app.post("/api/documents")
async def upload_document(
    request: Request, file: UploadFile = File(...)
) -> DocumentSummary:
    """Parse an uploaded document, embed its sentences, and store them."""
    data = await file.read()
    filename = file.filename or "upload"
    try:
        text, sentences = parse_document(filename, data)
    except UnsupportedFileTypeError as err:
        raise HTTPException(status_code=415, detail=str(err)) from err
    except EmptyDocumentError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    vectors = request.app.state.embedding_service.embed_text_units(
        [s.text for s in sentences]
    )
    document = request.app.state.store.add_document(filename, text, sentences, vectors)
    return DocumentSummary(
        id=document.id,
        filename=document.filename,
        character_count=len(text),
        sentence_count=len(sentences),
    )


@app.get("/api/documents")
def list_documents(request: Request) -> list[DocumentSummary]:
    """Return every uploaded document with its sentence count."""
    return [
        DocumentSummary(
            id=d.id,
            filename=d.filename,
            character_count=len(d.text),
            sentence_count=len(d.sentences),
        )
        for d in request.app.state.store.list_documents()
    ]


@app.get("/api/documents/{document_id}")
def get_document(request: Request, document_id: str) -> DocumentDetail:
    """Return the full text of one uploaded document."""
    document = request.app.state.store.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetail(
        id=document.id,
        filename=document.filename,
        character_count=len(document.text),
        sentence_count=len(document.sentences),
        text=document.text,
    )


@app.post("/api/search")
def search(request: Request, body: SearchRequest) -> SearchResponse:
    """Return the stored sentences most similar in meaning to the query."""
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query is empty")

    query_vector = request.app.state.embedding_service.embed_query(body.query)
    results = request.app.state.store.search(query_vector, body.top_k)
    return SearchResponse(
        query=body.query,
        results=[
            SearchHit(
                document_id=r.document_id,
                filename=r.filename,
                text=r.text,
                start_char=r.start_char,
                end_char=r.end_char,
                similarity=round(r.similarity, 3),
            )
            for r in results
        ],
    )
