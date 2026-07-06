from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ExtractionPattern(Base):
    __tablename__ = "extraction_patterns"
    
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    position_hint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    regex_pattern: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    confidence_boost: Mapped[float] = mapped_column(Float, default=0.1)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    example_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # embedding handled by pgvector externally
