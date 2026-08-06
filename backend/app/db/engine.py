from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL

from app.db.config import load_database_settings, parse_database_url

_engine: Engine | None = None


def create_database_engine(
    database_url: str | URL | None = None,
    **engine_options: Any,
) -> Engine:
    if database_url is None:
        url = load_database_settings().url
    elif isinstance(database_url, URL):
        url = database_url
    else:
        url = parse_database_url(database_url).url

    options: dict[str, Any] = {"pool_pre_ping": True}
    options.update(engine_options)
    return create_engine(url, **options)


def get_database_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def dispose_database_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
