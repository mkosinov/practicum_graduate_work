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

app.include_router(webhook.router)
app.include_router(healthcheck.router)
app.include_router(dialogs.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
