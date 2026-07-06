from __future__ import annotations

import asyncio

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "doc_processor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """Async document processing via Celery"""
    from app.services.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(processor.process_document(document_id))
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
    finally:
        loop.close()
