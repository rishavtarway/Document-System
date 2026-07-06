from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024))
    file_size: Mapped[int] = mapped_column(default=0)
    content_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    type_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    is_new_type: Mapped[bool] = mapped_column(Boolean, default=False)
    suggested_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    upload_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")


class Extraction(Base):
    __tablename__ = "extractions"
    
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    extracted_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    extraction_method: Mapped[str] = mapped_column(String(50), default="ai")
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_gibberish: Mapped[bool] = mapped_column(Boolean, default=False)
    
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    corrected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    alternatives: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    document = relationship("Document", back_populates="extractions")
    mcq_dialogues = relationship("MCQDialogue", back_populates="extraction", cascade="all, delete-orphan")


class MCQDialogue(Base):
    __tablename__ = "mcq_dialogues"
    
    extraction_id: Mapped[str] = mapped_column(String(36), ForeignKey("extractions.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[dict] = mapped_column(JSON)
    context_hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_selection: Mapped[int] = mapped_column(default=0)
    allow_custom_input: Mapped[bool] = mapped_column(default=True)
    
    user_selection: Mapped[Optional[int]] = mapped_column(nullable=True)
    user_custom_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    confidence_before: Mapped[float] = mapped_column(Float)
    confidence_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    resolved: Mapped[bool] = mapped_column(default=False)
    
    extraction = relationship("Extraction", back_populates="mcq_dialogues")
