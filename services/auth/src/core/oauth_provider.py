from __future__ import annotations

import base64
import enum
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any

import httpx
from fastapi import HTTPException

from core.config import get_settings
from schemas.oauth import OAuthProviderDataSchema


class CodeChallengeMethod(enum.Enum):
    S256 = "S256"
    plain = "plain"
    not_used = ""


class AbstractOAuthProvider(ABC):
    """Abstract class to create oauth providers with authorization code flow"""

    title: str
    client_id: str
    client_secret: str
    code_challende_method: CodeChallengeMethod
    oauth_provider_authorization_page_url_template: str

    @abstractmethod
    async def flow(self, code, **kwargs) -> OAuthProviderDataSchema:
        """Public abstract method to authorize and get user info"""
        pass

    @abstractmethod
    async def _request_access_token(self, code, **kwargs) -> dict[str, Any]:
        """Private abstract method to get access token from provider"""
        pass

    @abstractmethod
    async def _get_user_info(
        self, access_token: str, **kwargs
    ) -> OAuthProviderDataSchema:
        """Private abstract method to get user information from provider"""
        pass


class VK(AbstractOAuthProvider):
    title = "vk"
    client_id = get_settings().oauth_vk_client_id
    client_secret = get_settings().oauth_vk_client_secret
    code_challende_method = CodeChallengeMethod.not_used
    oauth_provider_authorization_page_url_template = (
        f"https://oauth.vk.com/authorize?client_id={client_id}"
        + "&display=page&redirect_uri={redirect_uri}&response_type=code&scope=email&v=5.131"
    )

    @classmethod
    async def flow(
        cls, code, redirect_uri, **kwargs
    ) -> OAuthProviderDataSchema:
        token_data = await cls._request_access_token(
            code=code, oauth_code_url=redirect_uri
        )
        user_info = await cls._get_user_info(
            access_token=token_data["access_token"]
        )
        return OAuthProviderDataSchema(
            provider=cls.title,
            email=token_data["email"],
            user_id=token_data["user_id"],
            first_name=user_info["response"]["first_name"],
            last_name=user_info["response"]["last_name"],
        )

    @classmethod
    def oauth_provider_authorization_page_url(cls, redirect_uri: str):
        return cls.oauth_provider_authorization_page_url_template.format(
            redirect_uri=redirect_uri
        )

    @classmethod
    async def _request_access_token(cls, code: str, oauth_code_url: str):
        url = f"https://oauth.vk.com/access_token?client_id={cls.client_id}&client_secret={cls.client_secret}&redirect_uri={oauth_code_url}&code={code}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
            )
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    @classmethod
    async def _get_user_info(cls, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://api.vk.com/method/account.getProfileInfo?v=5.199"
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()


class Yandex(AbstractOAuthProvider):
    title = "yandex"
    client_id = get_settings().oauth_yandex_client_id
    client_secret = get_settings().oauth_yandex_client_secret
    code_challenge_method = CodeChallengeMethod.S256
    oauth_provider_authorization_page_url_template = (
        f"https://oauth.yandex.ru/authorize?client_id={client_id}&code_challenge_method={code_challenge_method.value}"
        + "&response_type=code&redirect_uri={redirect_uri}&state={state}&code_challenge={code_challenge}"
    )

    @classmethod
    def oauth_provider_authorization_page_url(
        cls, redirect_uri: str, state: str, code_challenge: str
    ) -> str:
        return cls.oauth_provider_authorization_page_url_template.format(
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
        )

    @classmethod
    async def flow(
        cls, code, code_verifier, **kwargs
    ) -> OAuthProviderDataSchema:
        tokens = await cls._request_access_token(
            code=code, code_verifier=code_verifier
        )
        user_info = await cls._get_user_info(
            access_token=tokens["access_token"]
        )
        return OAuthProviderDataSchema(
            provider=cls.title,
            email=user_info["default_email"],
            user_id=int(user_info["id"]),
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
        )

    @classmethod
    async def _request_access_token(cls, code: str, code_verifier: str):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {cls.yandex_basic_base64().decode()}",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://oauth.yandex.ru/token",
                headers=headers,
                data=data,
            )
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    @classmethod
    async def _get_user_info(cls, access_token):
        headers = {"Authorization": f"OAuth {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url="https://login.yandex.ru/info?", headers=headers
            )
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    @classmethod
    def yandex_basic_base64(cls) -> bytes:
        return base64.standard_b64encode(
            f"{cls.client_id}:{cls.client_secret}".encode()
        )


class OAuthProviders(enum.Enum):
    vk = VK
    yandex = Yandex
