PATTERN_EXTRACTION_PROMPT = """A user corrected an extraction. Learn the pattern.

Document Type: {document_type}
Field: {field_name}
Wrong extraction: "{original_value}"
Correct value: "{corrected_value}"

Context:
{document_context}

Extract:
1. The text pattern/template that indicates this field
2. Common words/phrases nearby
3. Position indicators (near top, after "Total:", etc.)
4. Format patterns (regex if applicable)

Format:
{{
    "text": "natural language description of pattern",
    "keywords": ["nearby", "words"],
    "position_hint": "location description",
    "regex_pattern": "optional regex",
    "confidence_boost": float
}}
"""
