from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import AliasChoices, Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CORS_ORIGINS = "http://127.0.0.1:5173,http://localhost:5173,http://tauri.localhost,tauri://localhost"
HOST_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


class BackendSettingsError(ValueError):
    """Raised when backend runtime configuration is missing or invalid."""


def _valid_host(value: str) -> bool:
    candidate = value.strip().strip("[]")
    if not candidate or any(char.isspace() for char in candidate) or "://" in candidate:
        return False
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        pass
    return all(HOST_LABEL.fullmatch(label) for label in candidate.rstrip(".").split("."))


def _valid_origin(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https", "tauri"} and bool(parsed.hostname) and value != "*"


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
        hide_input_in_errors=True,
    )

    app_env: Literal["development", "test", "production"] = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    app_name: str = Field(default="Template Project API", validation_alias="APP_NAME", min_length=1)
    backend_host: str = Field(default="127.0.0.1", validation_alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, ge=1, le=65535, validation_alias="BACKEND_PORT")
    backend_cors_origins_value: str = Field(
        default=DEFAULT_CORS_ORIGINS,
        validation_alias=AliasChoices("BACKEND_CORS_ORIGINS", "CORS_ORIGINS"),
        exclude=True,
    )
    database_url: SecretStr | None = Field(default=None, validation_alias="DATABASE_URL", repr=False)

    @field_validator("backend_host")
    @classmethod
    def validate_backend_host(cls, value: str) -> str:
        if not _valid_host(value):
            raise ValueError("must be a valid IP address or host name")
        return value

    @field_validator("backend_cors_origins_value")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins or any(not _valid_origin(origin) for origin in origins):
            raise ValueError("must contain comma-separated explicit HTTP(S) or Tauri origins")
        return value

    @property
    def backend_cors_origins(self) -> tuple[str, ...]:
        return tuple(origin.strip() for origin in self.backend_cors_origins_value.split(",") if origin.strip())


def load_backend_settings(
    *,
    require_database: bool = False,
    require_postgres: bool = False,
) -> BackendSettings:
    try:
        settings = BackendSettings()
    except ValidationError as exc:
        raise BackendSettingsError(f"Invalid backend configuration: {exc}") from exc

    if require_database and settings.database_url is None:
        raise BackendSettingsError("DATABASE_URL is required when the database feature is enabled.")
    if require_postgres and settings.database_url is not None:
        database_url = settings.database_url.get_secret_value()
        try:
            scheme = urlsplit(database_url).scheme
        except ValueError as exc:
            raise BackendSettingsError("DATABASE_URL is not a valid database URL.") from exc
        if scheme != "postgresql+psycopg":
            raise BackendSettingsError("PostgreSQL requires the postgresql+psycopg DATABASE_URL scheme.")
    return settings
