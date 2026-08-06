from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError


class DatabaseConfigurationError(ValueError):
    """Raised when required database configuration is absent or invalid."""


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    url: URL

    @property
    def safe_url(self) -> str:
        return self.url.render_as_string(hide_password=True)


def parse_database_url(value: str) -> DatabaseSettings:
    candidate = value.strip()
    if not candidate:
        raise DatabaseConfigurationError("DATABASE_URL is required when the database feature is enabled.")
    try:
        url = make_url(candidate)
    except ArgumentError as exc:
        raise DatabaseConfigurationError("DATABASE_URL is not a valid SQLAlchemy database URL.") from exc
    if not url.drivername:
        raise DatabaseConfigurationError("DATABASE_URL must include a database driver.")
    return DatabaseSettings(url=url)


def load_database_settings(
    environ: Mapping[str, str] | None = None,
    *,
    variable_name: str = "DATABASE_URL",
) -> DatabaseSettings:
    source = os.environ if environ is None else environ
    value = source.get(variable_name)
    if value is None:
        raise DatabaseConfigurationError(
            f"{variable_name} is required when the database feature is enabled."
        )
    return parse_database_url(value)
