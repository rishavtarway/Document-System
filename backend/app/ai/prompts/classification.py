CLASSIFICATION_PROMPT = """Analyze this document and classify its type.

Filename: {filename}
Content Preview: {text_preview}

Known Document Types:
{known_types}

Tasks:
1. Identify the document type (from known types or suggest new)
2. Provide confidence score (0-1)
3. List key indicators that led to this classification
4. If it's a new type, suggest a name and typical fields

Respond in JSON:
{{
    "document_type": "string",
    "confidence": float,
    "is_new_type": boolean,
    "indicators": ["string"],
    "suggested_fields": ["string"]
}}
"""

NEW_TYPE_SCHEMA_PROMPT = """Create a JSON schema for extracting data from this new document type: {new_type}

Sample content:
{sample_text}

Suggested fields: {suggested_fields}

Generate a schema with:
- Field names
- Data types
- Validation rules
- Confidence thresholds

Format:
{{
    "fields": [
        {{"name": "string", "type": "string", "required": boolean, "validation": "regex_or_rule"}}
    ]
}}
"""
