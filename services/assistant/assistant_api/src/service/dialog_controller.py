import random
from functools import lru_cache

from assistant.alice import Alice
from fastapi import Depends
from schema.alice import AliceRequest
from service.nlu import NLUService, get_nlu_service


class DialogController:
    def __init__(self, nlu_service):
        self.nlu_service = nlu_service

    async def process_assistant_request(
        self, request: AliceRequest, assistant: Alice
    ):
        assistant_intents = assistant.get_intents(request).keys()
        nlu_intents = self.nlu_service.get_intents(request)
        scenario_place = assistant.get_scenario_state(request)
        if assistant.is_new_session(request):
            reply, state = await ScenarioPlaces.hello(
                assistant.is_first_user_request(request)
            )
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        elif (assistant.is_end_session(request)) or (
            "Bye" in assistant_intents
        ):
            reply, state = await ScenarioPlaces.bye()
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        elif "YANDEX.HELP" in assistant_intents:
            reply, state = await ScenarioPlaces.help()
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        elif "YANDEX.REPEAT" in assistant_intents:
            reply, state = await ScenarioPlaces.repeat_response(
                assistant.get_last_response(request)
            )
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        elif "repeat_request" in assistant_intents:
            reply, state = await ScenarioPlaces.repeat_request(
                assistant.get_last_request(request)
            )
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        elif "film_title_by_description" in assistant_intents:
            reply, state = await ScenarioPlaces.film_title_by_description(
                assistant.get_intents(request).get("film_title_by_description")
            )
            return assistant.create_response(
                request=request, state=state, text=reply
            )
        else:
            return assistant.create_response(
                request=request,
                state={},
                text="Здесь будет обработка разных интентов",
                tts="Галас+авой sil <[2000]> бот",
            )
        assistant_tokens = assistant.get_tokens(request)
        assistant_entities = assistant.get_entities(request)
        nlu_entities = self.nlu_service.get_entities(request)
        assistant_state = assistant.get_state(request)


class ScenarioPlaces:
    # TODO: переложить в файл scenario.yml
    def __init__(self) -> None:
        self.places = {
            "help": self.Help,
            "start": self.Start,
            "bye": self.Bye,
            "film": self.FilmSearch,
            "person": self.PersonSearch,
            "aggregation": self.AggregationSearch,
        }
        # self.intent_scenario_map = {
        #     "YANDEX.HELP": self.Help,
        #     "start": self.Start,
        #     "bye": self.Bye,
        #     "FILM": self.FilmSearch,
        #     "PERSON": self.PersonSearch,
        #     "AGGREGATION": self.AggregationSearch,
        # }

    @staticmethod
    async def hello(is_first_user_request: bool = True) -> str:
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
        reply = random.choice(replies)
        state = {"scenario_place": "hello"}
        return reply, state

    @staticmethod
    async def bye():
        reply = "До свидания!"
        state = {"scenario_place": "bye"}
        return reply, state

    @staticmethod
    async def help():
        reply = "Задавайте ваши вопросы в свободной форме. Также я могу повторить ответ, или уточнить предыдущий запрос. Для этого скажите 'уточнение' и уточняющую информацию. Для выхода скажите просто 'выход'."
        state = {"scenario_place": "help"}
        return reply, state

    @staticmethod
    async def repeat_response(previous_response):
        scenario_place = {"scenario_place": "repeat_response"}
        if not previous_response:
            return (
                "Я уже забыл что говорил... Попробуйте ещё раз задать вопрос.",
                scenario_place,
            )
        else:
            return previous_response, scenario_place

    @staticmethod
    async def repeat_request(previous_request):
        scenario_place = {"scenario_place": "repeat_request"}
        if not previous_request:
            return (
                "эмм.. не могу вспомнить о чем вы спрашивали. Попробуйте ещё раз задать вопрос.",
                scenario_place,
            )
        else:
            return previous_request, scenario_place

    @staticmethod
    async def film_title_by_description(intent):
        state = {"scenario_place": "film_title_by_description"}
        slots = intent.get("slots", {})
        film_type = slots.get("film_type", {}).get("value", None)
        film_description = slots.get("film_description", {}).get("value", None)
        film_genre = slots.get("film_genre", {}).get("value", None)
        film_creation_date = slots.get("film_creation_date", {}).get(
            "value", None
        )
        # TODO service_interactor call to get film description f(slots)
        reply = "Название фильма: Star Wars"
        return reply, state

    async def film_search(self, *args, **kwargs):
        pass

    async def person_search(self, *args, **kwargs):
        pass

    async def aggregation_search(self, *args, **kwargs):
        pass


@lru_cache()
def get_dialog_controller(
    nlu_service: NLUService = Depends(get_nlu_service),
) -> DialogController:
    return DialogController(nlu_service=nlu_service)
