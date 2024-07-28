from functools import lru_cache

from opentelemetry import trace

from schema.alice import AliceRequest, AliceResponse
from schema.mongo import Dialogue

tracer = trace.get_tracer(__name__)


class DialogueKeeperService:
    collection = Dialogue

    @tracer.start_as_current_span("dialog_keeper.save")
    async def save(self, request: AliceRequest, response: AliceResponse):
        await self.collection.insert_one(
            self.collection(request=request, response=response)
        )

    @tracer.start_as_current_span("dialog_keeper.get_all")
    async def get_all(self, skip: int, limit: int):
        return await self.collection.find(
            skip=skip,
            limit=limit,
        ).to_list()

    @tracer.start_as_current_span("dialog_keeper.get_fallbacks")
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
