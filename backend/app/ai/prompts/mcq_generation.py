MCQ_GENERATION_PROMPT = """Create a user-friendly multiple choice question to clarify an uncertain extraction.

Field: {field_name}
Type: {field_type}

Extracted Value: "{extracted_value}"
Confidence: {confidence}
Reason for Uncertainty: {reasoning}

Document Context:
{document_context}

Generate:
1. A clear question for the user
2. 3-5 multiple choice options (include "None of the above"/"Manual entry")
3. Visual hints (like highlighting which part of document each option refers to)
4. Default recommendation

Make it conversational and helpful, not technical.

Format:
{{
    "question": "Which of these is the correct {field_name}?",
    "context_hint": "We found this near the top of the document",
    "options": [
        {{
            "id": 0,
            "label": "string",
            "value": "actual_value",
            "explanation": "why this might be correct"
        }}
    ],
    "default_selection": 0,
    "allow_custom_input": boolean
}}
"""
