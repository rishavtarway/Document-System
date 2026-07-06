from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, JSON, String, Text

from app.models.base import Base


class DocumentSchema(Base):
    __tablename__ = "document_schemas"
    
    document_type: str = mapped_column(String(100), unique=True, nullable=False)
    version: int = mapped_column(Integer, default=1)
    schema_definition: dict = mapped_column(JSON, nullable=False)
    extraction_prompts: dict = mapped_column(JSON, nullable=False)
    validation_rules: dict = mapped_column(JSON, nullable=False)
    is_active: bool = mapped_column(Boolean, default=True)
