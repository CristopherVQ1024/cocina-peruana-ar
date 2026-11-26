from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(BACKEND.parent / ".env", BACKEND / ".env"), extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_models: str = "gemini-3.1-flash-lite,gemini-3.6-flash"
    # espera por intento y modelo
    gemini_timeout_s: float = 8
    gemini_timeout_traducir_s: float = 15
    # tope de todos los intentos juntos, menor que los 60 s del proxy_read_timeout de Nginx
    gemini_timeout_total_s: float = 55
    datos_dir: Path = Path(__file__).resolve().parent.parent / "data" / "platos"


@lru_cache
def get_settings() -> Settings:
    return Settings()
