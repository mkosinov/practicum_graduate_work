import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = Field(default="movies")
    # Настройки Redis
    REDIS_HOST: str = Field(default="127.0.0.1")
    REDIS_PORT: int = Field(default=6379)
    CACHE_EXPIRE_IN_SECONDS: int = 60 * 5  # 5 минут
    # Настройки Elasticsearch
    ELASTIC_HOST: str = Field(default="127.0.0.1", alias="ES_HOST")
    ELASTIC_PORT: int = Field(default=9200, alias="ES_PORT")
    STANDART_PAGE_SIZE: int = 50
    DESCRIPTION: str = (
        "Информация о фильмах, жанрах и людях, участвовавших в создании"
        "кинопроизведения"
    )
    VERSION: str = "0.1.0"
    OPEN_API_DOCS_URL: str = "/api/openapi"
    OPENAPI_URL: str = "/api/openapi.json"

    # JWT
    JWT_SECRET: SecretStr = Field(default="Secret encode token")
    JWT_CODE: str = "utf-8"


settings = Settings()
