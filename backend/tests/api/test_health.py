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


def test_readiness_fails_closed_when_database_is_enabled_without_url(monkeypatch) -> None:
    # PostgreSQL integration runs export DATABASE_URL for the process. This test
    # verifies the missing-value branch, so it must not inherit that external
    # configuration.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    application = create_app(BackendSettings(_env_file=None), database_enabled=True)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_readiness_checks_database_without_exposing_error() -> None:
    settings = BackendSettings(
        _env_file=None,
        DATABASE_URL="postgresql+psycopg://app:secret@database:5432/app",
    )
    application = create_app(settings, database_enabled=True, database_probe=lambda: False)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "secret" not in response.text
