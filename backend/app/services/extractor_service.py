from __future__ import annotations

import json
from typing import Optional

from app.ai.llm_client import LLMClient
from app.services.vector_store import VectorStore


class IntelligentExtractor:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    async def extract_all(self, document_id: str, text: str, document_type: str, schema: dict) -> list[dict]:
        extractions = []
        
        similar_docs = await self.vector_store.find_similar(
            document_type=document_type,
            query_text=text[:500],
            limit=3,
        )
        
        fields = schema.get("fields", [])
        for field in fields:
            extraction = await self._extract_field(
                text=text,
                field=field,
                document_type=document_type,
                context=similar_docs,
            )
            if extraction.get("confidence", 0) < 0.7 or self._is_gibberish(extraction.get("value", "")):
                extraction = await self._handle_uncertain_extraction(
                    text=text, field=field, initial_extraction=extraction
                )
            extractions.append(extraction)
        
        return extractions
    
    async def _extract_field(self, text: str, field: dict, document_type: str, context: list) -> dict:
        context_examples = "\n".join([
            f"Similar doc: {c.get('field_name', '?')} = {c.get('example_value', '?')}"
            for c in context if c.get("field_name") == field.get("name")
        ])
        
        prompt = (
            f"Extract the field '{field.get('name')}' from this {document_type}.\n\n"
            f"Field Definition:\n"
            f"- Type: {field.get('type', 'string')}\n"
            f"- Validation: {field.get('validation', 'none')}\n"
            f"- Required: {field.get('required', False)}\n\n"
            f"Historical Examples:\n{context_examples or 'None available'}\n\n"
            f"Document Text:\n{text[:6000]}\n\n"
            "Instructions:\n"
            "1. Extract the most likely value for this field\n"
            "2. If text is unclear/gibberish, provide best guesses with alternatives\n"
            "3. Assign confidence score (0-1)\n"
            "4. Explain reasoning\n\n"
            'Respond in JSON:\n{\n    "value": "extracted_value",\n    "confidence": float,\n'
            '    "alternatives": ["alternative1", "alternative2"],\n'
            '    "reasoning": "explanation",\n    "is_gibberish": boolean\n}\n'
        )
        
        response = await self.llm.generate(prompt)
        return json.loads(response)
    
    def _is_gibberish(self, text: str) -> bool:
        if not text or len(text) < 2:
            return True
        
        special_ratio = len([c for c in text if not c.isalnum() and not c.isspace()]) / max(len(text), 1)
        if special_ratio > 0.5:
            return True
        
        vowels = set("aeiouAEIOU")
        consonant_streak = 0
        for char in text:
            if char.isalpha():
                if char not in vowels:
                    consonant_streak += 1
                    if consonant_streak > 6:
                        return True
                else:
                    consonant_streak = 0
        
        return False
    
    async def _handle_uncertain_extraction(self, text: str, field: dict, initial_extraction: dict) -> dict:
        prompt = (
            f'The extracted value "{initial_extraction.get("value", "")}" for field '
            f'"{field.get("name")}" has low confidence or appears to be gibberish.\n\n'
            f"Context: {text[:500]}\n\n"
            f"Generate 4 possible interpretations:\n"
            "1. Most likely correction\n"
            "2. Second best interpretation\n"
            "3. Conservative/minimal interpretation\n"
            "4. Option to manually enter\n\n"
            "Consider OCR errors like:\n"
            "- 0/O confusion\n- 1/I/l confusion\n- 5/S confusion\n\n"
            'Format:\n{\n    "options": [\n'
            '        {{"label": "string", "value": "corrected_value", "reasoning": "why"}},\n'
            "        ...\n    ],\n"
            '    "recommendation": 0\n}\n'
        )
        
        mcq_data = await self.llm.generate(prompt)
        mcq = json.loads(mcq_data)
        
        initial_extraction["mcq_options"] = mcq.get("options", [])
        initial_extraction["recommended_option"] = mcq.get("recommendation", 0)
        initial_extraction["needs_review"] = True
        return initial_extraction
