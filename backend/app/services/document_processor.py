from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings, UPLOAD_PATH
from app.core.database import SessionLocal
from app.models.document import Document, Extraction, MCQDialogue
from app.models.schema import DocumentSchema
from app.services.document_classifier import DocumentClassifier
from app.services.extractor_service import IntelligentExtractor
from app.services.validation_service import ValidationService
from app.services.mcq_generator import MCQGenerator
from app.services.learning_service import LearningService
from app.services.confidence_analyzer import ConfidenceAnalyzer
from app.processors.ocr_processor import OCRProcessor


class DocumentProcessor:
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.extractor = IntelligentExtractor()
        self.validator = ValidationService()
        self.mcq_generator = MCQGenerator()
        self.learning_service = LearningService()
        self.confidence_analyzer = ConfidenceAnalyzer()
    
    async def process_document(self, document_id: str) -> dict:
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                return {"error": "Document not found"}
            
            doc.status = "processing"
            db.commit()
            
            file_path = Path(doc.file_path)
            text_content = await OCRProcessor.process(file_path)
            doc.raw_text = text_content
            db.commit()
            
            classification = await self.classifier.classify(text_content, doc.filename)
            doc.document_type = classification.get("document_type", "unknown")
            doc.type_confidence = classification.get("confidence", 0.0)
            doc.is_new_type = classification.get("is_new_type", False)
            doc.suggested_type = classification.get("suggested_type")
            
            if classification.get("is_new_type"):
                schema_data = await self.classifier.create_schema_for_new_type(
                    classification["document_type"],
                    classification.get("suggested_fields", []),
                    text_content[:2000],
                )
                
                new_schema = DocumentSchema(
                    document_type=classification["document_type"],
                    schema_definition=schema_data,
                    extraction_prompts={},
                    validation_rules={},
                )
                db.add(new_schema)
                db.commit()
            else:
                schema_data = self._get_schema_for_type(db, classification["document_type"])
            
            if not schema_data:
                doc.status = "failed"
                db.commit()
                return {"error": f"No schema for type: {classification['document_type']}"}
            
            extractions_data = await self.extractor.extract_all(
                document_id=document_id,
                text=text_content,
                document_type=classification["document_type"],
                schema=schema_data,
            )
            
            extraction_records = []
            for ext_data in extractions_data:
                extraction = Extraction(
                    document_id=document_id,
                    field_name=ext_data.get("field_name", ext_data.get("name", "unknown")),
                    extracted_value=str(ext_data.get("value", "")),
                    confidence_score=ext_data.get("confidence", 0.0),
                    extraction_method="ai",
                    needs_review=ext_data.get("needs_review", False),
                    is_gibberish=ext_data.get("is_gibberish", False),
                    alternatives=ext_data.get("alternatives", []),
                    reasoning=ext_data.get("reasoning", ""),
                )
                db.add(extraction)
                db.flush()
                
                if extraction.needs_review or extraction.confidence_score < 0.5:
                    mcq_data = await self.mcq_generator.generate_clarification_dialog(
                        extraction=ext_data,
                        document_context=text_content[:500],
                        field_definition={"name": extraction.field_name, "type": "string"},
                    )
                    
                    mcq = MCQDialogue(
                        extraction_id=extraction.id,
                        question=mcq_data.get("question", f"What is the correct {extraction.field_name}?"),
                        options=mcq_data.get("options", []),
                        context_hint=mcq_data.get("context_hint", ""),
                        default_selection=mcq_data.get("default_selection", 0),
                        allow_custom_input=mcq_data.get("allow_custom_input", True),
                        confidence_before=extraction.confidence_score,
                    )
                    db.add(mcq)
                
                extraction_records.append(extraction)
            
            db.commit()
            
            processed_data = {}
            for ext in extraction_records:
                processed_data[ext.field_name] = {
                    "value": ext.corrected_value or ext.extracted_value,
                    "confidence": ext.confidence_score,
                    "needs_review": ext.needs_review,
                }
            doc.processed_data = processed_data
            
            review_needed = any(e.needs_review for e in extraction_records)
            doc.status = "review_needed" if review_needed else "completed"
            db.commit()
            
            return self._build_response(doc, extraction_records)
        
        except Exception as e:
            doc.status = "failed"
            db.commit()
            return {"error": str(e)}
        finally:
            db.close()
    
    def _get_schema_for_type(self, db, document_type: str) -> Optional[dict]:
        schema = db.query(DocumentSchema).filter(
            DocumentSchema.document_type == document_type,
            DocumentSchema.is_active == True,
        ).first()
        return schema.schema_definition if schema else None
    
    def _build_response(self, doc: Document, extractions: list[Extraction]) -> dict:
        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "document_type": doc.document_type,
            "type_confidence": doc.type_confidence,
            "status": doc.status,
            "is_new_type": doc.is_new_type,
            "extractions": [
                {
                    "id": e.id,
                    "field_name": e.field_name,
                    "extracted_value": e.extracted_value,
                    "confidence_score": e.confidence_score,
                    "needs_review": e.needs_review,
                    "is_gibberish": e.is_gibberish,
                    "reasoning": e.reasoning,
                    "alternatives": e.alternatives,
                    "has_mcq": len(e.mcq_dialogues) > 0,
                }
                for e in extractions
            ],
        }
