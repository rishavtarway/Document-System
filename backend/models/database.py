from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Text, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(512), nullable=False)
    content_type = Column(String(128), nullable=True)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Float, default=0)
    document_type = Column(String(64), nullable=True)
    status = Column(String(32), default="uploaded")
    extraction_data = Column(JSON, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    validations = Column(JSON, nullable=True)
    corrected_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
