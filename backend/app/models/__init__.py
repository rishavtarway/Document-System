from __future__ import annotations

from app.models.base import Base
from app.models.document import Document
from app.models.extraction import Extraction, MCQDialogue
from app.models.schema import DocumentSchema
from app.models.correction import UserCorrection
from app.models.pattern import ExtractionPattern

__all__ = [
    "Base",
    "Document", "Extraction", "MCQDialogue",
    "DocumentSchema", "UserCorrection", "ExtractionPattern",
]
