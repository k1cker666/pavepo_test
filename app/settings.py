from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="psql_", env_file_encoding="utf-8", extra="ignore",
    )
    dbname: str
    user: str
    password: str
    host: str
    port: str

    def get_conninfo(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password}@{self.host}:{self.port}/{self.dbname}"
        )

class YandexSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="yandex_", env_file_encoding="utf-8", extra="ignore",
    )
    client_id: str
    client_secret: str
    redirect_uri: str
    token_url: str
    userinfo_url: str
    authrize_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="app_", env_file_encoding="utf-8", extra="ignore",
    )
    secret_key: str
    algorithm: str
    audio_storage_path: Path = BASE_DIR / "audio_storage"

    postgresql: PostgreSQLSettings = PostgreSQLSettings()
    yandex: YandexSettings = YandexSettings()


settings = Settings()

if not Path.is_dir(settings.audio_storage_path):
    Path.mkdir(settings.audio_storage_path)
