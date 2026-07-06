from __future__ import annotations

import json

from app.ai.llm_client import LLMClient


class MCQGenerator:
    def __init__(self):
        self.llm = LLMClient()
    
    async def generate_clarification_dialog(self, extraction: dict, document_context: str, field_definition: dict) -> dict:
        prompt = (
            "Create a user-friendly multiple choice question to clarify an uncertain extraction.\n\n"
            f"Field: {field_definition.get('name', 'unknown')}\n"
            f"Type: {field_definition.get('type', 'string')}\n\n"
            f'Extracted Value: "{extraction.get("value", "")}"\n'
            f'Confidence: {extraction.get("confidence", 0.0)}\n'
            f'Reason for Uncertainty: {extraction.get("reasoning", "Low confidence")}\n\n'
            f"Document Context:\n{document_context[:500]}\n\n"
            "Generate:\n"
            "1. A clear question for the user\n"
            "2. 3-5 multiple choice options (include 'None of the above'/'Manual entry')\n"
            "3. Visual hints\n"
            "4. Default recommendation\n\n"
            "Make it conversational and helpful, not technical.\n\n"
            'Format:\n{\n    "question": "Which of these is the correct {field_name}?",\n'
            '    "context_hint": "We found this near the top of the document",\n'
            '    "options": [\n        {{\n            "id": 0,\n            "label": "string",\n'
            '            "value": "actual_value",\n            "explanation": "why this might be correct"\n'
            "        }}\n    ],\n"
            '    "default_selection": 0,\n    "allow_custom_input": boolean\n}\n'
        )
        
        response = await self.llm.generate(prompt)
        return json.loads(response)
    
    async def generate_batch_dialogs(self, uncertain_extractions: list[dict], document_text: str, schema: dict) -> list[dict]:
        dialogs = []
        fields_map = {f["name"]: f for f in schema.get("fields", [])}
        
        for extraction in uncertain_extractions:
            field_def = fields_map.get(extraction.get("field_name", ""), {})
            dialog = await self.generate_clarification_dialog(extraction, document_text, field_def)
            dialogs.append({
                "extraction_id": extraction.get("id"),
                "field_name": extraction.get("field_name"),
                "original_value": extraction.get("value"),
                "dialog": dialog,
            })
        
        return dialogs
