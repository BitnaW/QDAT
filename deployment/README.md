# QDAT Deployment & Infrastructure

This directory contains containerization manifests and local deployment configurations for QDAT.

## Local Services

### 1. PostgreSQL with pgvector

QDAT relies on PostgreSQL with the `pgvector` extension for:
- Storing relational qualitative research metadata (projects, documents, codes, annotations)
- High-dimensional vector indexing (`vector(384)`) using HNSW for cosine distance similarity queries

#### Quick Start

To launch the database container:

```bash
docker compose -f deployment/docker-compose.yml up -d
```

#### Configuration Details

- **Image:** `pgvector/pgvector:pg16`
- **Port:** `5432`
- **Database Name:** `qdat_db`
- **Username:** `qdat_user`
- **Password:** `qdat_password`
- **Initialization:** Automatically mounts `code/backend/schema.sql` to `/docker-entrypoint-initdb.d/01_init.sql` on first boot.
- **Volume:** `qdat_pgdata` persists database state locally.

#### Stopping the Service

```bash
docker compose -f deployment/docker-compose.yml down
```
