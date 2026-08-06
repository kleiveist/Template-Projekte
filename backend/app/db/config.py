from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

from app.config.settings import BackendSettings, BackendSettingsError, load_backend_settings


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


def load_database_settings(settings: BackendSettings | None = None) -> DatabaseSettings:
    try:
        backend_settings = settings or load_backend_settings(require_database=True)
    except BackendSettingsError as exc:
        raise DatabaseConfigurationError(str(exc)) from exc
    if backend_settings.database_url is None:
        raise DatabaseConfigurationError("DATABASE_URL is required when the database feature is enabled.")
    return parse_database_url(backend_settings.database_url.get_secret_value())
