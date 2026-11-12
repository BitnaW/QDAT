# Qualitative Data Analysis Tool (QDAT)

## Project summary

### One sentence description of the project

QDAT is a local, privacy focused tool that helps researchers organize, search, and code qualitative documents by meaning, without sending their data to any outside service.

### Additional information about the project

QDAT is being built for the Washington State University Division of Governmental Studies and Services (DGSS).

Researchers often have to read through large piles of survey responses, interview transcripts, and discussion notes to find recurring ideas and themes. Doing that by hand takes a long time, and general purpose AI tools can put sensitive data at risk or make it hard to see where an answer came from. QDAT runs entirely on the researcher's own computer. It breaks documents into passages, turns each passage into an embedding that represents its meaning, and lets the researcher search for related passages even when the exact words differ. Every result links back to its original document and text location.

Project goals

* **Secure data processing.** Keep research data local and never send document contents to external services.
* **Automated coding.** Group related passages and suggest codes using machine learning.
* **Document management.** Upload and organize multiple documents in a project.
* **Semantic search.** Find passages by meaning instead of exact keywords.
* **Source traceability.** Link codes and search results back to the original text.
* **Code management.** Review, rename, merge, split, and organize codes.
* **Research summaries.** Show recurring themes across documents.
* **Usability.** An interface modeled on NVivo so researchers can pick it up quickly.

Current status (Sprint 2)

* Document parsing for .txt, .md, .pdf, and .docx files, with the start and end position of every text segment
* Local storage of text segments and embeddings in PostgreSQL with pgvector
* Semantic search over uploaded documents, demoed to the clients on November 3
* NVivo style interface with Dashboard, Documents, Codebook, and Search pages

Planned features that are not built yet include automatic code suggestions, clustering, code merging and splitting, and document summaries.

## Installation

### Prerequisites

Install these before starting.

* Git
* Python 3.10 or newer
* Node.js 18 or newer, which includes npm
* PostgreSQL 14 or newer with the pgvector extension available

### Add-ons

* **FastAPI and Uvicorn** run the backend API.
* **React, React Router, Vite, and Tailwind CSS** make up the frontend.
* **PostgreSQL with pgvector** stores text segments and embeddings so similarity search runs locally.
* **The all-MiniLM-L6-v2 embedding model** turns text into embeddings on the researcher's own machine.
* **The document parsing libraries listed in requirements.txt** read .txt, .md, .pdf, and .docx files.
* **pytest** runs the backend tests.

### Installation Steps

Clone the Sprint 2 branch of the repository.

```bash
git clone -b BRANCH_NAME https://github.com/BitnaW/QDAT.git
cd QDAT
```

Create the database and turn on the vector extension.

```bash
createdb qdat
psql qdat -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Set up and start the backend on macOS or Linux.

```bash
cd code/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

On Windows PowerShell, activate the environment with `.\.venv\Scripts\Activate.ps1` instead of the `source` line.

The first time the embedding service runs, it downloads the all-MiniLM-L6-v2 model, so that first run needs an internet connection. After that, everything runs locally.

Set up and start the frontend in a second terminal.

```bash
cd code/frontend
npm install
npm run dev
```

Open the address Vite prints, usually http://localhost:5173. The backend runs at http://127.0.0.1:8000, and http://127.0.0.1:8000/api/health should return a status of ok. Automatic API documentation is at http://127.0.0.1:8000/docs.

To run the backend tests, open a terminal in the backend folder with the virtual environment still activated and make sure PostgreSQL is running.

```bash
cd code/backend
pytest
```

## Functionality

This walkthrough follows the Sprint 2 branch.

1. **Dashboard.** The landing page of the application.
2. **Documents.** Upload a .txt, .md, .pdf, or .docx file. The backend splits it into segments, records where each segment starts and ends in the original text, and stores the segments and their embeddings locally.
3. **Search.** Type a word or phrase. QDAT returns passages with similar meaning, ranked by a similarity score, even when they do not share the same words.
4. **Codebook.** This page is a layout for now. Creating and managing codes is planned for Sprint 3.

## Known Problems

* Automatic coding, clustering, and code management are not implemented yet, and the Codebook page does not create codes.
* The clients asked on November 3 for document summaries, manual coding from the search page, a button that jumps to a result's location in its document, removing results, and similarity range filters. These are planned for Sprint 3.
* The first run needs an internet connection to download the embedding model.


## Additional Documentation

* Sprint reports
  * [Sprint 1 report](Sprints/Sprint_1/Sprint_Report/Sprint1_Report.md)
  * [Sprint 2 report](Sprints/Sprint_2/Sprint_Report/Sprint2_Report.md)
* Meeting minutes
  * [Sprint 1 minutes](Sprints/Sprint_1/MoM/)
  * [Sprint 2 minutes](Sprints/Sprint_2/MoM/)
* Sprint 2 demo video and slides
  * [Video link](Sprints/Sprint_2/Video/Sprint2_Demo.md)
  * [Slides](Sprints/Sprint_2/PPT/)
* [Backend notes](code/backend/README.md) and [API documentation](code/backend/API_Documentation.md)
* [Frontend notes](code/frontend/README.md) and [UI design](code/frontend/UI_Design.md)
* [System architecture](Reports/CptS421_Report/03_System_Architecture.md) and [database design](Reports/CptS421_Report/04_Design_Specification.md)
* [Test strategy](testing/test_strategy.md)

## License

This project uses the MIT license. See the `LICENSE` file.
