# QDAT Backend

This is the Python backend for QDAT. Right now it just has a basic FastAPI
server and a test endpoint, but more features are planned.

## Running it locally

Open PowerShell in this folder:

```powershell
cd code/backend
```

Create a virtual environment and activate it:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the packages:

```powershell
python -m pip install -r requirements.txt
```

Start the server:

```powershell
python -m uvicorn app.main:app --reload
```

If PowerShell blocks `Activate.ps1`, you can use the virtual environment
without activating it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The backend should now be running at <http://127.0.0.1:8000>.

## Test endpoint

Go to <http://127.0.0.1:8000/api/health> in a browser. If everything is
working, it should return:

```json
{
  "status": "ok",
  "message": "QDAT backend is running"
}
```

FastAPI also provides automatic API documentation at
<http://127.0.0.1:8000/docs>.

If PowerShell does not allow the virtual environment activation command, run
this once and then try activating it again

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Document parsing endpoint

`POST /api/documents/parse` accepts a file upload (`.txt`, `.md`, `.pdf`,
`.docx`) and returns every sentence with its position in the extracted text.
The field names match the `document_chunks` table:

```json
{
  "filename": "interview1.txt",
  "character_count": 82,
  "sentence_count": 2,
  "sentences": [
    { "index": 0, "text": "I felt supported.", "start_char": 0, "end_char": 17 }
  ]
}
```

`text[start_char:end_char]` is always exactly the sentence text. Unsupported
file types return 415 and empty documents return 422. Parsing runs entirely
locally.

## Running the tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

`tests/test_embedding_service.py` is a manual script that downloads the real
MiniLM model, so `pytest` skips it. Run it with
`python -m tests.test_embedding_service`.

