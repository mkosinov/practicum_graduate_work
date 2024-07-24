import random
from enum import Enum
from functools import lru_cache
from typing import Callable


class ReplyGenerator:
    def __init__(self):
        self.reply_enum = ReplyEnum

    @staticmethod
    def hello_first_time():
        return random.choice([
            "Здравствуйте! Я помогу вам найти информацию о фильмах и персонах. Вы можете меня спросить, к примеру, Кто снимался в фильме матрица 2003 года? Или, как называется фильм где джедаи спасают галактику? Если вы захотите выйти из навыка, скажите просто 'выход' или 'помоги' чтобы вызвать справку по навыку.",
            "Добрый день! Я готов помочь вам найти информацию о фильмах и актерах. Вы можете задать мне вопросы вроде: 'Какие актеры снимались в фильме 'Матрица' 2003 года?' или 'Как называется фильм, в котором джедаи спасают галактику?'. Если вы захотите завершить сеанс, просто скажите 'выход' или 'помощь', чтобы получить инструкции по использованию навыка.",
            "Приветствую! Я готов помочь вам с поиском информации о фильмах и актерах. Вы можете задать мне вопросы вроде: 'Какие актеры снимались в фильме 'Матрица' 2003 года?' или 'Как называется фильм, где джедаи спасают галактику?' Если вам нужна помощь или вы хотите выйти из навыка, просто скажите 'помоги' или 'выход'.",
        ])

    @staticmethod
    def hello_again():
        return random.choice([
            "Рад снова видеть вас. Задавайте ваши вопросы или скажите 'выход' или 'справка'",
            "С возвращением. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
            "Спасибо, что обратились к навыку. Жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
            "Здравствуйте. Спрашивайте, с нетерпением жду ваших вопросов! Для выхода скажите 'выход' или 'помощь'",
        ])
    
    @staticmethod
    def bye():
        return random.choice([
            "До свидания!",
            "До скорой встречи!",
            "Пока!",
            "Буду ждать вас снова!"
        ])
    
    @staticmethod
    def fallback():
        return random.choice([
            "Я не понимаю вас. Повторите, пожалуйста",
            "Переформулируйте, пожалуйста",
            "Задайте вопрос по-другому, пожалуйста",
            "Не пойму о чём речь. Повторите, пожалуйста"
        ])

    @staticmethod
    def help():
        return "Задавайте ваши вопросы в свободной форме. Также я могу повторить ответ, или уточнить предыдущий запрос. Для этого скажите 'уточнение' и уточняющую информацию. Для выхода скажите просто 'выход'."
    
    @staticmethod
    def empty_repeat_request():
        return "эмм.. не могу вспомнить о чем вы спрашивали. Попробуйте ещё раз задать вопрос."

    @staticmethod
    def empty_repeat_response():
        return "Я уже забыл что говорил... Попробуйте ещё раз задать вопрос."
    
    @staticmethod
    def empty_search_result():
        return random.choice([
            "Ничего не найдено. Попробуйте ещё.",
            "Не могу найти в базе данных. Попробуйте по-другому.",
            "Ничего не нашлось. Поищите что-то другое.",
            "По вашему запросу ничего не найдено, хотя в моей базе 1000 фильмов!",
            "Что-нибудь обязательно найдется, но не в этот раз. Поищите что-то ещё."
        ])
    
    @staticmethod
    def empty_film_description():
        return random.choice([
            "У меня нет описания этого фильма. Попробуйте поискать что-то другое.",
            "Кажется кто-то забыл добавить описание фильма. Попробуйте поискать что-то ещё.",
        ])    

class ReplyEnum(Enum):
    hello_first_time = ReplyGenerator.hello_first_time()
    hello_again = ReplyGenerator.hello_again()
    bye = ReplyGenerator.bye()
    fallback = ReplyGenerator.fallback()
    help = ReplyGenerator.help()
    empty_repeat_request = ReplyGenerator.empty_repeat_request()
    empty_repeat_response = ReplyGenerator.empty_repeat_response()
    empty_search_result = ReplyGenerator.empty_search_result()
    empty_film_description = ReplyGenerator.empty_film_description()

@lru_cache()
def get_reply_generator() -> ReplyGenerator:
    return ReplyGenerator()
