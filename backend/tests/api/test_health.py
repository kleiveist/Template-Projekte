import asyncio

import httpx

from app.config.settings import BackendSettings
from app.main import PROJECT_ROOT, app, create_app


def test_health_endpoint() -> None:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/health")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "template-backend"}
    assert app.version == (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_readiness_without_database_dependency() -> None:
    application = create_app(BackendSettings(_env_file=None), database_enabled=False)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_fails_closed_when_database_is_enabled_without_url() -> None:
    application = create_app(BackendSettings(_env_file=None), database_enabled=True)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_readiness_checks_database_without_exposing_error(monkeypatch) -> None:
    settings = BackendSettings(
        _env_file=None,
        DATABASE_URL="postgresql+psycopg://app:secret@database:5432/app",
    )
    application = create_app(settings, database_enabled=True)
    monkeypatch.setattr("app.api.health._database_ready", lambda: False)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "secret" not in response.text
