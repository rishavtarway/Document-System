from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.config import UPLOAD_PATH
from core.extractors import EXTRACTOR_REGISTRY
from core.extractors.base import BaseExtractor
from core.schemas import (
    DocumentType,
    DocumentStatus,
    ExtractionResult,
    ValidationResult,
)
from core.validator import validate_extraction


async def process_document(
    file_path: Path,
    filename: str,
    content_type: Optional[str] = None,
) -> ExtractionResult:
    doc_id = str(uuid.uuid4())

    text_content = _extract_text(file_path)
    image_data = _get_image_data(file_path)

    doc_type, cls_confidence = _classify_document(text_content)
    status = DocumentStatus.PROCESSING

    extraction: ExtractionResult

    if doc_type == "unknown" or cls_confidence < 0.6:
        extraction = ExtractionResult(
            document_id=doc_id,
            document_type=DocumentType.UNKNOWN,
            confidence=cls_confidence,
            data={"raw_text": text_content[:2000]},
            validations=[
                ValidationResult(
                    field="document_type",
                    status="error",
                    message=f"Could not classify document confidently (confidence={cls_confidence:.2f})",
                )
            ],
            status=DocumentStatus.FAILED,
        )
        return extraction

    extractor_cls = EXTRACTOR_REGISTRY.get(doc_type)
    if not extractor_cls:
        extraction = ExtractionResult(
            document_id=doc_id,
            document_type=DocumentType.UNKNOWN,
            confidence=0.0,
            data={"raw_text": text_content[:2000]},
            validations=[
                ValidationResult(
                    field="document_type",
                    status="error",
                    message=f"No extractor found for type '{doc_type}'",
                )
            ],
            status=DocumentStatus.FAILED,
        )
        return extraction

    extractor: BaseExtractor = extractor_cls()
    extracted_data, extraction_confidence = extractor.extract(text_content, image_data)

    overall_confidence = round((cls_confidence * 0.3 + extraction_confidence * 0.7), 2)
    validations = validate_extraction(doc_type, extracted_data)

    status = DocumentStatus.EXTRACTED
    for v in validations:
        if v.status == "error":
            status = DocumentStatus.VALIDATED
            break

    extraction = ExtractionResult(
        document_id=doc_id,
        document_type=DocumentType(doc_type),
        confidence=overall_confidence,
        data=extracted_data,
        validations=validations,
        status=status,
    )
    return extraction


def _classify_document(text_content: str) -> tuple[str, float]:
    from core.ai_client import AIClient
    return AIClient.classify_document(text_content)


def _extract_text(file_path: Path) -> str:
    import fitz
    try:
        doc = fitz.open(str(file_path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip() or ""
    except Exception:
        return ""


def _get_image_data(file_path: Path) -> Optional[str]:
    import base64
    from pathlib import Path

    ext = file_path.suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".tiff", ".tif"):
        return None

    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
