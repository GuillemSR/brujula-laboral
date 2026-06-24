from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "brujula-laboral"
    log_level: str = "INFO"
    allowed_origins: list[str] = ["http://localhost:8000", "http://localhost:5173"]

    ai_provider: Literal["bedrock", "mock", "ollama"] = "bedrock"
    aws_region: str = "eu-south-2"
    bedrock_region: str | None = None
    bedrock_model_id: str | None = None
    bedrock_embedding_model_id: str | None = None
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model_id: str = "qwen2.5:1.5b"
    ollama_timeout_seconds: float = 120.0
    s3_temp_bucket: str | None = None
    s3_corpus_bucket: str | None = None
    kms_key_id: str | None = None

    rag_top_k: int = 6
    rag_min_score: float = 0.2
    rag_vector_backend: str = "local"

    store_user_prompts: bool = False
    store_model_responses: bool = False
    store_private_documents: bool = False
    temp_document_storage: Literal["auto", "memory", "s3"] = "auto"
    temp_document_ttl_minutes: int = 30
    temp_document_max_bytes: int = 5 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
