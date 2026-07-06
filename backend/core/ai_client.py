from __future__ import annotations

import json
from typing import Optional

from openai import OpenAI, APIError, RateLimitError

from core.config import settings


class AIClient:
    _instance: Optional[OpenAI] = None

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._instance is None:
            if not settings.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is not set. Set it in .env or environment."
                )
            cls._instance = OpenAI(api_key=settings.openai_api_key)
        return cls._instance

    @classmethod
    def extract_structured(cls, prompt: str, response_schema: dict, image_data: Optional[str] = None) -> dict:
        client = cls.get_client()
        messages = [{"role": "system", "content": prompt}]

        content_parts = []
        if image_data:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"}
            })

        content_parts.append({"type": "text", "text": prompt})
        messages.append({"role": "user", "content": content_parts})

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=4096,
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        except (json.JSONDecodeError, APIError, RateLimitError) as e:
            raise RuntimeError(f"AI extraction failed: {e}") from e

    @classmethod
    def classify_document(cls, text_content: str) -> tuple[str, float]:
        client = cls.get_client()
        prompt = (
            "You are a document classifier. Analyze the following document text and "
            "classify it into one of these categories: invoice, purchase_order, contract, resume, or unknown. "
            "Return a JSON object with keys 'document_type' (string) and 'confidence' (float 0-1). "
            "Base your classification on the content, structure, and keywords in the text.\n\n"
            f"Document text:\n{text_content[:8000]}"
        )

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=200,
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("document_type", "unknown"), float(result.get("confidence", 0.0))
        except Exception as e:
            return "unknown", 0.0
