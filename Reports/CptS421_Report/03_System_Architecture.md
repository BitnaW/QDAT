# System Architecture

## 1. System Overview

The Qualitative Data Analysis Tool (QDAT) is designed as a secure, local-first, containerized architecture that runs entirely on client workstations without transmitting sensitive human-subjects data to external cloud services.

```
+-----------------------------------------------------------------------+
|                         PRESENTATION LAYER                            |
|             React + Tailwind CSS (Vite / Node 20+)                    |
|  - Document Reader & Highlighting Pane (Coordinate-based marks)       |
|  - Hierarchical Codebook Tree Manager                                 |
|  - Semantic Search & Cluster Exploration Panel                        |
+-----------------------------------+-----------------------------------+
                                    | REST APIs (HTTP / JSON)
+-----------------------------------v-----------------------------------+
|                           APPLICATION LAYER                           |
|                      Python 3.11+ / FastAPI                           |
|  - Ingestion & Text Parser (TXT, DOCX, PDF)                           |
|  - Chunking Engine (Sliding coordinate window)                        |
|  - Semantic Search & Distance Ranking Service                         |
|  - Clustering Pipeline (HDBSCAN / k-means)                            |
+------------------+--------------------------------+-------------------+
                   |                                | Local Inference
+------------------v--------------+  +--------------v-------------------+
|         PERSISTENCE LAYER       |  |       LOCAL NLP / LLM RUNNER     |
|   PostgreSQL 16 + pgvector      |  |  Sentence-Transformers (MiniLM)  |
|  - Relational Data Modeling     |  |  Ollama / llama.cpp (Llama 3 8B) |
|  - HNSW Vector Cosine Indexing  |  |  100% Offline / No Telemetry     |
+---------------------------------+  +----------------------------------+
```

## 2. Key Architectural Subsystems

1. **Presentation Layer (Frontend):**
   - Built with React and Tailwind CSS.
   - Provides a synchronized multi-pane workspace with real-time coordinate-based text highlights.

2. **Application Layer (FastAPI Backend):**
   - High-performance asynchronous REST endpoints.
   - Coordinates file ingestion, text chunking, and database interactions.

3. **Storage & Persistence Layer (PostgreSQL + pgvector):**
   - Relational tables for projects, documents, codes, and annotations.
   - Vector column `embedding vector(384)` with HNSW indexing for sub-second semantic similarity searches.

4. **Inference & NLP Pipeline:**
   - Local sentence-transformers generating 384-dimensional dense vectors.
   - Local LLM engine (Ollama) providing grounded summaries and code suggestions.
