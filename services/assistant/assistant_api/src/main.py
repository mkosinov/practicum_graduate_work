from contextlib import asynccontextmanager

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import core.tracing  # noqa
from api.v1 import dialogs, healthcheck, webhook
from service.mongo import mongo_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_init()

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Assistant API",
    description="Alice voice assistant integration for online cinema",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

FastAPIInstrumentor.instrument_app(app)

app.include_router(webhook.router)
app.include_router(healthcheck.router)
app.include_router(dialogs.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
app.include_router(webhook.router, tags=["Assistants webhooks"])
app.include_router(healthcheck.router, tags=["Service healthchecks"])
app.include_router(dialogs.router, tags=["Dialogs history"])
