EXTRACTION_PROMPT = """Extract the field '{field_name}' from this {document_type}.

Field Definition:
- Type: {field_type}
- Validation: {validation}
- Required: {required}

Historical Examples:
{context_examples}

Document Text:
{document_text}

Instructions:
1. Extract the most likely value for this field
2. If text is unclear/gibberish, provide best guesses with alternatives
3. Assign confidence score (0-1)
4. Explain reasoning

Respond in JSON:
{{
    "value": "extracted_value",
    "confidence": float,
    "alternatives": ["alternative1", "alternative2"],
    "reasoning": "explanation",
    "is_gibberish": boolean
}}
"""

FULL_EXTRACTION_PROMPT = """You are a document data extraction specialist. Extract ALL fields from this {document_type} document.

Schema to populate:
{schema_json}

Historical patterns for this document type:
{historical_context}

Document Text:
{document_text}

Instructions:
1. Extract every field from the schema
2. If a field is not present, set it to null
3. Assign confidence score for each field (0-1)
4. Flag gibberish or unclear text
5. Provide reasoning for uncertain fields

Respond in JSON with all fields populated.
"""

GIBBERISH_CORRECTION_PROMPT = """The extracted value "{extracted_value}" for field "{field_name}" has low confidence or appears to be gibberish.

Context: {document_context}

Generate {num_options} possible interpretations:
1. Most likely correction
2. Second best interpretation
3. Conservative/minimal interpretation
4. Option to manually enter

Consider OCR errors like:
- 0/O confusion
- 1/I/l confusion
- 5/S confusion
- Special character issues

Format:
{{
    "options": [
        {{"label": "string", "value": "corrected_value", "reasoning": "why"}},
        ...
    ],
    "recommendation": 0
}}
"""
