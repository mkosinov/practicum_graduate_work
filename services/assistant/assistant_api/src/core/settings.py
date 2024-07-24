import logging
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Tuple, Type

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class Settings(BaseSettings):
    workdir: ClassVar[Path] = Path(__file__).parent.parent
    model_config = SettingsConfigDict(
        toml_file=workdir.joinpath("config.toml"),
        secrets_dir="/run/secrets",
        env_file=workdir.parent.parent.joinpath(".env"),
        extra="ignore",
    )

    debug: bool = False
    logs_dir: Path = workdir.joinpath("logs")
    logging_level: int = logging.INFO
    mongo_dsn_1: str = Field(default=...)
    mongo_dsn_2: str = Field(default=...)
    mongo_db_name: str = Field(default=...)
    mongo_dialogue_collection: str = Field(default=...)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )

settings = Settings()

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
