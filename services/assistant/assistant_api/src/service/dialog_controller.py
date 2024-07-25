import asyncio
import inspect
import random
from collections import namedtuple
from functools import lru_cache, wraps
from time import sleep, time
from typing import Callable

from assistant.alice import Alice
from fastapi import Depends
from schema.alice import AliceRequest
from service.nlu import NLUService, get_nlu_service
from service.reply_generator import ReplyGenerator, get_reply_generator
from service.services_interactor import (ServicesInteractor,
                                         get_service_interactor)
from wrapt_timeout_decorator import timeout


def async_add_dialog_node_to_return(func):
    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        response = await func(self, *args, **kwargs)
        if isinstance(response, tuple):
            return response
        return (response, {"dialog_node": func.__name__})
    return async_wrapper

def add_dialog_node_to_return(func):
    @wraps(func)        
    def wrapper(self, *args, **kwargs):
        response = func(self, *args, **kwargs)
        if isinstance(response, tuple):
            return response
        return (response, {"dialog_node": func.__name__})
    return wrapper


class DialogController:
    def __init__(
        self, nlu_service: NLUService, services_interactor: ServicesInteractor, reply_generator: ReplyGenerator
    ):
        self.nlu_service = nlu_service
        self.services_interactor = services_interactor
        self.reply_generator = reply_generator
        self.search_intents: dict[str, Callable] = {
            "film_description_by_title": self.film_description,
            "film_title_by_description": self.film_title,
            "film_title_by_genre": self.film_title,
            "person_name_by_action_title": self.person_name,
            "person_name_by_role_title": self.person_name
        }

    async def process_request(self, request: AliceRequest, assistant: Alice):
        response = namedtuple("dialog_response", "text, state, kwargs", defaults=("", {}, {}))
        if assistant.is_new_session(request):
            return response(*self.hello(
                assistant.is_first_user_request(request)
            ))
        assistant_intents = assistant.get_intents(request).keys()
        nlu_intents = self.nlu_service.get_intents(request)
        nlu_entities = self.nlu_service.get_entities(request)
        reply = ""
        if "YANDEX.REPEAT" in assistant_intents:
            return response(*self.repeat_response(
                assistant.get_last_response(request)
            ))
        elif "repeat_request" in assistant_intents:
            return response(*self.repeat_request(
                assistant.get_last_request(request), assistant.get_dialog_node_state(request)
            ))
        elif "bye" in assistant_intents:
            return response(*self.bye(), end_session=True)
        elif "YANDEX.HELP" in assistant_intents:
            return response(*self.help())
        for intent_id in list(assistant_intents)+nlu_intents:
            if intent_id in self.search_intents.keys():
                try:
                    reply, state = await asyncio.wait_for(self.search_intents.get(intent_id)(
                        assistant.get_intents(request)
                        .get(intent_id, {})
                        .get("slots", {})
                    ), timeout=2)
                except TimeoutError:
                    reply, state = self.timeout()                    
        if not reply:
            reply, state = self.fallback()
        return response(reply, state)

    @add_dialog_node_to_return
    def timeout(self) -> tuple[str, dict | None]:
        return self.reply_generator.reply_enum.timeout.value, None

    @add_dialog_node_to_return
    def fallback(self) -> tuple[str, dict | None]:
        return self.reply_generator.reply_enum.fallback.value, None

    @add_dialog_node_to_return
    def hello(self, is_first_user_request: bool = True) -> str:
        if is_first_user_request:
            return self.reply_generator.reply_enum.hello_first_time.value
        return self.reply_generator.reply_enum.hello_again.value

    @add_dialog_node_to_return
    def bye(self):
        return self.reply_generator.reply_enum.bye.value

    @add_dialog_node_to_return
    def help(self):
        return self.reply_generator.reply_enum.help.value

    def repeat_response(self, previous_response, previous_dialog_node_state):
        if previous_response:
            return previous_response, previous_dialog_node_state
        return self.reply_generator.reply_enum.empty_repeat_response.value, None

    def repeat_request(self, previous_request, previous_dialog_node_state):
        if previous_request:
            return previous_request, previous_dialog_node_state
        return self.reply_generator.reply_enum.empty_repeat_request.value, None

    @async_add_dialog_node_to_return
    async def film_title(
        self,
        slots: dict,
    ):
        film = await self.services_interactor.search_films(slots)
        if not film:
            return self.reply_generator.reply_enum.empty_search_result.value, None
        reply = film.title
        if film.creation_date:
            reply += f"\nДата выхода: {film.creation_date}"
        return reply

    @async_add_dialog_node_to_return
    async def film_description(
        self,
        slots: dict,
    ):
        film = await self.services_interactor.search_films(slots)
        if not film:
            return self.reply_generator.reply_enum.empty_search_result.value, None
        if not film.description:
            return self.reply_generator.reply_enum.empty_film_description.value
        reply = film.description
        return reply

    @async_add_dialog_node_to_return    
    async def person_name(
        self,
        slots: dict,
    ):
        person = await self.services_interactor.search_persons(slots)
        if not person:
            return self.reply_generator.reply_enum.empty_search_result.value, None
        return person.full_name


@lru_cache()
def get_dialog_controller(
    nlu_service: NLUService = Depends(get_nlu_service),
    services_interactor: ServicesInteractor = Depends(get_service_interactor),
    reply_generator: ReplyGenerator = Depends(get_reply_generator),
) -> DialogController:
    return DialogController(
        nlu_service=nlu_service, services_interactor=services_interactor, reply_generator=reply_generator
    )
