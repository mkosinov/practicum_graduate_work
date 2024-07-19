from functools import lru_cache

from schema.alice import AliceRequest, AliceResponse


class ReplyGenerator:
    async def generate(self, request: AliceRequest) -> AliceResponse:
        pass


@lru_cache()
def get_reply_generator() -> ReplyGenerator:
    return ReplyGenerator()
