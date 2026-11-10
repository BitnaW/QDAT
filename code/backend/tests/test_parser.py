from io import BytesIO

import pytest
from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app.parser import (
    EmptyDocumentError,
    UnsupportedFileTypeError,
    parse_document,
    split_sentences,
)

client = TestClient(app)

SAMPLE = (
    "I felt supported by my neighbors. Dr. Smith said the roads were bad! "
    "Did anyone fix them? Nobody did."
)


def make_pdf(text: str) -> bytes:
    """Build a minimal one-page PDF containing `text` (no extra dependencies)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (
        len(objects) + 1,
        xref,
    )
    return out


def test_split_sentences_handles_abbreviations_and_punctuation():
    sentences = split_sentences(SAMPLE)
    assert [s.text for s in sentences] == [
        "I felt supported by my neighbors.",
        "Dr. Smith said the roads were bad!",
        "Did anyone fix them?",
        "Nobody did.",
    ]
    assert [s.index for s in sentences] == [0, 1, 2, 3]


def test_offsets_point_back_into_source_text():
    for s in split_sentences(SAMPLE):
        assert SAMPLE[s.start_char : s.end_char] == s.text


def test_offsets_survive_newlines_and_leading_whitespace():
    text = "  First one here.\n\n   Second one here.\nThird one here."
    sentences = split_sentences(text)
    assert len(sentences) == 3
    for s in sentences:
        assert text[s.start_char : s.end_char] == s.text


def test_txt_and_docx_loading():
    _, from_txt = parse_document("a.txt", SAMPLE.encode())
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("First point here. Second point here.")
    doc.save(buf)
    _, from_docx = parse_document("a.docx", buf.getvalue())
    assert len(from_txt) == 4
    assert len(from_docx) == 2


def test_pdf_loading():
    text, sentences = parse_document("a.pdf", make_pdf("First point here. Second point here."))
    assert "First point here." in text
    assert len(sentences) == 2
    for s in sentences:
        assert text[s.start_char : s.end_char] == s.text


def test_rejects_unsupported_and_empty():
    with pytest.raises(UnsupportedFileTypeError):
        parse_document("a.exe", b"x")
    with pytest.raises(EmptyDocumentError):
        parse_document("a.txt", b"   \n ")


def test_endpoint_success_and_errors():
    ok = client.post("/api/documents/parse", files={"file": ("t.txt", SAMPLE.encode())})
    assert ok.status_code == 200
    body = ok.json()
    assert body["sentence_count"] == 4
    first = body["sentences"][0]
    assert set(first) == {"index", "text", "start_char", "end_char"}
    assert first["start_char"] == 0

    assert client.post("/api/documents/parse", files={"file": ("t.exe", b"x")}).status_code == 415
    assert client.post("/api/documents/parse", files={"file": ("t.txt", b"")}).status_code == 422
