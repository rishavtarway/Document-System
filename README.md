# AI-Powered Document Intelligence System

An intelligent, self-improving document processing system that automatically classifies, extracts, validates, and learns from user feedback. Handles any document type — known or unknown.

## System Architecture

```
┌──────────────┐    ┌──────────────────────────────────────────────────────┐    ┌──────────────┐
│   Frontend   │    │                   Backend (FastAPI)                  │    │  PostgreSQL  │
│  (React/TS)  │───▶│                                                    │───▶│   + pgvector │
└──────────────┘    │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │    │              │
                    │  │Upload    │─▶│  Document    │─▶│  Intelligent │  │    │  Documents   │
                    │  │Endpoint  │  │  Classifier  │  │  Extractor   │  │    │  Extractions │
                    │  └──────────┘  │  (AI + regex)│  │  (AI + vec)  │  │    │  MCQ Dialogs │
                    │                └──────────────┘  └──────┬───────┘  │    │  Schemas     │
                    │                                         │          │    │  Patterns    │
                    │                ┌──────────────┐  ┌──────▼───────┐  │    │  Corrections │
                    │                │   MCQ Gen    │  │  Validation  │  │    └──────────────┘
                    │                │  (low conf)  │  │ (determin.)  │  │
                    │                └──────┬───────┘  └──────┬───────┘  │    ┌──────────────┐
                    │                       │                 │          │    │    Redis     │
                    │                ┌──────▼─────────────────▼───────┐  │───▶│              │
                    │                │    Learning Service           │  │    │  Cache +     │
                    │                │    (vector store + pattern)   │  │    │  Celery      │
                    │                └──────────────────────────────┘  │    └──────────────┘
                    │                                                   │
                    │  ┌─────────────────────────────────────────────┐  │    ┌──────────────┐
                    │  │          Celery Worker (async)              │  │    │    MinIO     │
                    │  │  OCR · PDF · Image · Long-running tasks     │  │───▶│              │
                    │  └─────────────────────────────────────────────┘  │    │ Doc Storage  │
                    └──────────────────────────────────────────────────────┘    └──────────────┘
```

## Key Features

- **Multi-document support** — Invoices, POs, Contracts, Resumes, and **any new type** discovered dynamically
- **AI + deterministic hybrid** — AI handles ambiguity, deterministic logic handles validation and business rules
- **Confidence scoring** — Every extraction is scored; low-confidence fields trigger interactive MCQ dialogs
- **Gibberish detection** — Detects poor OCR/random text and suggests intelligent corrections
- **MCQ clarification dialogs** — When uncertain, the system asks the user targeted multiple-choice questions with explanations
- **Learning system** — User corrections are stored in a vector database; patterns improve extraction over time
- **Extensible plugin architecture** — New document types added by registering a schema (no code changes)
- **Async processing** — Celery workers handle OCR and AI extraction in the background
- **Full REST API** — JSON export for downstream system integration
- **Dark mode UI** — Modern React frontend with real-time MCQ dialogs

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | FastAPI (Python 3.12) | Async, auto-docs, Pydantic integration |
| **AI Model** | DeepSeek-V3 (via API/OpenRouter) | Cost-effective, strong document understanding |
| **Database** | PostgreSQL + pgvector | Relational data + vector similarity search |
| **Cache/Queue** | Redis + Celery | Async processing, background tasks |
| **Object Storage** | MinIO | S3-compatible document storage |
| **OCR** | Tesseract + PyMuPDF | Text extraction from PDFs/images |
| **Frontend** | React 18 + TypeScript + Tailwind | Modern, type-safe UI with MCQ dialogs |
| **Vector Store** | pgvector (IVFFlat index) | Semantic pattern matching for learning |

## Design Decisions

### AI vs Deterministic Split

| Concern | Approach | Why |
|---------|----------|-----|
| **Document classification** | AI (LLM) + regex pattern matching | Fast path for known types, AI for ambiguity |
| **Field extraction** | AI (LLM) | Handles variation in layout, formatting |
| **Field validation** | Deterministic | Email, phone, date formats are well-defined |
| **Gibberish detection** | Deterministic (character analysis) | Fast, reliable, no AI cost |
| **Confidence scoring** | Hybrid (AI + validation + patterns) | Combines model certainty with business rules |
| **Cross-field validation** | Deterministic | e.g., total vs subtotal comparison |
| **MCQ generation** | AI (LLM) | Creates human-readable options with reasoning |
| **Pattern learning** | AI + vector search | Extracts patterns from corrections, stores for similarity |

### Extensibility Strategy

1. **Schema registry** — Document type definitions stored in PostgreSQL, loaded at runtime
2. **Plugin architecture** — New types added via `document_schemas` table (no backend code changes)
3. **Dynamic discovery** — Unknown document types trigger AI schema creation on-the-fly
4. **Vector memory** — Patterns learned from corrections improve extraction for similar documents
5. **Few-shot ready** — 3-5 corrected documents of a new type builds reliable extraction patterns

### Low-Confidence Handling

1. **Confidence threshold system**:
   - `>= 0.8`: Auto-approve
   - `0.5 - 0.8`: Flag for review (field highlighted in UI)
   - `< 0.5`: Generate MCQ dialog with options

2. **MCQ generation** considers:
   - Common OCR errors (0/O, 1/I/l, 5/S)
   - Context from surrounding text
   - Historical patterns from similar documents
   - Provides explanations for each option

3. **Gibberish detection**:
   - Checks special character ratio > 50%
   - Checks consonant streaks > 6
   - Empty / very short values flagged

### Learning & Memory

Corrections feed into a **continuous learning loop**:

```
User corrects a field
       │
       ▼
Store correction in PostgreSQL
       │
       ▼
AI extracts the pattern (keywords, position, regex)
       │
       ▼
Generate embedding via text-embedding-3-small
       │
       ▼
Store in pgvector with IVFFlat index
       │
       ▼
Future extractions query similar patterns
       │
       ▼
Patterns boost confidence for matching fields
```

After 100 unprocessed corrections, the system triggers a model update (fine-tuning pipeline).

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── worker.py                  # Celery worker
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # Route aggregator
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── process.py         # Document CRUD, processing, corrections
│   │   │       └── system.py          # Health, types, document listing
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py          # DeepSeek/OpenAI client
│   │   │   ├── embeddings.py         # Embedding generation
│   │   │   └── prompts/
│   │   │       ├── classification.py  # Classification prompt template
│   │   │       ├── extraction.py      # Extraction prompt template
│   │   │       ├── mcq_generation.py  # MCQ generation prompt template
│   │   │       └── learning.py        # Pattern extraction prompt template
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings via pydantic-settings
│   │   │   └── database.py           # SQLAlchemy + session management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Abstract base model
│   │   │   ├── document.py           # Document + Extraction + MCQDialogue
│   │   │   ├── schema.py             # DocumentSchema
│   │   │   ├── correction.py         # UserCorrection
│   │   │   └── pattern.py            # ExtractionPattern (with embedding)
│   │   ├── services/
│   │   │   ├── document_classifier.py    # AI + pattern classification
│   │   │   ├── extractor_service.py      # Intelligent field extraction
│   │   │   ├── validation_service.py     # Deterministic validation
│   │   │   ├── mcq_generator.py          # MCQ dialog generation
│   │   │   ├── learning_service.py       # Correction learning + patterns
│   │   │   ├── confidence_analyzer.py    # Confidence scoring
│   │   │   ├── vector_store.py           # pgvector operations
│   │   │   └── document_processor.py     # Orchestration pipeline
│   │   └── processors/
│   │       ├── ocr_processor.py      # Tesseract + image OCR
│   │       └── pdf_processor.py      # PyMuPDF text extraction
│   ├── db/
│   │   └── init.sql                  # DB schema + seed data
│   ├── tests/
│   │   ├── test_services.py          # Service unit tests
│   │   └── __init__.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── UploadZone.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   └── MCQDialog.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- DeepSeek API key (or OpenRouter key)
- 4GB+ RAM

### Setup

```bash
# 1. Clone and enter
git clone <repo> && cd doc-intelligence-system

# 2. Configure API keys
cp backend/.env.example backend/.env
# Edit backend/.env — set DEEPSEEK_API_KEY or OPENROUTER_API_KEY

# 3. Start all services
docker compose up -d --build

# 4. Run database migrations (auto on first start via init.sql)
```

### Access

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000/docs |
| **MinIO Console** | http://localhost:9001 (minioadmin:minioadmin) |

### Usage Flow

1. **Upload** — Drag a PDF invoice into the upload zone
2. **Auto-classify** — System identifies it as an "invoice" (AI + pattern matching)
3. **Extract** — Structured data extracted with per-field confidence scores
4. **Review** — High-confidence fields auto-approved; low-confidence flagged
5. **MCQ Clarify** — Uncertain fields present an MCQ dialog with options and explanations
6. **Correct** — User selects the right option or enters a custom value
7. **Learn** — Correction is stored as a pattern in pgvector; future extractions improve
8. **Export** — Download structured JSON for downstream systems

## API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload a document file |
| `POST` | `/api/documents/{id}/process` | Process (classify + extract + validate) |
| `GET` | `/api/documents/{id}/status` | Get processing status |
| `GET` | `/api/documents/{id}/extractions` | Get extracted fields with MCQ dialogs |
| `POST` | `/api/documents/{id}/corrections` | Submit corrections (triggers learning) |
| `GET` | `/api/documents/{id}/export` | Export structured JSON |
| `GET` | `/api/documents/{id}/mcqs` | Get pending MCQ dialogs |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/types` | List supported document types |
| `GET` | `/api/documents` | List all documents |

## API Example

```bash
# Upload
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@invoice.pdf"

# Process
curl -X POST http://localhost:8000/api/documents/{id}/process

# Get extractions with MCQ dialogs
curl http://localhost:8000/api/documents/{id}/extractions

# Submit correction (triggers learning)
curl -X POST http://localhost:8000/api/documents/{id}/corrections \
  -H "Content-Type: application/json" \
  -d '{"corrections": [{"extraction_id": "...", "corrected_value": "INV-2024-001"}]}'

# Export structured data
curl http://localhost:8000/api/documents/{id}/export
```

## Testing

```bash
# Backend tests
docker compose exec backend python -m pytest tests/ -v

# Test specific services
docker compose exec backend python -m pytest tests/test_services.py -v
```

## Extending with New Document Types

Add a new document type without code changes by inserting into `document_schemas`:

```sql
INSERT INTO document_schemas (id, document_type, schema_definition, extraction_prompts, validation_rules)
VALUES (
    gen_random_uuid(),
    'bank_statement',
    '{
        "fields": [
            {"name": "account_holder", "type": "string", "required": true},
            {"name": "account_number", "type": "string", "required": true},
            {"name": "statement_period", "type": "string", "required": true},
            {"name": "opening_balance", "type": "number", "required": true},
            {"name": "closing_balance", "type": "number", "required": true},
            {"name": "transactions", "type": "array", "required": false}
        ]
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);
```

Or upload a document of an unknown type — the AI will auto-discover it and create the schema interactively.

## Future Improvements

- **Multi-page document splitting** — Auto-detect and process each page separately
- **Batch processing** — Upload multiple documents simultaneously
- **Active learning pipeline** — Periodic fine-tuning with accumulated corrections
- **Multi-language support** — Extend classification and extraction prompts
- **Webhook notifications** — Push processed data to ERP/CRM systems
- **User authentication** — Multi-tenant with API keys
- **Template designer UI** — Visual schema editor for new document types
- **Mobile document capture** — Camera-to-extraction pipeline

## Assumptions

1. Documents are primarily text-based (PDFs or clear images)
2. AI model has internet access (API-based) with 8K+ context window
3. Valid DeepSeek/OpenRouter API key with sufficient credits
4. English-language documents (extensible via prompt modifications)
5. Single-user system in current iteration (no auth layer)
6. Documents arrive individually (not batch uploads)

---

Built with FastAPI, React, TypeScript, Tailwind CSS, PostgreSQL/pgvector, DeepSeek-V3, and Celery.
