from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

##################
# Alice Enums #
##################

class CardType(StrEnum):
    BigImage = "BigImage"
    ItemsList = "ItemsList"
    ImageGallery = "ImageGallery"


class RequestType(StrEnum):
    SimpleUtterance = "SimpleUtterance"
    ButtonPressed = "ButtonPressed"
    AudioPlayerPlaybackStarted = "AudioPlayer.PlaybackStarted"
    AudioPlayerPlaybackFinished = "AudioPlayer.PlaybackFinished"
    AudioPlayerPlaybackNearlyFinished = "AudioPlayer.PlaybackNearlyFinished"
    AudioPlayerPlaybackStopped = "AudioPlayer.PlaybackStopped"
    AudioPlayerPlaybackFailed = "AudioPlayer.PlaybackFailed"
    PurchaseConfirmation = "Purchase.Confirmation"
    ShowPull = "Show.Pull"


class EntityType(StrEnum):
    GEO = "YANDEX.GEO"
    FIO = "YANDEX.FIO"
    NUMBER = "YANDEX.NUMBER"
    DATETIME = "YANDEX.DATETIME"


##################
# Alice Request #
##################

class State(BaseModel):
    session: Optional[dict] = None
    user: Optional[dict] = None
    application: Optional[dict] = None


class Application(BaseModel):
    application_id: Optional[str] = None


class User(BaseModel):
    user_id: Optional[str] = None
    access_token: Optional[str] = None


class Session(BaseModel):
    message_id: Optional[int] = None
    session_id: Optional[str] = None
    skill_id: Optional[str] = None
    user_id: Optional[str] = None  # deprecated
    user: Optional[User] = None
    application: Optional[Application] = None
    new: bool = False


class Token(BaseModel):
    start: int
    end: int


class Entity(BaseModel):
    tokens: Optional[Token] = None
    type: Optional[EntityType] = None
    value: Optional[dict] = None


class Nlu(BaseModel):
    tokens: Optional[List[str]] = None
    entities: Optional[List[dict]] = None
    intents: Optional[dict] = None


class Request(BaseModel):
    type: RequestType
    command: str
    original_utterance: Optional[str] = None
    markup: Optional[dict] = None
    payload: Optional[dict] = None
    nlu: Optional[Nlu] = None


class Interfaces(BaseModel):
    screen: Optional[dict] = None
    account_linking: Optional[dict] = None
    audio_player: Optional[dict] = None


class Meta(BaseModel):
    locale: Optional[str] = None
    timezone: Optional[str] = None
    client_id: Optional[str] = None
    interfaces: Optional[Interfaces] = None


class AliceRequest(BaseModel):
    meta: Optional[Meta] = None
    request: Request
    session: Optional[Session] = None
    state: Optional[State] = None
    version: str


##################
# Alice Response #
##################


class Button(BaseModel):
    title: str
    url: Optional[str] = None
    payload: Optional[dict] = None
    hide: bool = False


class Card(BaseModel):
    type: CardType


class InnerResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str
    tts: Optional[str] = None
    card: Optional[Card] = None
    buttons: Optional[list[Button]] = None
    end_session: bool = False
    directives: Optional[dict] = None
    show_item_meta: Optional[dict] = (
        None  # Обязательный параметр только для сценария утреннего шоу.
    )

    @field_validator('text')
    def validate_text_length(cls, text):
        if len(text) > 300:
            return text[0:300]
        return text

class Analytics(BaseModel):
    events: list[dict] = []


class AliceResponse(BaseModel):
    response: InnerResponse
    session_state: Optional[dict] = None
    user_state_update: Optional[dict] = None
    application_state: Optional[dict] = None
    analytics: Optional[Analytics] = None
    version: str
