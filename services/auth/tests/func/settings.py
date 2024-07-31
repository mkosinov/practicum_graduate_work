import os
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir="/run/secrets")
    # Postgres
    pg_host: str = Field(alias="auth_postgres_host")
    pg_port: int = Field(alias="auth_postgres_port")
    pg_user: SecretStr = Field(alias="auth_postgres_user")
    pg_password: SecretStr = Field(alias="auth_postgres_password")
    pg_db: SecretStr = Field(alias="auth_postgres_db")

    # Redis
    auth_redis_host: str = Field()
    auth_redis_port: int = Field()

    # FastAPI
    auth_fastapi_host: str = Field()
    auth_fastapi_port: int = Field()

    # Requests
    BASE_HEADERS: dict = {
        "content-type": "application/json",
        "accept": "application/json",
    }
    LOGIN_HEADERS: dict = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    jwt_code: str = Field(default="utf-8")
    jwt_secret: SecretStr = Field(alias="auth_jwt_secret")

    @property
    def api_url(self) -> str:
        return (
            f"http://{self.auth_fastapi_host}:{self.auth_fastapi_port}/api/v1"
        )


@lru_cache(maxsize=1)
def get_settings():
    return Settings()
