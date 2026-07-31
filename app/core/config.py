from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ferretería Generative AI"
    app_version: str = "1.0.0"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    auto_create_tables: bool = True
    seed_demo_data: bool = True

    database_url: str = "sqlite+aiosqlite:///./ferreteria_genai.db"

    ai_provider: Literal["demo", "openai"] = "demo"
    embedding_provider: Literal["local", "openai"] = "local"
    openai_api_key: SecretStr | None = None
    openai_model: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    openai_max_retries: int = Field(default=2, ge=0, le=6)
    max_agent_turns: int = Field(default=4, ge=1, le=10)

    admin_api_key: SecretStr = SecretStr("development-admin-key-change-me")
    cors_origins: list[str] = [
        "http://localhost:4200",
        "http://localhost:3000",
    ]
    log_level: str = "INFO"

    chat_history_messages: int = Field(default=12, ge=2, le=50)
    input_max_characters: int = Field(default=2_000, ge=100, le=20_000)
    chunk_size: int = Field(default=900, ge=200, le=4_000)
    chunk_overlap: int = Field(default=150, ge=0, le=1_000)
    rag_top_k: int = Field(default=4, ge=1, le=20)
    local_embedding_dimensions: int = Field(default=256, ge=64, le=2_048)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_provider_configuration(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

        if self.ai_provider == "openai":
            if self.openai_api_key is None or not self.openai_api_key.get_secret_value():
                raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
            if not self.openai_model.strip():
                raise ValueError("OPENAI_MODEL is required when AI_PROVIDER=openai")

        if self.embedding_provider == "openai" and (
            self.openai_api_key is None or not self.openai_api_key.get_secret_value()
        ):
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
