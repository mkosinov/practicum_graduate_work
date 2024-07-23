import random
from collections import namedtuple
from functools import lru_cache
from typing import Callable

from assistant.alice import Alice
from fastapi import Depends
from schema.alice import AliceRequest
from service.nlu import NLUService, get_nlu_service
from service.services_interactor import (ServicesInteractor,
                                         get_service_interactor)


class DialogController:
    def __init__(
        self, nlu_service: NLUService, services_interactor: ServicesInteractor
    ):
        self.nlu_service = nlu_service
        self.services_interactor = services_interactor
        self.search_intents: dict[str, Callable] = {
            "film_description_by_title": self.film_description,
            "film_title_by_description": self.film_title,
            "film_title_by_genre": self.film_title,
            "person_name_by_action_title": self.person_name,
            "person_name_by_role_title": self.person_name,
            "aggregation_search": self.aggregation_search,
        }

    async def process_request(self, request: AliceRequest, assistant: Alice):
        response = namedtuple("dialog_response", "text, state, end_session", defaults=("", {}, False))
        if assistant.is_new_session(request):
            return response(*await self.hello(
                assistant.is_first_user_request(request)
            ))
        assistant_intents = assistant.get_intents(request).keys()
        nlu_intents = self.nlu_service.get_intents(request)
        nlu_entities = self.nlu_service.get_entities(request)
        reply = ""
        if "YANDEX.REPEAT" in assistant_intents:
            return response(*await self.repeat_response(
                assistant.get_last_response(request)
            ))
        elif "repeat_request" in assistant_intents:
            return response(*await self.repeat_request(
                assistant.get_last_request(request)
            ))
        elif "bye" in assistant_intents:
            return response(*await self.bye(), end_session=True)
        elif "YANDEX.HELP" in assistant_intents:
            return response(*await self.help())
        for intent_id in list(assistant_intents)+nlu_intents:
            if intent_id in self.search_intents.keys():
                reply, state = await self.search_intents.get(
                    intent_id, self.default
                )(
                    assistant.get_intents(request)
                    .get(intent_id, {})
                    .get("slots", {})
                )
        if not reply:
            reply, state = await self.default()
        return response(reply, state)

    async def default(self) -> str:
        return "Я не понимаю вас. Повторите, пожалуйста", None

    async def hello(self, is_first_user_request: bool = True) -> str:
        if is_first_user_request:
            replies = [
                "Здравствуйте! Я помогу вам найти информацию о фильмах и персонах. Вы можете меня спросить, к примеру, Кто снимался в фильме матрица 2003 года? Или, как называется фильм где джедаи спасают галактику? Если вы захотите выйти из навыка, скажите просто 'выход' или 'помоги' чтобы вызвать справку по навыку.",
                "Добрый день! Я готов помочь вам найти информацию о фильмах и актерах. Вы можете задать мне вопросы вроде: 'Какие актеры снимались в фильме 'Матрица' 2003 года?' или 'Как называется фильм, в котором джедаи спасают галактику?'. Если вы захотите завершить сеанс, просто скажите 'выход' или 'помощь', чтобы получить инструкции по использованию навыка.",
                "Приветствую! Я готов помочь вам с поиском информации о фильмах и актерах. Вы можете задать мне вопросы вроде: 'Какие актеры снимались в фильме 'Матрица' 2003 года?' или 'Как называется фильм, где джедаи спасают галактику?' Если вам нужна помощь или вы хотите выйти из навыка, просто скажите 'помоги' или 'выход'.",
            ]
        else:
            replies = [
                "Рад снова видеть вас. Задавайте ваши вопросы или скажите 'выход' или 'справка'",
                "С возвращением. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
                "Спасибо, что обратились к навыку. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
                "Здравствуйте. Спрашивайте, с нетерпением жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
            ]
        return random.choice(replies), {"dialog_node": "hello"}

    async def bye(self):
        return "До свидания!", {"dialog_node": "bye"}

    async def help(self):
        return (
            "Задавайте ваши вопросы в свободной форме. Также я могу повторить ответ, или уточнить предыдущий запрос. Для этого скажите 'уточнение' и уточняющую информацию. Для выхода скажите просто 'выход'.",
            {"dialog_node": "help"},
        )

    async def repeat_response(self, previous_response):
        state = {"dialog_node": "repeat_response"}
        if not previous_response:
            return (
                "Я уже забыл что говорил... Попробуйте ещё раз задать вопрос.",
                state,
            )
        else:
            return previous_response, None

    async def repeat_request(self, previous_request):
        state = {"dialog_node": "repeat_request"}
        if not previous_request:
            return (
                "эмм.. не могу вспомнить о чем вы спрашивали. Попробуйте ещё раз задать вопрос.",
                state,
            )
        else:
            return previous_request, None

    async def film_title(
        self,
        slots: dict,
    ):
        state = {"dialog_node": "film_title"}
        film = await self.services_interactor.search_films(slots)
        if not film:
            return "Фильм не найден. Попробуйте ещё раз задать вопрос.", state
        reply = f"Название фильма: {film.title}"
        if film.creation_date:
            reply += f", дата выхода: {film.creation_date}"
        return reply, state

    async def film_description(
        self,
        slots: dict,
    ):
        state = {"dialog_node": "film_description"}
        film = await self.services_interactor.search_films(slots)
        if not film:
            return "Фильм не найден. Попробуйте ещё раз задать вопрос.", state
        if not film.description:
            return (
                "У меня нет описания этого фильма. Попробуйте поискать что-то другое.",
                state,
            )
        reply = film.description
        return reply, state

    async def person_name(
        self,
        slots: dict,
    ):
        state = {"dialog_node": "person_name"}
        person = await self.services_interactor.search_persons(slots)
        if not person:
            return (
                "Персона не найдена. Попробуйте ещё раз задать вопрос.",
                state,
            )
        return person.full_name, state

    async def aggregation_search(self, *args, **kwargs):
        pass


@lru_cache()
def get_dialog_controller(
    nlu_service: NLUService = Depends(get_nlu_service),
    services_interactor: ServicesInteractor = Depends(get_service_interactor),
) -> DialogController:
    return DialogController(
        nlu_service=nlu_service, services_interactor=services_interactor
    )
