from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from app.config.settings import BackendSettings
from app.services.readiness import readiness_status

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "template-backend"}


@router.get("/ready")
def ready(request: Request, response: Response) -> dict[str, str]:
    """Report whether enabled runtime dependencies can serve requests."""
    settings: BackendSettings = request.app.state.settings
    readiness = readiness_status(
        database_enabled=bool(getattr(request.app.state, "database_enabled", False)),
        database_configured=settings.database_url is not None,
        database_probe=request.app.state.database_probe,
    )
    if readiness == "unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": readiness}
