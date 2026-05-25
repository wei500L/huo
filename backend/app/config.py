"""Application settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

__all__ = ["Settings", "get_settings"]


class Settings(BaseSettings):
    """Runtime settings for the backend."""

    model_config = SettingsConfigDict(extra="ignore", strict=True, env_file=None)

    app_name: str = "yes-boss-backend"
    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    llm_mode: Literal["mock", "openai_compat"] = "openai_compat"
    llm_endpoint: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_timeout_ms: int = 15_000
    llm_allow_fallback: bool = False
    settlement_max_concurrency: int = Field(default=4, ge=1)
    settlement_queue_max_size: int = Field(default=64, ge=1)
    settlement_task_timeout_ms: int = Field(default=45_000, ge=1_000)

    @model_validator(mode="after")
    def _validate_production_llm(self) -> Settings:
        if self.env != "prod":
            return self
        if self.llm_mode == "mock":
            raise ValueError("llm_mode=mock is not allowed when env=prod")
        missing = [
            name
            for name, value in (
                ("llm_endpoint", self.llm_endpoint),
                ("llm_api_key", self.llm_api_key),
                ("llm_model", self.llm_model),
            )
            if value is None or (isinstance(value, str) and not value.strip())
        ]
        if missing:
            raise ValueError(
                "production LLM configuration is incomplete: " + ", ".join(missing)
            )
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Keep settings construction explicit and test-friendly."""

        return (init_settings, env_settings, dotenv_settings, file_secret_settings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings singleton."""

    return Settings()
