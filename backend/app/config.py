"""Application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

__all__ = ["Settings", "get_settings"]


class Settings(BaseSettings):
    """Runtime settings for the backend."""

    model_config = SettingsConfigDict(extra="ignore", strict=True, env_file=None)

    app_name: str = "yes-boss-backend"
    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    llm_mode: Literal["mock", "openai_compat"] = "mock"
    llm_endpoint: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_timeout_ms: int = 15_000
    settlement_max_concurrency: int = 4

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

        return (init_settings,)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings singleton."""

    return Settings()
