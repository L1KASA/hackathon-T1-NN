from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.lifecycle.app_lifecycle import AppLifecycle
from app.routers import skill_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    lifecycle = AppLifecycle(app)
    await lifecycle.on_startup()
    try:
        yield
    finally:
        await lifecycle.on_shutdown()

def create_app() -> FastAPI:
    application = FastAPI(
        title="Hackathon T1 NN",
        summary="API",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    return application


app = create_app()

app.include_router(skill_router.router)
