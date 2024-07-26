from fastapi import APIRouter, Depends

from service.dialog_keeper import DialogueKeeperService, get_dialogue_keeper

router = APIRouter()


@router.get("/all")
async def get_all(
    skip: int = 0,
    limit: int = 10,
    dialog_keeper: DialogueKeeperService = Depends(get_dialogue_keeper),
):
    return await dialog_keeper.get_all(skip, limit)


@router.get("/fallbacks")
async def get_fallbacks(
    skip: int = 0,
    limit: int = 10,
    dialog_keeper: DialogueKeeperService = Depends(get_dialogue_keeper),
):
    return await dialog_keeper.get_fallbacks(skip, limit)
