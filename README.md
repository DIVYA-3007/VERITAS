# VERITAS

### From documents to trusted knowledge.

**VERITAS** is a document intelligence platform designed to transform digital and scanned PDF documents into searchable knowledge and provide evidence-grounded answers using Retrieval-Augmented Generation (RAG).

The project combines document extraction, Optical Character Recognition (OCR), semantic search, vector embeddings, and Large Language Models (LLMs) to make information retrieval more reliable and transparent.

## Project Overview

Finding specific information in lengthy documents can be time-consuming. VERITAS aims to simplify this process by allowing users to upload PDF documents, search their contents semantically, and ask questions using natural language.

The platform retrieves relevant document passages and uses them as evidence when generating answers. When sufficient supporting evidence is unavailable, it can abstain rather than inventing an answer.

## Current Features

- **PDF Document Upload:** Upload and process PDF documents.
- **Native Text Extraction:** Extract text from digitally generated PDFs using PyMuPDF.
- **OCR Processing:** Extract text from scanned PDF pages using EasyOCR.
- **Semantic Chunking:** Divide extracted content into overlapping chunks.
- **Vector Embeddings:** Generate semantic embeddings using Sentence Transformers.
- **Vector Search:** Retrieve relevant document passages using PostgreSQL and pgvector.
- **RAG Question Answering:** Generate answers using retrieved document evidence and Ollama.
- **Evidence References:** Return relevant source documents and page references.
- **Evidence-Based Abstention:** Avoid answering when sufficient supporting evidence is unavailable.
- **Web Dashboard:** React-based interface for document management, search, and question answering.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL 18 |
| Vector Search | pgvector |
| PDF Processing | PyMuPDF |
| OCR | EasyOCR |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM Runtime | Ollama |
| Language Model | llama3.2 |
| API Testing | FastAPI Swagger UI |

## System Architecture

```text
              User
               |
               v
       React Web Dashboard
               |
               v
          FastAPI Backend
               |
       +-------+--------+
       |                |
       v                v
 Document Processing  Question Answering
       |                |
       v                v
 PDF Text Extraction  Semantic Retrieval
       |                |
       v                v
 OCR Fallback       PostgreSQL + pgvector
       |                |
       v                v
 Text Chunking       Relevant Evidence
       |                |
       v                v
 Sentence Transformers + Ollama
               |
               v
       Evidence-Grounded Answer
               |
               v
       Source and Page References
```

## Project Structure

```text
VERITAS/
│
├── ai_engine/
├── backend/
│   └── app/
│       ├── main.py
│       ├── services/
│       └── ...
│
├── database/
├── documentation/
├── frontend/
├── research/
├── storage/
├── tests/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

Install the following before running VERITAS:

- Python 3.12
- Node.js and npm
- PostgreSQL with the pgvector extension
- Ollama

### 1. Clone the Repository

```bash
git clone https://github.com/DIVYA-3007/VERITAS.git
cd VERITAS
```

### 2. Backend Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration

Create your local `.env` file using `.env.example` as a reference.

Configure your PostgreSQL connection and other required settings.

**Important:** Never commit your `.env` file or expose database credentials.

### 4. Database Setup

Create a PostgreSQL database named `veritas_db` and enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Ensure the database connection details match your `.env` configuration.

### 5. Configure Ollama

Install Ollama and download the required model:

```bash
ollama pull llama3.2
```

Ensure Ollama is running before using question answering.

### 6. Run the Backend

From the project root:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Run the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/v1/documents/upload` | Upload a PDF document |
| GET | `/api/v1/documents/` | List uploaded documents |
| GET | `/api/v1/documents/{document_id}` | Retrieve document details |
| POST | `/api/v1/search/` | Perform semantic document search |
| POST | `/api/v1/qa/` | Ask questions about document content |

## Current Development Status

VERITAS currently has a working PDF document processing and evidence-grounded question-answering MVP.

Implemented and tested capabilities include:

- Native PDF text extraction.
- OCR-based scanned PDF processing.
- Document ingestion and storage.
- Semantic vector search.
- RAG-based question answering.
- Source and page references.
- Abstention when relevant evidence is unavailable.
- React frontend production build and lint checks.

## Current Scope and Limitations

The current MVP focuses on PDF text extraction, scanned-page OCR, semantic retrieval, and evidence-grounded question answering.

Advanced visual understanding, complex table extraction, audio/video processing, multi-document comparison, and model fine-tuning are not currently part of the implemented MVP.

These capabilities may be explored in future development.

## Future Enhancements

- Improved table and layout extraction.
- Advanced visual document understanding.
- Multi-document question answering and comparison.
- More detailed evidence and citation verification.
- Improved retrieval evaluation and benchmarking.
- User authentication and document access management.
- Production deployment and monitoring.

## Project Vision

The long-term vision of VERITAS is to build a reliable document intelligence system that connects information extraction, semantic retrieval, and evidence-grounded reasoning into one unified platform.

**VERITAS — From documents to trusted knowledge.**