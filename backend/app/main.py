from __future__ import annotations

import tomllib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import BackendSettings, load_backend_settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _application_version() -> str:
    try:
        return (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def _database_feature_enabled() -> bool:
    try:
        profile = tomllib.loads((PROJECT_ROOT / "project-profile.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return False
    features = profile.get("features", [])
    return isinstance(features, list) and "database" in features


def create_app(
    settings: BackendSettings | None = None,
    *,
    database_enabled: bool | None = None,
) -> FastAPI:
    runtime_settings = settings or load_backend_settings()
    application = FastAPI(
        title=runtime_settings.app_name,
        version=_application_version(),
    )
    application.state.settings = runtime_settings
    application.state.database_enabled = (
        _database_feature_enabled() if database_enabled is None else database_enabled
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
