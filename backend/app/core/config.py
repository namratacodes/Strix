"""
Centralized application configuration.

Why pydantic-settings:
- Reads from environment variables (and a local .env file in dev) with full
  type validation, so a missing/malformed env var fails fast at startup
  instead of causing a mysterious bug three layers deep at request time.
- Keeps config access to a single injectable object (`get_settings()`)
  rather than scattering `os.getenv()` calls across the codebase.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App metadata ---
    app_name: str = "STRIX"
    environment: str = "development"  # development | staging | production
    debug: bool = True

    # --- API ---
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    # Comma-separated origins allowed to call this API. In dev this is the
    # Vite dev server; in production it will be the Vercel deployment URL.
    cors_origins: str = "http://localhost:5173"

    # --- Database (wired in a later milestone) ---
    database_url: str | None = None

    # --- Auth (wired in a later milestone) ---
    google_client_id: str | None = None
    google_client_secret: str | None = None
    session_secret_key: str = "dev-secret-change-me"

    # --- LLM (wired in a later milestone) ---
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. FastAPI's dependency-injection system will
    call this once and reuse the same Settings instance across requests,
    rather than re-parsing environment variables on every call.
    """
    return Settings()
