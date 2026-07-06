from __future__ import annotations

from sqlalchemy import Column, Float, Integer, String, Text

from app.models.base import Base


class ExtractionPattern(Base):
    __tablename__ = "extraction_patterns"
    
    document_type: str = mapped_column(String(100), nullable=False)
    field_name: str = mapped_column(String(100), nullable=False)
    pattern_text: str | None = mapped_column(Text, nullable=True)
    keywords: list | None = mapped_column(nullable=True)
    position_hint: str | None = mapped_column(String(255), nullable=True)
    regex_pattern: str | None = mapped_column(String(512), nullable=True)
    confidence_boost: float = mapped_column(Float, default=0.1)
    success_count: int = mapped_column(Integer, default=0)
    example_value: str | None = mapped_column(String(255), nullable=True)
    # embedding handled by pgvector externally
