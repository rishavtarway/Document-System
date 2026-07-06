# Document Intelligence System

AI-powered document processing system that automatically classifies, extracts, validates, and exposes structured data from business documents (Invoices, Purchase Orders, Contracts, Resumes).

## Architecture Overview

```
┌─────────────┐     ┌─────────────────────────────────────┐     ┌──────────┐
│   Frontend  │────▶│            Backend (FastAPI)        │────▶│ SQLite   │
│  (React/TS) │     │                                     │     │ Database │
└─────────────┘     │  ┌─────────┐  ┌───────────────┐     │     └──────────┘
                    │  │Upload   │  │Document       │     │
                    │  │Endpoint │──▶│Classifier (AI)│     │
                    │  └─────────┘  └───────┬───────┘     │
                    │                       ▼              │
                    │  ┌──────────────────────────────┐    │
                    │  │  Extractor Registry          │    │
                    │  │  ┌────────┐ ┌───────────┐    │    │
                    │  │  │Invoice │ │Purchase   │    │    │
                    │  │  │        │ │Order      │    │    │
                    │  │  ├────────┤ ├───────────┤    │    │
                    │  │  │Contract│ │Resume     │    │    │
                    │  │  └────────┘ └───────────┘    │    │
                    │  └───────────┬──────────────────┘    │
                    │              ▼                       │
                    │  ┌──────────────────────────────┐    │
                    │  │  Validator                   │    │
                    │  │  (Deterministic + AI checks) │    │
                    │  └───────────┬──────────────────┘    │
                    │              ▼                       │
                    │  ┌──────────────────────────────┐    │
                    │  │  User Correction Workflow    │    │
                    │  │  (Review → Edit → Save)     │    │
                    │  └──────────────────────────────┘    │
                    │                                     │
                    │  ┌──────────────────────────────┐    │
                    │  │  Export / API Endpoints      │    │
                    │  │  (JSON output for downstream)│    │
                    │  └──────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

## Design Decisions

### What's Handled by AI vs. Deterministic Logic

| Concern | Approach | Why |
|---------|----------|-----|
| **Document Classification** | AI (GPT-4o) | Documents vary widely in format; AI understands semantic content and layout |
| **Field Extraction** | AI (GPT-4o) | Handles variations in layout, phrasing, and formatting; extracts meaning |
| **Field Validation** | Deterministic (regex, type checks, business rules) | Format validation (email, phone, dates) is well-defined and should be deterministic |
| **Confidence Scoring** | Hybrid: AI provides per-field confidence + deterministic rules boost/lower overall score | Combines model certainty with rule-based verification |
| **Cross-field Checks** | Deterministic (e.g., total vs subtotal comparison) | Business logic that should be consistent and explainable |
| **Data Persistence** | Deterministic (SQLAlchemy + SQLite) | Standard database operations |

### Extensibility for New Document Types

New document types are added via a **plugin-based extractor registry**:

1. Create a new extractor class in `backend/core/extractors/` that extends `BaseExtractor`
2. Define the `extraction_prompt` (what fields the AI should extract)
3. Define `validation_rules` (deterministic checks for the fields)
4. Register the extractor in `backend/core/extractors/__init__.py`

```python
# Example: Adding a "Bank Statement" extractor
class BankStatementExtractor(BaseExtractor):
    document_type = "bank_statement"

    @property
    def extraction_prompt(self):
        return "Extract account holder, account number, statement period, transactions..."

    @property
    def validation_rules(self):
        return {
            "account_holder": {"required": True, "type": "string"},
            "statement_balance": {"required": True, "type": "number"},
        }

# Register in __init__.py
EXTRACTOR_REGISTRY["bank_statement"] = BankStatementExtractor
```

The classifier automatically detects new document types if they appear in extracted prompts, and the system routes to the right extractor via the registry.

### Handling Low-Confidence AI Responses

1. **Confidence Thresholds**: Documents below `0.6` classification confidence are flagged as `unknown` and not auto-processed
2. **Validation Layer**: Each extracted field is validated; errors surface to the user with suggested corrections
3. **Human-in-the-Loop**: Users can review, edit, and correct any field; corrections are saved separately
4. **Reprocessing**: Users can trigger re-extraction at any time
5. **Fallback**: If extraction fails entirely, raw text is stored for manual review

### Downstream System Integration

- **REST API**: All processed data is available via JSON endpoints
- **Export Endpoint**: `GET /api/documents/{id}/export` returns structured data with metadata
- **Webhook-ready**: Architecture supports adding webhooks to push data to ERP, CRM, or document management systems
- **Standard JSON Schema**: Each document type has a consistent Pydantic schema for predictable output

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend Framework** | FastAPI (Python) | Async, auto-docs, pydantic integration, high performance |
| **AI Model** | OpenAI GPT-4o | Best-in-class document understanding, JSON mode for structured output |
| **Database** | SQLite (via SQLAlchemy) | Zero-config, sufficient for demo/medium scale |
| **Frontend** | React 18 + TypeScript + Tailwind CSS | Modern, type-safe, responsive UI |
| **Build Tool** | Vite | Fast dev server, optimized builds |
| **Validation** | Regex + type checks + business rules | Deterministic, explainable, low-latency |
| **PDF Processing** | PyMuPDF (fitz) | Fast PDF text extraction |
| **Containerization** | Docker / docker-compose | Easy deployment |

## Project Structure

```
document-processing-system/
├── backend/
│   ├── api/
│   │   ├── main.py                  # FastAPI app, middleware, routes
│   │   └── routes/
│   │       └── documents.py         # Document CRUD, processing, correction endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── schemas.py               # Pydantic models for all document types
│   │   ├── ai_client.py             # OpenAI client wrapper
│   │   ├── validator.py             # Deterministic validation logic
│   │   └── extractors/
│   │       ├── __init__.py          # Extractor registry (plugin system)
│   │       ├── base.py              # Abstract base extractor
│   │       ├── invoice.py           # Invoice extractor
│   │       ├── purchase_order.py    # Purchase order extractor
│   │       ├── contract.py          # Contract extractor
│   │       └── resume.py            # Resume extractor
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py              # SQLAlchemy models + DB setup
│   ├── services/
│   │   ├── __init__.py
│   │   └── document_service.py      # Core processing pipeline
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                  # Main app component
│   │   ├── index.css                # Tailwind imports
│   │   ├── api/
│   │   │   └── documents.ts         # API client (all endpoints)
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript interfaces
│   │   └── components/
│   │       ├── Header.tsx           # App header
│   │       ├── UploadZone.tsx       # Drag-and-drop file upload
│   │       ├── DocumentList.tsx     # Sidebar document list
│   │       └── DocumentViewer.tsx   # Extraction display + correction UI
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── tests/
│   ├── test_validator.py            # Validation logic tests
│   └── test_extractors.py           # Extractor registry + confidence tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .gitignore
└── README.md
```

## Setup & Running

### Prerequisites

- Python 3.12+
- Node.js 20+
- OpenAI API key

### Quick Start (Local)

```bash
# 1. Clone and set up backend
cd backend
cp .env.example .env
# Edit .env: set OPENAI_API_KEY=sk-...
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# 2. In another terminal, set up frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
export OPENAI_API_KEY=sk-...
docker compose up --build
```

### Verify

- Backend: http://localhost:8000/docs (Swagger UI)
- Frontend: http://localhost:3000

### Run Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/types` | List supported document types |
| POST | `/api/documents/upload` | Upload a document file |
| POST | `/api/documents/process/{id}` | Classify + extract + validate |
| GET | `/api/documents/` | List all documents |
| GET | `/api/documents/{id}` | Get document details |
| POST | `/api/documents/{id}/correct` | Submit field corrections |
| GET | `/api/documents/{id}/export` | Export structured JSON |

## Live Demo Walkthrough

1. **Upload**: Drag a PDF invoice into the upload zone (or click to browse)
2. **Auto-classify**: The system identifies it as an "invoice"
3. **Extract**: Structured data (invoice number, vendor, line items, totals) is extracted
4. **Validate**: Fields are checked — missing invoice number shows a red error, suspect dates get a yellow warning
5. **Review**: The user sees all extracted data with validation banners at the top
6. **Correct**: Any field can be clicked and edited inline
7. **Save**: Corrections are saved; status changes to "reviewed"
8. **Export**: Click "Export" to download the final structured JSON

## Future Improvements

- **Batch Processing**: Upload and process multiple documents simultaneously
- **OCR Pipeline**: Integrate Tesseract for scanned document support
- **More Document Types**: Bank statements, shipping labels, tax forms, ID cards
- **Fine-tuned Models**: Train smaller models on domain-specific document layouts for faster/cheaper inference
- **Webhook Notifications**: Push processed data to ERP/CRM systems
- **User Authentication**: Multi-tenant support with API keys
- **Confidence Calibration**: Collect user corrections to tune confidence scoring
- **Streaming Extraction**: Real-time streaming for very large documents
- **Version History**: Track all corrections and reprocessing events per document
- **Search & Filter**: Full-text search across extracted data

## Assumptions

1. Documents are primarily text-based (PDFs or images with readable text)
2. AI model has sufficient context window (8K+ tokens) for most documents
3. Users have valid OpenAI API keys with GPT-4o access
4. Documents arrive as individual files (not batches)
5. Single-user system in current iteration (no auth)
6. English-language documents (extensible via prompt changes)

---

Built with FastAPI, React, TypeScript, Tailwind CSS, and OpenAI GPT-4o.
