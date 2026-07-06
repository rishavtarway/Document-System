from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserCorrection(Base):
    __tablename__ = "user_corrections"
    
    extraction_id: Mapped[str] = mapped_column(String(36), nullable=False)
    original_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    applied_to_model: Mapped[bool] = mapped_column(Boolean, default=False)
