from __future__ import annotations

import contextlib

import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.params import Security
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from api.v1 import access, auth, oauth, personal, roles
from core.config import get_settings
from db.prepare_db import redis_shutdown, redis_startup
from setup.tracer import configure_tracer
from util.JWT_helper import strict_token_checker


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_startup()
    yield
    await redis_shutdown()

sentry_sdk.init(integrations=[StarletteIntegration(), FastApiIntegration()])

app = FastAPI(
    lifespan=lifespan,
    title=get_settings().project_name,
    version=get_settings().version,
    description=get_settings().description,
    docs_url=get_settings().open_api_docs_url,
    openapi_url=get_settings().open_api_url,
)

if get_settings().enable_tracing:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

app.include_router(
    auth.router,
    prefix=get_settings().url_prefix + "/auth",
    tags=["Authentication service."],
)
app.include_router(
    oauth.router,
    prefix=get_settings().url_prefix + "/oauth",
    tags=["OAuth2.0 service."],
)
app.include_router(
    personal.router,
    prefix=get_settings().url_prefix + "/profile",
    tags=["Personal account."],
)
app.include_router(
    roles.router,
    prefix=get_settings().url_prefix + "/roles",
    tags=["Roles"],
    dependencies=[Security(strict_token_checker, scopes=["auth_admin"])],
)
app.include_router(
    access.router,
    prefix=get_settings().url_prefix + "/access",
    tags=["Access"],
    dependencies=[Security(strict_token_checker, scopes=["auth_admin"])],
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if (
        request.url
        == f"{request.base_url}{get_settings().open_api_docs_url[1:]}"
        or request.url
        == f"{request.base_url}{get_settings().open_api_url[1:]}"
    ):
        return response
    if get_settings().enable_tracing and not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=get_settings().auth_fastapi_port, debug=True
    )
