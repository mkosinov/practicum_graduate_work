from beanie import Document
from pydantic import BaseModel

from core.settings import get_settings
from schema.alice import AliceRequest, AliceResponse


class Dialogue(Document):
    request: AliceRequest
    response: AliceResponse

    class Settings:
        name: str = get_settings().mongo_dialogue_collection


class Dialog(BaseModel):
    request: AliceRequest
    response: AliceResponse
