from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.config import UPLOAD_PATH, settings
from core.schemas import (
    CorrectionBatch,
    DocumentResponse,
    DocumentStatus,
    DocumentType,
    ExtractionResult,
    ValidationResult,
)
from models.database import DocumentRecord, get_db
from services.document_service import process_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc_id = str(uuid.uuid4())
    safe_name = f"{doc_id}_{file.filename}"
    file_path = UPLOAD_PATH / safe_name

    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_file_size_mb}MB limit",
        )

    with open(file_path, "wb") as f:
        f.write(content)

    record = DocumentRecord(
        id=doc_id,
        filename=file.filename,
        content_type=file.content_type,
        file_path=str(file_path),
        file_size=len(content),
        status=DocumentStatus.UPLOADED.value,
    )
    db.add(record)
    db.commit()

    return _record_to_response(record)


@router.post("/process/{doc_id}", response_model=DocumentResponse)
async def process_document_endpoint(doc_id: str, db: Session = Depends(get_db)):
    record = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    result = await process_document(
        file_path=file_path,
        filename=record.filename,
        content_type=record.content_type,
    )

    record.document_type = result.document_type.value
    record.status = result.status.value
    record.extraction_data = result.data
    record.extraction_confidence = result.confidence
    record.validations = [v.model_dump() for v in result.validations]
    record.updated_at = datetime.utcnow()

    if result.status == DocumentStatus.FAILED:
        record.status = DocumentStatus.FAILED.value

    db.commit()
    db.refresh(record)
    return _record_to_response(record, result)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    records = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    return [_record_to_response(r) for r in records]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    record = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return _record_to_response(record)


@router.post("/{doc_id}/correct", response_model=DocumentResponse)
async def correct_extraction(
    doc_id: str, corrections: CorrectionBatch, db: Session = Depends(get_db)
):
    record = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    corrected = record.extraction_data.copy() if record.extraction_data else {}

    for corr in corrections.corrections:
        keys = corr.field_path.split(".")
        target = corrected
        for key in keys[:-1]:
            if isinstance(target, dict):
                target = target.setdefault(key, {})
            else:
                break
        if isinstance(target, dict):
            target[keys[-1]] = corr.corrected_value

    record.corrected_data = corrected
    record.status = DocumentStatus.REVIEWED.value
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return _record_to_response(record)


@router.get("/{doc_id}/export", response_model=dict)
async def export_document(doc_id: str, db: Session = Depends(get_db)):
    record = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    data = record.corrected_data or record.extraction_data or {}
    return {
        "id": record.id,
        "filename": record.filename,
        "document_type": record.document_type,
        "status": record.status,
        "confidence": record.extraction_confidence,
        "data": data,
        "validations": record.validations or [],
        "exported_at": datetime.utcnow().isoformat(),
    }


def _record_to_response(
    record: DocumentRecord, result: ExtractionResult | None = None
) -> DocumentResponse:
    extraction = None
    if result:
        extraction = result
    elif record.extraction_data:
        extraction = ExtractionResult(
            id=record.id,
            document_id=record.id,
            document_type=DocumentType(record.document_type or "unknown"),
            confidence=record.extraction_confidence or 0.0,
            data=record.corrected_data or record.extraction_data,
            validations=[ValidationResult(**v) for v in (record.validations or [])],
            status=DocumentStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    return DocumentResponse(
        id=record.id,
        filename=record.filename,
        content_type=record.content_type,
        file_size=int(record.file_size),
        document_type=DocumentType(record.document_type) if record.document_type else None,
        status=DocumentStatus(record.status),
        extraction=extraction,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
