import asyncio
from contextlib import asynccontextmanager

from api.v1 import healthcheck, webhook
from assistant.alice import Alice
from fastapi import FastAPI, Request, responses
from fastapi.responses import JSONResponse
from schema.alice import AliceResponse, InnerResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug"
    )