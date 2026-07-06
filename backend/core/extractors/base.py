from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.ai_client import AIClient


class BaseExtractor(ABC):
    """Base class for document-type-specific extractors.
    To add a new document type, subclass this and register in __init__.py.
    """

    @property
    @abstractmethod
    def document_type(self) -> str:
        ...

    @property
    @abstractmethod
    def extraction_prompt(self) -> str:
        ...

    @property
    @abstractmethod
    def validation_rules(self) -> dict:
        """Return deterministic validation rules keyed by field name.
        Each rule is a dict with keys: 'required' (bool), 'type' (str),
        'pattern' (optional regex), 'range' (optional [min, max]).
        """
        ...

    @property
    def confidence_boosters(self) -> list[str]:
        """List of fields whose presence boosts overall confidence."""
        return []

    def extract(self, text_content: str, image_data: Optional[str] = None) -> tuple[dict, float]:
        raw = AIClient.extract_structured(
            prompt=self.extraction_prompt,
            response_schema={"type": "object"},
            image_data=image_data,
        )
        return self._post_process(raw)

    def _post_process(self, data: dict) -> tuple[dict, float]:
        cleaned = self._clean(data)
        confidence = self._calculate_confidence(cleaned)
        return cleaned, confidence

    def _clean(self, data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None and v != "" and v != []}

    def _calculate_confidence(self, data: dict) -> float:
        rules = self.validation_rules
        if not rules:
            return 0.5

        required_fields = [f for f, r in rules.items() if r.get("required")]
        if not required_fields:
            return 0.8

        present = sum(1 for f in required_fields if f in data)
        return round(present / len(required_fields), 2)
