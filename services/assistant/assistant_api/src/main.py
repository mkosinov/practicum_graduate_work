from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(webhook.router, tags=["Assistants webhooks"])
app.include_router(healthcheck.router, tags=["Service healthchecks"])
app.include_router(dialogs.router, tags=["Dialogs history"])
