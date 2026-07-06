from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: str = "sqlite:///./data/documents.db"
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 20
    allowed_extensions: str = ".pdf,.png,.jpg,.jpeg,.tiff,.txt,.docx"
    openai_model: str = "gpt-4o"
    extraction_confidence_threshold: float = 0.7
    classification_confidence_threshold: float = 0.6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

UPLOAD_PATH = Path(settings.upload_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH = Path(settings.upload_dir).parent
DATA_PATH.mkdir(parents=True, exist_ok=True)
