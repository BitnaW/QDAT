# QDAT REST API Documentation

This document specifies the integration contracts between the React frontend and the FastAPI backend, backed by the PostgreSQL + pgvector database schema.

---

## 1. System Health

### `GET /api/health`
Check backend server status.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "message": "QDAT backend is running"
}
```

---

## 2. Projects API

### `POST /api/projects`
Create a new qualitative research workspace.
- **Request Body**:
```json
{
  "name": "Rural Community Infrastructure Study 2026",
  "description": "DGSS qualitative evaluation of focus group transcripts."
}
```
- **Response `201 Created`**:
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "name": "Rural Community Infrastructure Study 2026",
  "description": "DGSS qualitative evaluation of focus group transcripts.",
  "created_at": "2026-10-12T20:00:00Z",
  "updated_at": "2026-10-12T20:00:00Z"
}
```

### `GET /api/projects`
List all active projects.
- **Response `200 OK`**: Array of project objects.

---

## 3. Documents & Source Ingestion API

### `POST /api/projects/{project_id}/documents`
Upload and process a qualitative document (TXT, DOCX, PDF). Backend parses text, computes character length, chunks the text into overlapping coordinate windows, and generates local vector embeddings.
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file`: Binary file
  - `metadata`: Optional JSON string (e.g. `{"session": "A", "interviewer": "Season Hoard"}`)
- **Response `201 Created`**:
```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "project_id": "11111111-1111-1111-1111-111111111111",
  "filename": "Focus_Group_Session_A.txt",
  "file_type": "txt",
  "file_size_bytes": 104200,
  "char_count": 25430,
  "chunk_count": 42,
  "created_at": "2026-10-12T20:05:00Z"
}
```

### `GET /api/documents/{document_id}`
Retrieve raw document text along with attached annotations for synchronized text highlighting in the frontend Document Reader.
- **Response `200 OK`**:
```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "filename": "Focus_Group_Session_A.txt",
  "raw_content": "Participant 1: Our local broadband access has been...",
  "char_count": 25430,
  "annotations": [
    {
      "id": "55555555-5555-5555-5555-555555555551",
      "code_id": "44444444-4444-4444-4444-444444444442",
      "code_name": "Broadband & Fiber Hurdles",
      "code_color": "#F97316",
      "start_char": 15,
      "end_char": 156,
      "selected_text": "Our local broadband access has been completely unreliable...",
      "confidence_score": 1.0,
      "is_verified": true
    }
  ]
}
```

---

## 4. Hierarchical Codebook API

### `GET /api/projects/{project_id}/codes`
Retrieve the hierarchical codebook tree.
- **Response `200 OK`**:
```json
[
  {
    "id": "44444444-4444-4444-4444-444444444441",
    "parent_id": null,
    "name": "Infrastructure Barriers",
    "description": "Physical, contractual, or technical obstacles.",
    "color": "#EF4444",
    "children": [
      {
        "id": "44444444-4444-4444-4444-444444444442",
        "parent_id": "44444444-4444-4444-4444-444444444441",
        "name": "Broadband & Fiber Hurdles",
        "description": "Specific delays or outages.",
        "color": "#F97316",
        "children": []
      }
    ]
  }
]
```

### `POST /api/projects/{project_id}/codes`
Create a new code or sub-code.
- **Request Body**:
```json
{
  "parent_id": "44444444-4444-4444-4444-444444444441",
  "name": "Power Grid Reliability",
  "description": "Electrical transformer outages.",
  "color": "#EAB308"
}
```

---

## 5. Annotations & Source Traceability API

### `POST /api/annotations`
Create an annotation linking a qualitative code to an exact coordinate span in a document.
- **Request Body**:
```json
{
  "document_id": "22222222-2222-2222-2222-222222222222",
  "chunk_id": "33333333-3333-3333-3333-333333333331",
  "code_id": "44444444-4444-4444-4444-444444444442",
  "start_char": 15,
  "end_char": 156,
  "selected_text": "Our local broadband access has been completely unreliable for the past two years.",
  "confidence_score": 1.0,
  "is_ai_suggested": false,
  "notes": "Direct quote regarding broadband failure."
}
```

---

## 6. Semantic Vector Search API

### `POST /api/projects/{project_id}/search`
Search document chunks semantically using dense vector cosine distance (`<=>` operator in pgvector).
- **Request Body**:
```json
{
  "query": "fiber installation delays and contractor disputes",
  "top_k": 5,
  "threshold": 0.75
}
```
- **Response `200 OK`**:
```json
{
  "query": "fiber installation delays and contractor disputes",
  "results": [
    {
      "chunk_id": "33333333-3333-3333-3333-333333333331",
      "document_id": "22222222-2222-2222-2222-222222222222",
      "document_name": "Focus_Group_Session_A.txt",
      "start_char": 0,
      "end_char": 157,
      "chunk_text": "Participant 1: Our local broadband access has been completely unreliable for the past two years. The fiber installation was halted due to contractor disputes.",
      "similarity_score": 0.884,
      "assigned_codes": ["Broadband & Fiber Hurdles"]
    }
  ]
}
```
