import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_prefix="psql_", env_file_encoding="utf-8", extra="ignore",
    )
    dbname: str
    user: str
    password: str
    host: str
    port: str

    def get_conninfo(self):
        conninfo = (
            f"postgresql+asyncpg://{self.user}:"
            + f"{self.password}@{self.host}:{self.port}/{self.dbname}"
        )
        return conninfo


class YandexSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_prefix="yandex_", env_file_encoding="utf-8", extra="ignore",
    )
    client_id: str
    client_secret: str
    redirect_uri: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_prefix="app_", env_file_encoding="utf-8", extra="ignore",
    )
    secret_key: str
    algorithm: str
    audio_storage_path: Path = BASE_DIR / "audio_storage"

    postgresql: PostgreSQLSettings = PostgreSQLSettings()
    yandex: YandexSettings = YandexSettings()


settings = Settings()

if not os.path.isdir(settings.audio_storage_path):
    os.mkdir(settings.audio_storage_path)