from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.models.schema import DocumentSchema

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-document-intelligence-system",
        "version": "2.0.0",
    }


@router.get("/types")
def get_document_types(db: Session = Depends(get_db)):
    schemas = db.query(DocumentSchema).filter(DocumentSchema.is_active == True).all()
    
    types = [
        {
            "id": "invoice",
            "name": "Invoice",
            "description": "Extract invoice details including line items, totals, vendor info",
        },
        {
            "id": "purchase_order",
            "name": "Purchase Order",
            "description": "Extract PO details including items, quantities, delivery info",
        },
        {
            "id": "contract",
            "name": "Contract",
            "description": "Extract contract terms, parties, and key clauses",
        },
        {
            "id": "resume",
            "name": "Resume",
            "description": "Extract candidate info, skills, experience, education",
        },
    ]
    
    for s in schemas:
        if s.document_type not in [t["id"] for t in types]:
            types.append({
                "id": s.document_type,
                "name": s.document_type.replace("_", " ").title(),
                "description": f"Extract data from {s.document_type} documents",
            })
    
    return {"types": types}


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(50).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "type_confidence": d.type_confidence,
            "status": d.status,
            "file_size": d.file_size,
            "is_new_type": d.is_new_type,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]
