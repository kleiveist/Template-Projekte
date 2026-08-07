from __future__ import annotations

import os
import asyncio

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.config import parse_database_url
from app.db.engine import create_database_engine
from app.config.settings import BackendSettings
from app.main import create_app


def test_postgres_connection_when_test_database_is_available() -> None:
    database_url = os.getenv("DATABASE_URL_TEST")
    if not database_url:
        pytest.skip("DATABASE_URL_TEST is not configured")

    settings = parse_database_url(database_url)
    if settings.url.get_backend_name() != "postgresql":
        pytest.fail("DATABASE_URL_TEST must use PostgreSQL")

    engine = create_database_engine(settings.url)
    try:
        try:
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT 1")) == 1
        except SQLAlchemyError as exc:
            pytest.fail(f"Configured PostgreSQL test database is unavailable: {exc.__class__.__name__}")
    finally:
        engine.dispose()


def test_readiness_with_postgres_when_test_database_is_available(monkeypatch) -> None:
    database_url = os.getenv("DATABASE_URL_TEST")
    if not database_url:
        pytest.skip("DATABASE_URL_TEST is not configured")

    monkeypatch.setenv("DATABASE_URL", database_url)
    application = create_app(BackendSettings(_env_file=None), database_enabled=True)

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/ready")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
