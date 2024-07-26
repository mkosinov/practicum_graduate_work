from functools import lru_cache

from schema.alice import AliceRequest, AliceResponse
from schema.mongo import Dialogue


class DialogueKeeperService:
    collection = Dialogue

    async def save(self, request: AliceRequest, response: AliceResponse):
        await self.collection.insert_one(
            self.collection(request=request, response=response)
        )

    async def get_all(self, skip: int, limit: int):
        return await self.collection.find(
            skip=skip,
            limit=limit,
        ).to_list()

    async def get_fallbacks(self, skip: int, limit: int):
        return await self.collection.find(
            self.collection.request.request.nlu.intents == {},
            self.collection.request.request.command != "",
            skip=skip,
            limit=limit,
        ).to_list()


@lru_cache()
def get_dialogue_keeper():
    return DialogueKeeperService()
