from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from app.config.settings import BackendSettings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "template-backend"}


@router.get("/ready")
def ready(request: Request, response: Response) -> dict[str, str]:
    """Report whether enabled runtime dependencies can serve requests."""
    if not bool(getattr(request.app.state, "database_enabled", False)):
        return {"status": "ready"}

    settings: BackendSettings = request.app.state.settings
    if settings.database_url is None or not _database_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}
    return {"status": "ready"}


def _database_ready() -> bool:
    # Import lazily because database modules are absent from profiles that do not enable them.
    try:
        from sqlalchemy import text
        from app.db.engine import get_database_engine

        with get_database_engine().connect() as connection:
            return connection.scalar(text("SELECT 1")) == 1
    except Exception:  # Dependency probes fail closed and never expose driver details.
        return False
