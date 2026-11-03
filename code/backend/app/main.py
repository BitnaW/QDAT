"""HTTP API entry point for the QDAT backend."""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.parser import (
    EmptyDocumentError,
    UnsupportedFileTypeError,
    parse_document,
)

app = FastAPI(title="QDAT Backend", version="0.1.0")

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
