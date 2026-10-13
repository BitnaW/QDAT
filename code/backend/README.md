# QDAT Backend

This is the Python backend for QDAT. It provides high-performance asynchronous REST endpoints backed by PostgreSQL and pgvector for on-device qualitative data analysis.

## Database Setup (PostgreSQL + pgvector)

QDAT uses PostgreSQL 16 with the `pgvector` extension for storing relational metadata, hierarchical codes, character coordinates, and 384-dimensional dense vector embeddings.

### Option 1: Run via Docker Compose (Recommended)

From the project root:

```bash
docker compose -f deployment/docker-compose.yml up -d
```

This starts PostgreSQL on port `5432` and automatically initializes the database tables and seed data using `code/backend/schema.sql`.

### Option 2: Apply to an Existing PostgreSQL Instance

If you are running PostgreSQL locally:

```bash
psql -U qdat_user -d qdat_db -f code/backend/schema.sql
```

Detailed database architecture and ERD diagrams can be found in [DATABASE_DESIGN.md](DATABASE_DESIGN.md).

---

## Running the Backend locally

Open a terminal or PowerShell in this folder:

```bash
cd code/backend
```

Create a virtual environment and activate it:

```bash
# On macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the packages:

```bash
python -m pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn app.main:app --reload
```

The backend will be running at <http://127.0.0.1:8000>.

---

## Test endpoint

Go to <http://127.0.0.1:8000/api/health> in a browser. If everything is working, it should return:

```json
{
  "status": "ok",
  "message": "QDAT backend is running"
}
```

FastAPI also provides interactive API documentation at <http://127.0.0.1:8000/docs>.