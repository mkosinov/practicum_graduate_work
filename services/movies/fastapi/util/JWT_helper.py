import base64
import http
import json
from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated

from argon2.exceptions import VerifyMismatchError
from core.config import settings
from Cryptodome.Hash import HMAC, SHA256
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.token import AccessTokenPayload


class JWTHelper:
    """JWTHelper provides methods to encode, decode and verify the token."""

    def __init__(self):
        self.encoding = settings.JWT_CODE
        self.key = settings.JWT_SECRET.get_secret_value().encode(self.encoding)

    def decode_payload(
        self,
        token: str,
    ) -> AccessTokenPayload:
        """Gets a token and return string with it's payload data."""
        try:
            token_parts = token.split(".")
            decoded_str = base64.b64decode(token_parts[1]).decode(
                self.encoding
            )
            payload = AccessTokenPayload(
                **(json.loads(decoded_str.replace("'", '"')))
            )
        except Exception:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Token payload decode error",
            )
        self.verify_exp_time(payload=payload)
        return payload

    def verify_token(self, token: str) -> None:
        """Gets a token string and verifies it."""
        try:
            hasher = HMAC.new(self.key, digestmod=SHA256)
            token_parts = token.split(".")
            if len(token_parts) != 3:
                raise ValueError
            payload = f"{token_parts[0]}.{token_parts[1]}"
            hasher.update(payload.encode(self.encoding))
            hasher.hexverify(token_parts[2])
        except VerifyMismatchError:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Token verification if failed",
            )

    def verify_exp_time(self, payload: AccessTokenPayload) -> None:
        """Helper verifies payload exp time."""
        now = datetime.now(timezone.utc).timestamp()
        if float(payload.exp) < now:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Access token is expired",
            )


@lru_cache()
def get_jwt_helper() -> JWTHelper:
    return JWTHelper()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
        jwthelper: Annotated[JWTHelper, Depends(get_jwt_helper)],
    ) -> AccessTokenPayload:
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        access_token = credentials.credentials
        jwthelper.verify_token(token=access_token)
        token_payload = jwthelper.decode_payload(token=access_token)
        return token_payload


security_jwt = JWTBearer()
