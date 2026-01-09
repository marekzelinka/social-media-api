from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: PostgresDsn
    secret_key: str
    access_token_expire_minutes: int


@lru_cache
def get_config() -> Settings:
    config = Settings.model_validate({})
    return config
