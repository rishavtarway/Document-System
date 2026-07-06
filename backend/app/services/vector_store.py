from __future__ import annotations

import json
from typing import Optional

from app.ai.llm_client import EmbeddingClient
from app.core.database import SessionLocal
from app.models.pattern import ExtractionPattern


class VectorStore:
    """Vector store for extraction pattern memory using pgvector"""
    
    async def find_similar(self, document_type: str, query_text: str, limit: int = 5) -> list[dict]:
        query_embedding = await EmbeddingClient.embed(query_text)
        
        db = SessionLocal()
        try:
            from sqlalchemy import text
            sql = text("""
                SELECT id, document_type, field_name, pattern_text, example_value,
                       success_count, confidence_boost, keywords, position_hint,
                       1 - (embedding <=> :query_embedding) as similarity
                FROM extraction_patterns
                WHERE document_type = :doc_type
                ORDER BY similarity DESC
                LIMIT :limit
            """)
            
            result = db.execute(sql, {
                "query_embedding": json.dumps(query_embedding),
                "doc_type": document_type,
                "limit": limit,
            })
            
            patterns = []
            for row in result:
                patterns.append({
                    "id": row.id,
                    "field_name": row.field_name,
                    "example_value": row.example_value,
                    "pattern_text": row.pattern_text,
                    "keywords": row.keywords or [],
                    "position_hint": row.position_hint,
                    "confidence_boost": row.confidence_boost,
                    "similarity": float(row.similarity) if row.similarity else 0,
                })
            return patterns
        finally:
            db.close()
    
    async def add_pattern(self, document_type: str, field_name: str, pattern_text: str, embedding: list[float], example_value: str):
        db = SessionLocal()
        try:
            from sqlalchemy import text
            sql = text("""
                INSERT INTO extraction_patterns 
                    (id, document_type, field_name, pattern_text, embedding, example_value, success_count, created_at, updated_at)
                VALUES 
                    (:id, :doc_type, :field_name, :pattern_text, :embedding::vector, :example_value, 1, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    success_count = extraction_patterns.success_count + 1,
                    updated_at = NOW()
            """)
            
            import uuid
            db.execute(sql, {
                "id": str(uuid.uuid4()),
                "doc_type": document_type,
                "field_name": field_name,
                "pattern_text": pattern_text,
                "embedding": json.dumps(embedding),
                "example_value": example_value,
            })
            db.commit()
        finally:
            db.close()
