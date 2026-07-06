from __future__ import annotations

import json
from typing import Optional

from app.ai.llm_client import LLMClient
from app.services.vector_store import VectorStore
from app.core.database import SessionLocal
from app.models.correction import UserCorrection
from app.models.pattern import ExtractionPattern


class LearningService:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    async def learn_from_correction(self, correction: dict):
        db = SessionLocal()
        try:
            db_correction = UserCorrection(
                extraction_id=correction.get("extraction_id", ""),
                original_value=correction.get("original_value"),
                corrected_value=correction.get("corrected_value"),
                field_name=correction.get("field_name", ""),
                document_type=correction.get("document_type", ""),
            )
            db.add(db_correction)
            db.commit()
            
            pattern = await self._extract_pattern(correction)
            
            from app.ai.embeddings import EmbeddingClient
            embedding = await EmbeddingClient.embed(pattern.get("text", correction.get("corrected_value", "")))
            
            db_pattern = ExtractionPattern(
                document_type=correction.get("document_type", ""),
                field_name=correction.get("field_name", ""),
                pattern_text=pattern.get("text"),
                keywords=pattern.get("keywords", []),
                position_hint=pattern.get("position_hint"),
                regex_pattern=pattern.get("regex_pattern"),
                confidence_boost=pattern.get("confidence_boost", 0.1),
                success_count=1,
                example_value=correction.get("corrected_value"),
            )
            db.add(db_pattern)
            db.commit()
            
            await self.vector_store.add_pattern(
                document_type=correction.get("document_type", ""),
                field_name=correction.get("field_name", ""),
                pattern_text=pattern.get("text", ""),
                embedding=embedding,
                example_value=correction.get("corrected_value"),
            )
            
            count = db.query(UserCorrection).filter(
                UserCorrection.applied_to_model == False
            ).count()
            
            from app.core.config import settings
            if count >= settings.min_corrections_for_retrain:
                await self._trigger_model_update()
        
        finally:
            db.close()
    
    async def _extract_pattern(self, correction: dict) -> dict:
        prompt = (
            "A user corrected an extraction. Learn the pattern.\n\n"
            f"Document Type: {correction.get('document_type', 'unknown')}\n"
            f"Field: {correction.get('field_name', 'unknown')}\n"
            f'Wrong extraction: "{correction.get("original_value", "")}"\n'
            f'Correct value: "{correction.get("corrected_value", "")}"\n\n'
            f"Context:\n{correction.get('document_text', '')[:500]}\n\n"
            "Extract:\n"
            "1. The text pattern/template that indicates this field\n"
            "2. Common words/phrases nearby\n"
            "3. Position indicators (near top, after 'Total:', etc.)\n"
            "4. Format patterns (regex if applicable)\n\n"
            'Format:\n{\n    "text": "natural language description of pattern",\n'
            '    "keywords": ["nearby", "words"],\n'
            '    "position_hint": "location description",\n'
            '    "regex_pattern": "optional regex",\n'
            '    "confidence_boost": float\n}\n'
        )
        response = await self.llm.generate(prompt)
        return json.loads(response)
    
    async def _trigger_model_update(self):
        # Placeholder for fine-tuning pipeline
        pass
