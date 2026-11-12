from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(BACKEND.parent / ".env", BACKEND / ".env"), extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    datos_dir: Path = Path(__file__).resolve().parent.parent / "data" / "platos"


@lru_cache
def get_settings() -> Settings:
    return Settings()
