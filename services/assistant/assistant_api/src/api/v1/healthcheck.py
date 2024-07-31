from fastapi import APIRouter, BackgroundTasks, Depends

from api.v1.webhook import webhook_alice
from assistant.alice import Alice, get_alice
from schema.alice import AliceRequest, Request
from service.dialog_controller import DialogController, get_dialog_controller
from service.dialog_keeper import DialogueKeeperService, get_dialogue_keeper
from service.services_interactor import (
    ServicesInteractor,
    get_service_interactor,
)

router = APIRouter()

router.prefix = "/healthcheck"


@router.get("/liveness")
async def liveness():
    return {"heathcheck": "OK"}


@router.get("/readiness")
async def readiness(
    background_tasks: BackgroundTasks,
    services_interactor: ServicesInteractor = Depends(get_service_interactor),
    assistant: Alice = Depends(get_alice),
    dialogue_controller: DialogController = Depends(get_dialog_controller),
    dialogue_keeper: DialogueKeeperService = Depends(get_dialogue_keeper),
):
    readiness = {
        "assistant_api": False,
        "movies_api": False,
    }
    alice_response = await webhook_alice(
        background_tasks=background_tasks,
        alice_request=AliceRequest(
            background_tasks=background_tasks,
            request=Request(command="healthcheck", type="HealthReadiness"),
            version="1.0",
        ),
        assistant=assistant,
        dialogue_controller=dialogue_controller,
        dialogue_keeper=dialogue_keeper,
    )
    readiness["assistant_api"] = bool(alice_response.response.text)
    readiness[
        "movies_api"
    ] = await services_interactor.movies_api.health_readiness()
    return readiness
