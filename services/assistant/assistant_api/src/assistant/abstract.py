from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Any

from pydantic import BaseModel


class AbstractAssistant(ABC):
    @abstractmethod
    class Request(ABC):
        pass

    @abstractmethod
    class Response(ABC):
        pass

    @abstractmethod
    def create_response(self, **kwargs) -> Response: 
        raise NotImplementedError("")

    @abstractmethod    
    def set_state_in_response(self, response: Response, **kwargs) -> Response:
        raise NotImplementedError("")        

    @abstractmethod
    def get_dialog_node_state(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")    
    
    @abstractmethod
    def get_tokens(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")

    @abstractmethod
    def get_intents(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")

    @abstractmethod
    def get_entities(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")

    @abstractmethod
    def is_new_session(self, request: Request) -> bool:
        raise NotImplementedError("")        

    @abstractmethod
    def is_first_user_request(self, request: Request) -> bool:
        raise NotImplementedError("")
    
    @abstractmethod
    def is_authenticated_user(self, request: Request) -> bool:
        raise NotImplementedError("")
    
    @abstractmethod    
    def get_last_response(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")

    @abstractmethod    
    def get_last_request(self, request: Request) -> dict[str, Any]:
        raise NotImplementedError("")