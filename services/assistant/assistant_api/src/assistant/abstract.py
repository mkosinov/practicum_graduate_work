from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Any

from pydantic import BaseModel


class AbstractAssistant(ABC):
    """ Абстрактный класс для реализации ассистента Алисы, Салюта, Маруси и тд. """

    @abstractmethod
    class Request(ABC):
        """ Схема данных входящего запроса """

    @abstractmethod
    class Response(ABC):
        """ Схема данных ответа """

    @abstractmethod
    def create_response(self, **kwargs) -> Response:
        """ Метод создания ответа с учетом передаваемых параметров """
        raise NotImplementedError("")

    @abstractmethod    
    def set_state_in_response(self, response: Response, **kwargs) -> Response:
        """ Метод для включения state в ответ ассистента """
        raise NotImplementedError("")        

    @abstractmethod
    def get_dialog_node_state(self, request: Request) -> dict[str, Any]:
        """ Метод для получения state из запроса """
        raise NotImplementedError("")    
    
    @abstractmethod
    def get_tokens(self, request: Request) -> dict[str, Any]:
        """ Метод для получения токенов из запроса """
        raise NotImplementedError("")

    @abstractmethod
    def get_intents(self, request: Request) -> dict[str, Any]:
        """ Метод для получения интентов из запроса """
        raise NotImplementedError("")

    @abstractmethod
    def get_entities(self, request: Request) -> dict[str, Any]:
        """ Метод для получения сущностей из запроса """
        raise NotImplementedError("")

    @abstractmethod
    def is_new_session(self, request: Request) -> bool:
        """ Метод для проверки что запрос - новая сессия """
        raise NotImplementedError("")        

    @abstractmethod
    def is_first_user_request(self, request: Request) -> bool:
        """ Метод для проверки что запрос - первый этого пользователя """
        raise NotImplementedError("")
    
    @abstractmethod
    def is_authenticated_user(self, request: Request) -> bool:
        """ Метод для проверки что пользователь аутентифицирован """
        raise NotImplementedError("")
    
    @abstractmethod    
    def get_last_response(self, request: Request) -> dict[str, Any]:
        """ Метод для получения последнего ответа сервиса (из state) """
        raise NotImplementedError("")

    @abstractmethod    
    def get_last_request(self, request: Request) -> dict[str, Any]:
        """ Метод для получения последнего запроса пользователя (из state) """
        raise NotImplementedError("")