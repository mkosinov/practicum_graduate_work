from functools import lru_cache


class NLUService:
    def __init__(self):
        """Инициализация сторонних библиотек: deeppavlov"""
        pass

    def get_intents(self, text):
        pass

    def get_entities(self, text):
        pass


@lru_cache()
def get_nlu_service() -> NLUService:
    return NLUService()
