"""Document loading and sentence parsing for QDAT.

Everything here runs locally: no document text leaves the machine.

Each sentence keeps its character offsets into the extracted text
(`start_char` inclusive, `end_char` exclusive) so that embeddings, codes and
search results can be traced back to their source location. These names match
the `start_char` / `end_char` columns of the `document_chunks` table.
"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pysbd

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


class UnsupportedFileTypeError(ValueError):
    """Raised when an uploaded file has an extension we cannot read."""


class EmptyDocumentError(ValueError):
    """Raised when no text could be extracted from a document."""


@dataclass(frozen=True)
class Sentence:
    index: int  # position of the sentence in the document, starting at 0
    text: str
    start_char: int  # offset into the extracted text (inclusive)
    end_char: int  # offset into the extracted text (exclusive)


def extract_text(filename: str, data: bytes) -> str:
    """Return the plain text of an uploaded file based on its extension."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext or filename}'. Supported types: {allowed}"
        )

    if ext in {".txt", ".md"}:
        return data.decode("utf-8", errors="replace")

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)

    from docx import Document

    doc = Document(BytesIO(data))
    return "\n\n".join(p.text for p in doc.paragraphs)


def split_sentences(text: str) -> list[Sentence]:
    """Split text into sentences, keeping character offsets into `text`.

    Guarantee: for every sentence, text[start_char:end_char] == sentence.text.
    """
    segmenter = pysbd.Segmenter(language="en", clean=False, char_span=True)
    sentences: list[Sentence] = []
    for span in segmenter.segment(text):
        stripped = span.sent.strip()
        if not stripped:
            continue
        # Trim whitespace but keep offsets pointing at the real characters.
        start = span.start + (len(span.sent) - len(span.sent.lstrip()))
        sentences.append(
            Sentence(
                index=len(sentences),
                text=stripped,
                start_char=start,
                end_char=start + len(stripped),
            )
        )
    return sentences


def parse_document(filename: str, data: bytes) -> tuple[str, list[Sentence]]:
    """Load a document and return (full_text, sentences)."""
    text = extract_text(filename, data)
    if not text.strip():
        raise EmptyDocumentError(f"No readable text found in '{filename}'.")
    return text, split_sentences(text)
