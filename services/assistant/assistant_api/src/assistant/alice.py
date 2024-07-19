from functools import lru_cache
from typing import Any

from assistant.abstract import AbstractAssistant
from schema.alice import AliceRequest, AliceResponse, Response


class Alice(AbstractAssistant):
    def create_response(
        self, request: AliceRequest, state: dict, **response_kwargs
    ) -> AliceResponse:
        response = AliceResponse(
            response=Response(**response_kwargs),
            version="1.0",
        )
        response_with_state = self.set_state_in_response(
            request, response, state
        )
        return response_with_state

    def set_state_in_response(
        self, request: AliceRequest, response: AliceResponse, state: dict
    ) -> dict[str, dict]:
        state["last_user_request"] = request.request.command
        state["last_user_response"] = response.response.text
        if self.is_authenticated_user(request):
            response.user_state_update = state
        else:
            response.application_state = state
        return response

    def get_tokens(self, request: AliceRequest):
        pass

    def get_intents(self, request: AliceRequest) -> dict[str, Any]:
        return getattr(request.request.nlu, "intents", {})

    def get_entities(self, request: AliceRequest):
        pass

    def get_session_state(self, request: AliceRequest) -> dict[str, Any]:
        return getattr(request.state, "session", {})

    def get_application_state(self, request: AliceRequest) -> dict[str, Any]:
        return getattr(request.state, "application", {})

    def get_scenario_state(self, request: AliceRequest) -> dict[str, Any]:
        if self.is_authenticated_user(request):
            return getattr(request.state.user, "scenario_place", {})
        else:
            return getattr(request.state.application, "scenario_place", {})

    def get_last_request(self, request: AliceRequest) -> dict[str, Any]:
        if self.is_authenticated_user(request):
            return getattr(request.state, "user", {}).get(
                "last_user_request", ""
            )
        else:
            return getattr(request.state, "application", {}).get(
                "last_user_request", ""
            )

    def get_last_response(self, request: AliceRequest) -> dict[str, Any]:
        if self.is_authenticated_user(request):
            return getattr(request.state, "user", {}).get(
                "last_user_response", ""
            )
        else:
            return getattr(request.state, "application", {}).get(
                "last_user_response", ""
            )

    def is_new_session(self, request: AliceRequest) -> bool:
        """Return if session is new. Default is False."""
        return getattr(request.session, "new", False)

    def is_authenticated_user(self, request: AliceRequest) -> bool:
        """Return True if user is authenticated."""
        if hasattr(request, "session") and hasattr(request.session, "user"):
            return True
        return False

    def is_first_user_request(self, request: AliceRequest) -> bool:
        """Check if user has state."""
        if hasattr(request, "state"):
            if (
                request.state.session
                or request.state.user
                or request.state.application
            ):
                return False
        return True

    def is_end_session(self, request: AliceRequest) -> bool:
        """Return if session is end. Default is False."""
        return getattr(request.session, "end_session", False)


@lru_cache()
def get_alice() -> Alice:
    return Alice()
