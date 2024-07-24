from pprint import pprint

from assistant.alice import Alice, get_alice
from core.logger import Logger, get_logger
from fastapi import APIRouter, Depends
from schema.alice import AliceRequest, AliceResponse
from service.dialog_controller import DialogController, get_dialog_controller
from service.dialog_keeper import get_dialogue_keeper, DialogueKeeperService

router = APIRouter(prefix="/webhook")


@router.post(path="/alice", response_model=AliceResponse)
async def webhook_alice(
    alice_request: AliceRequest,
    assistant: Alice = Depends(get_alice),
    dialogue_controller: DialogController = Depends(get_dialog_controller),
    logger: Logger = Depends(get_logger),
    dialogue_keeper: DialogueKeeperService = Depends(get_dialogue_keeper)
) -> AliceResponse:
    # logger.debug(alice_request)
    response = await dialogue_controller.process_assistant_request(
        request=alice_request, assistant=assistant
    )
    await dialogue_keeper.save(alice_request, response)

    return response


primer = {
    "sessionId": "86024848-c12b-4056-b58b-93c69b412314",
    "messageId": 0,
    "uuid": {
        "userChannel": "B2С",
        "sub": "d2d6da62-6bdd-452b-b5dd-a145090075ba",
        "userId": 123,
    },
    "messageName": "ANSWER_TO_USER",
    "payload": {
        "pronounceText": "Привет! Чем я могу помочь?",
        "pronounceTextType": "application/text",
        "emotion": {"emotionId": "oups"},
        "items": [{"bubble": {}, "card": {}, "command": {}}],
        "suggestions": {
            "buttons": [{"title": "string", "action": {}, "actions": [{}]}]
        },
        "auto_listening": True,
        "finished": True,
        "device": {
            "platformType": "ANDROID",
            "platformVersion": "1.0.2",
            "surface": "SBOL",
            "surfaceVersion": "1.0.2",
            "devicesId": "string",
            "features": {"appTypes": ["DIALOG"]},
            "capabilities": {
                "screen": {
                    "available": True,
                    "width": 1080,
                    "height": 1920,
                    "scale_factor": 2.5,
                },
                "mic": {"available": True},
                "speak": {"available": True},
            },
            "additionalInfo": {},
        },
        "intent": "string",
        "asr_hints": {},
    },
}


@router.post(path="/salut")
def webhook_salut(webhook: dict):
    get_logger().debug(webhook)
    pprint(webhook)
    a = {}
    a["sessionId"] = webhook["sessionId"]
    a["messageId"] = webhook["messageId"]
    a["uuid"] = webhook["uuid"]
    a["messageName"] = "ANSWER_TO_USER"
    a["payload"] = {"pronounceText": "Привет! Это тест салюта"}
    return a
