from core.logger import get_logger
from fastapi import APIRouter
from schema.alice import AliceRequest, AliceResponse, Response

router = APIRouter(prefix="/alice")


@router.post(path="/webhook", response_model=AliceResponse)
def webhook(webhook: AliceRequest) -> AliceResponse:
    get_logger().debug(webhook)
    response = Response(text="Hello, World!")
    return AliceResponse(response=response, version="1.0")
