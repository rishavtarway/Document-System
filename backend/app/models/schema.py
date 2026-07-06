from __future__ import annotations

from sqlalchemy import Boolean, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocumentSchema(Base):
    __tablename__ = "document_schemas"
    
    document_type: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    schema_definition: Mapped[dict] = mapped_column(JSON, nullable=False)
    extraction_prompts: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_rules: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
