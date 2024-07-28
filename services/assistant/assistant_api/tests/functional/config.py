from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # model_config = SettingsConfigDict(env_file='./functional/.env', extra='ignore')

    assistant_api_host: str = "localhost"
    assistant_api_port: int = 80

    # mongo
    mongo_dsn_1: str = "mongodb://localhost:27019"
    mongo_dsn_2: str = "mongodb://localhost:27020"
    mongo_db_name: str = "AliceDB"
    mongo_dialogue_collection: str = "dialogueCollection"

    @property
    def assistant_api_url(self) -> str:
        return f"http://{self.assistant_api_host}:{self.assistant_api_port}"


test_settings = TestSettings()
