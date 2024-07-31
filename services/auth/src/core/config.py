from __future__ import annotations, nested_scopes

import os
from functools import lru_cache

from fastapi.security import OAuth2PasswordBearer
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",
    )

    # Postgres
    pg_host: str = Field(alias="auth_postgres_host", default="auth.db")
    pg_port: int = Field(alias="auth_postgres_port", default="9999")
    pg_user: SecretStr = Field(
        alias="auth_postgres_user", default="Postgres_user"
    )
    pg_password: SecretStr = Field(
        alias="auth_postgres_password", default="Postgres_pasword"
    )
    pg_db: SecretStr = Field(alias="auth_postgres_db", default="Auth_DB")

    # Redis
    auth_redis_host: str = Field(default="auth.cache")
    auth_redis_port: int = Field(default="9998")

    # Swagger-docs config
    url_prefix: str = "/api/v1"
    project_name: str = Field(default="Auth-service")
    version: str = "0.1.0"
    description: str = "Authetification service."
    open_api_docs_url: str = "/auth/docs"
    open_api_url: str = "/auth/openapi.json"

    # # FastAPI
    auth_fastapi_host: str = Field(default="auth.app")
    auth_fastapi_port: int = Field(default="8000")

    # Jaeger
    jaeger_service_name: str = Field(
        alias="auth_jaeger_service_name", default="auth_service"
    )
    enable_tracing: bool = Field(alias="auth_enable_tracing", default=True)
    jaeger_host: str = Field(alias="auth_jaeger_host", default="auth.jaeger")
    jaeger_port: int = Field(alias="auth_jaeger_port", default="6831")

    # JWT
    refresh_token_max_length: int = 300
    jwt_secret: SecretStr = Field(alias="auth_jwt_secret")
    jwt_code: str = Field(default="utf-8")
    # Acess token lifetime in hours
    acess_token_lifetime: int = Field(default=2)
    # Acess token lifetime in days
    refresh_token_lifetime: int = Field(default=14)

    # OAuth2.0
    oauth_base_url: str = Field(default="http://localhost/api/v1/oauth")
    oauth_yandex_client_id: SecretStr = Field(
        alias="auth_oauth_yandex_client_id"
    )
    oauth_yandex_client_secret: SecretStr = Field(
        alias="auth_oauth_yandex_client_secret"
    )
    oauth_vk_client_id: SecretStr = Field(alias="auth_oauth_vk_client_id")
    oauth_vk_client_secret: SecretStr = Field(
        alias="auth_oauth_vk_client_secret"
    )

    # Validation config
    role_title_min_length: int = 3
    role_title_max_length: int = 50
    role_title_pattern: str = ("^[A-Za-z0-9_-]{%s,%s}$") % (
        role_title_min_length,
        role_title_max_length,
    )
    role_description_max_length: int = 255

    login_min_length: int = 5
    login_max_length: int = 50
    login_pattern: str = ("^[A-Za-z0-9_-]{%s,%s}$") % (
        login_min_length,
        login_max_length,
    )

    email_min_length: int = 8
    email_max_length: int = 50

    password_min_length: int = 5
    password_max_length: int = 50
    hashed_password_max_length: int = 255

    first_name_min_length: int = 3
    first_name_max_length: int = 255
    last_name_min_length: int = 3
    last_name_max_length: int = 255
    fingerprint_max_length: int = 50

    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
        tokenUrl=url_prefix + "/auth/login",
        scopes={
            "auth_admin": "Admin to manage roles and access",
            "subscriber": "User who paid subscription",
        },
        auto_error=False,
    )

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user.get_secret_value()}:{self.pg_password.get_secret_value()}@{self.pg_host}:{self.pg_port}/{self.pg_db.get_secret_value()}"


@lru_cache(maxsize=1)
def get_settings():
    return Settings()
