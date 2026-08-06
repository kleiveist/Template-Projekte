from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import BackendSettings, load_backend_settings


def create_app(settings: BackendSettings | None = None) -> FastAPI:
    runtime_settings = settings or load_backend_settings()
    application = FastAPI(
        title=runtime_settings.app_name,
        version="0.1.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(runtime_settings.backend_cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api")
    return application


app = create_app()
