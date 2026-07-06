from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.documents import router as document_router
from models.database import init_db

app = FastAPI(
    title="Document Intelligence System",
    description="AI-powered document processing, classification, extraction, and validation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "document-intelligence-system"}


@app.get("/api/types")
def get_document_types():
    return {
        "types": [
            {"id": "invoice", "name": "Invoice", "description": "Extract invoice details including line items, totals, and vendor info"},
            {"id": "purchase_order", "name": "Purchase Order", "description": "Extract PO details including items, quantities, and delivery info"},
            {"id": "contract", "name": "Contract", "description": "Extract contract terms, parties, and key clauses"},
            {"id": "resume", "name": "Resume", "description": "Extract candidate info, skills, experience, and education"},
        ]
    }
