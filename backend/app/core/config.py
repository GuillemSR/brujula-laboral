from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "brujula-laboral"
    log_level: str = "INFO"
    allowed_origins: list[str] = ["http://localhost:8000", "http://localhost:5173"]

    aws_region: str = "eu-south-2"
    bedrock_model_id: str | None = None
    bedrock_embedding_model_id: str | None = None
    s3_temp_bucket: str | None = None
    s3_corpus_bucket: str | None = None
    kms_key_id: str | None = None

    rag_top_k: int = 6
    rag_min_score: float = 0.2
    rag_vector_backend: str = "local"

    store_user_prompts: bool = False
    store_model_responses: bool = False
    store_private_documents: bool = False
    temp_document_ttl_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
