from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    assistant_api_host: str = "localhost"
    assistant_api_port: int = 80

    @property
    def assistant_api_url(self) -> str:
        return f"http://{self.assistant_api_host}:{self.assistant_api_port}"


test_settings = TestSettings()
