from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings, UPLOAD_PATH
from app.core.database import get_db
from app.models.document import Document, Extraction, MCQDialogue
from app.models.schema import DocumentSchema
from app.services.document_processor import DocumentProcessor
from app.services.learning_service import LearningService

router = APIRouter(prefix="/api/documents", tags=["documents"])
processor = DocumentProcessor()
learning_service = LearningService()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc_id = str(uuid.uuid4())
    safe_name = f"{doc_id}_{file.filename}"
    file_path = UPLOAD_PATH / safe_name
    
    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_file_size_mb}MB limit")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    doc = Document(
        id=doc_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    
    return {"document_id": doc_id, "filename": doc.filename, "status": "uploaded"}


@router.post("/{document_id}/process")
async def process_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = await processor.process_document(document_id)
    return result


@router.get("/{document_id}/status")
async def get_status(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "type_confidence": doc.type_confidence,
        "status": doc.status,
        "is_new_type": doc.is_new_type,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.get("/{document_id}/extractions")
async def get_extractions(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    extractions = db.query(Extraction).filter(Extraction.document_id == document_id).all()
    
    result = []
    for ext in extractions:
        mcqs = db.query(MCQDialogue).filter(MCQDialogue.extraction_id == ext.id).all()
        result.append({
            "id": ext.id,
            "field_name": ext.field_name,
            "extracted_value": ext.extracted_value,
            "confidence_score": ext.confidence_score,
            "needs_review": ext.needs_review,
            "is_gibberish": ext.is_gibberish,
            "reasoning": ext.reasoning,
            "alternatives": ext.alternatives,
            "corrected_value": ext.corrected_value,
            "mcq_dialogs": [
                {
                    "id": m.id,
                    "question": m.question,
                    "options": m.options,
                    "context_hint": m.context_hint,
                    "default_selection": m.default_selection,
                    "allow_custom_input": m.allow_custom_input,
                    "resolved": m.resolved,
                }
                for m in mcqs
            ],
        })
    
    return {
        "document_id": document_id,
        "document_type": doc.document_type,
        "extractions": result,
        "review_needed": any(e.needs_review for e in extractions),
    }


@router.post("/{document_id}/corrections")
async def submit_correction(document_id: str, body: dict, db: Session = Depends(get_db)):
    corrections = body.get("corrections", [])
    
    for corr in corrections:
        extraction = db.query(Extraction).filter(
            Extraction.id == corr.get("extraction_id"),
            Extraction.document_id == document_id,
        ).first()
        
        if not extraction:
            continue
        
        extraction.corrected_value = corr.get("corrected_value", extraction.extracted_value)
        extraction.needs_review = False
        
        if "selected_mcq_option" in corr:
            mcq = db.query(MCQDialogue).filter(
                MCQDialogue.extraction_id == extraction.id,
                MCQDialogue.resolved == False,
            ).first()
            if mcq:
                mcq.user_selection = corr.get("selected_mcq_option")
                mcq.user_custom_value = corr.get("corrected_value")
                mcq.confidence_after = 1.0
                mcq.resolved = True
        
        await learning_service.learn_from_correction({
            "extraction_id": extraction.id,
            "original_value": extraction.extracted_value,
            "corrected_value": corr.get("corrected_value"),
            "field_name": extraction.field_name,
            "document_type": extraction.document.document_type if extraction.document else "unknown",
            "document_text": extraction.document.raw_text[:500] if extraction.document else "",
        })
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    remaining = db.query(Extraction).filter(
        Extraction.document_id == document_id,
        Extraction.needs_review == True,
    ).count()
    
    if remaining == 0:
        doc.status = "completed"
    
    db.commit()
    
    return {"status": "updated", "message": "Thank you! System learned from your input."}


@router.get("/{document_id}/export")
async def export_document(document_id: str, format: str = "json", db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    extractions = db.query(Extraction).filter(Extraction.document_id == document_id).all()
    
    data = {
        "document_id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "type_confidence": doc.type_confidence,
        "status": doc.status,
        "processed_at": doc.updated_at.isoformat() if doc.updated_at else None,
        "extracted_data": {},
        "metadata": {
            "file_size": doc.file_size,
            "is_new_type": doc.is_new_type,
        },
    }
    
    for ext in extractions:
        data["extracted_data"][ext.field_name] = {
            "value": ext.corrected_value or ext.extracted_value,
            "confidence": ext.confidence_score,
        }
    
    return data


@router.get("/{document_id}/mcqs")
async def get_pending_mcqs(document_id: str, db: Session = Depends(get_db)):
    extractions = db.query(Extraction).filter(
        Extraction.document_id == document_id,
        Extraction.needs_review == True,
    ).all()
    
    mcqs = []
    for ext in extractions:
        dialogs = db.query(MCQDialogue).filter(
            MCQDialogue.extraction_id == ext.id,
            MCQDialogue.resolved == False,
        ).all()
        for d in dialogs:
            mcqs.append({
                "mcq_id": d.id,
                "extraction_id": ext.id,
                "field_name": ext.field_name,
                "question": d.question,
                "options": d.options,
                "context_hint": d.context_hint,
                "default_selection": d.default_selection,
                "allow_custom_input": d.allow_custom_input,
            })
    
    return {"document_id": document_id, "mcq_count": len(mcqs), "mcqs": mcqs}
