from __future__ import annotations

from sqlalchemy import Boolean, Column, String, Text

from app.models.base import Base


class UserCorrection(Base):
    __tablename__ = "user_corrections"
    
    extraction_id: str = mapped_column(String(36), nullable=False)
    original_value: str | None = mapped_column(Text, nullable=True)
    corrected_value: str | None = mapped_column(Text, nullable=True)
    field_name: str = mapped_column(String(100), nullable=False)
    document_type: str = mapped_column(String(100), nullable=False)
    applied_to_model: bool = mapped_column(Boolean, default=False)
