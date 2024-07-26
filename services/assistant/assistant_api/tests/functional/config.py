from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='./functional/.env', extra='ignore')

    service_url: str = Field(default=...)

    kafka_host: str = Field(default=...)
    kafka_port: int = Field(default=...)
    kafka_topic: str = Field(default=...)


test_settings = TestSettings()
