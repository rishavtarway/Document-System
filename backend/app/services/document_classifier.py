from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings
from app.ai.llm_client import LLMClient
from app.models.schema import DocumentSchema


KNOWN_TYPE_PATTERNS = {
    "invoice": [
        r'\b(?:INVOICE|INV|INVOICE\s+NUMBER|INVOICE\s+#)\b',
        r'\b(?:BILL\s+TO|BILLING\s+ADDRESS)\b',
        r'\b(?:SUBTOTAL|SUB\s+TOTAL)\b',
    ],
    "purchase_order": [
        r'\b(?:PURCHASE\s+ORDER|PO\s+NUMBER|PURCHASE\s+ORDER\s+#)\b',
        r'\b(?:REQUISITIONER|REQ\s+#)\b',
        r'\b(?:SHIP\s+TO|SHIPPING\s+ADDRESS)\b',
    ],
    "contract": [
        r'\b(?:CONTRACT|AGREEMENT)\b',
        r'\b(?:THIS\s+AGREEMENT|PARTIES|EFFECTIVE\s+DATE)\b',
        r'\b(?:GOVERNING\s+LAW|JURISDICTION)\b',
    ],
    "resume": [
        r'\b(?:RESUME|CURRICULUM\s+VITAE|CV)\b',
        r'\b(?:EXPERIENCE|EMPLOYMENT\s+HISTORY|WORK\s+HISTORY)\b',
        r'\b(?:EDUCATION|DEGREE|UNIVERSITY)\b',
        r'\b(?:SKILLS|TECHNICAL\s+SKILLS|PROFICIENCIES)\b',
    ],
}


class DocumentClassifier:
    def __init__(self):
        self.llm = LLMClient()
    
    async def classify(self, text: str, filename: str) -> dict:
        pattern_match = self._pattern_based_classification(text)
        if pattern_match["confidence"] > 0.9:
            return pattern_match
        
        known_types = await self._load_known_types()
        prompt = (
                "Analyze this document and classify its type.\n\n"
                f"Filename: {filename}\n"
                f"Content Preview: {text[:3000]}\n\n"
                f"Known Document Types:\n{json.dumps(known_types, indent=2)}\n\n"
                "Tasks:\n"
                "1. Identify the document type (from known types or suggest new)\n"
                "2. Provide confidence score (0-1)\n"
                "3. List key indicators that led to this classification\n"
                "4. If it's a new type, suggest a name and typical fields\n\n"
                'Respond in JSON:\n{\n    "document_type": "string",\n    "confidence": float,\n'
                '    "is_new_type": boolean,\n    "indicators": ["string"],\n'
                '    "suggested_fields": ["string"]\n}\n'
            )
        
        response = await self.llm.generate(prompt)
        result = json.loads(response)
        
        return {
            "document_type": result.get("document_type", "unknown"),
            "confidence": float(result.get("confidence", 0.0)),
            "is_new_type": result.get("is_new_type", False),
            "indicators": result.get("indicators", []),
            "suggested_fields": result.get("suggested_fields", []),
            "method": "ai" if not result.get("is_new_type") else "ai_new",
        }
    
    def _pattern_based_classification(self, text: str) -> dict:
        scores = {}
        text_upper = text.upper()
        
        for doc_type, patterns in KNOWN_TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    score += 1
            if score > 0:
                scores[doc_type] = score / len(patterns)
        
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            if best_score >= 0.5:
                return {
                    "document_type": best_type,
                    "confidence": min(0.95, 0.5 + best_score * 0.5),
                    "is_new_type": False,
                    "indicators": [],
                    "suggested_fields": [],
                    "method": "pattern",
                }
        
        return {"document_type": "unknown", "confidence": 0.0, "is_new_type": True, "indicators": [], "suggested_fields": [], "method": "none"}
    
    async def _load_known_types(self) -> list:
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            schemas = db.query(DocumentSchema).filter(DocumentSchema.is_active == True).all()
            return [{"type": s.document_type, "fields": list(s.schema_definition.keys())} for s in schemas]
        finally:
            db.close()
    
    async def create_schema_for_new_type(self, new_type: str, suggested_fields: list[str], sample_text: str) -> dict:
        prompt = (
            f"Create a JSON schema for extracting data from this new document type: {new_type}\n\n"
            f"Sample content:\n{sample_text[:2000]}\n\n"
            f"Suggested fields: {suggested_fields}\n\n"
            "Generate a schema with:\n"
            "- Field names\n- Data types\n- Validation rules\n- Confidence thresholds\n\n"
            'Format:\n{\n    "fields": [\n'
            '        {{"name": "string", "type": "string", "required": boolean, "validation": "regex_or_rule"}}\n'
            "    ]\n}\n"
        )
        response = await self.llm.generate(prompt)
        return json.loads(response)
