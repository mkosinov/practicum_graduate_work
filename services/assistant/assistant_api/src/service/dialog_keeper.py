from functools import lru_cache
from schema.alice import AliceRequest, AliceResponse
from schema.mongo import Dialogue


class DialogueKeeperService:
    collection = Dialogue

    async def save(self, request: AliceRequest, response: AliceResponse):
        await self.collection.insert_one(
            self.collection(
                request=request,
                response=response
            )
        )


@lru_cache()
def get_dialogue_keeper():
    return DialogueKeeperService()