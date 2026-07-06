from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    app_name: str = "Document Intelligence System"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    
    database_url: str = "postgresql://docproc:docproc@db:5432/docprocessor"
    redis_url: str = "redis://redis:6379/0"
    
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "documents"
    
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    openrouter_api_key: str = ""
    use_openrouter: bool = False
    
    ocr_engine: str = "tesseract"
    azure_doc_intelligence_endpoint: str = ""
    azure_doc_intelligence_key: str = ""
    
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 20
    allowed_extensions: str = ".pdf,.png,.jpg,.jpeg,.tiff,.tif"
    
    confidence_threshold_auto: float = 0.8
    confidence_threshold_mcq: float = 0.5
    max_mcq_options: int = 4
    
    min_corrections_for_retrain: int = 100
    similarity_threshold: float = 0.75
    embedding_dim: int = 1536
    
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH = UPLOAD_PATH.parent
DATA_PATH.mkdir(parents=True, exist_ok=True)
