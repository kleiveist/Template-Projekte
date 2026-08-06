from __future__ import annotations

import pytest
from pydantic import SecretStr

from app.config.settings import BackendSettings
from app.db.config import DatabaseConfigurationError, load_database_settings, parse_database_url


def test_load_database_settings_reads_database_url() -> None:
    backend_settings = BackendSettings(database_url=SecretStr("sqlite+pysqlite:///:memory:"), _env_file=None)
    settings = load_database_settings(backend_settings)

    assert settings.url.drivername == "sqlite+pysqlite"
    assert settings.url.database == ":memory:"


def test_load_database_settings_rejects_missing_url() -> None:
    with pytest.raises(DatabaseConfigurationError, match="DATABASE_URL is required"):
        load_database_settings(BackendSettings(database_url=None, _env_file=None))


def test_parse_database_url_rejects_invalid_value() -> None:
    with pytest.raises(DatabaseConfigurationError, match="valid SQLAlchemy"):
        parse_database_url("not a database url")


def test_safe_url_hides_password() -> None:
    settings = parse_database_url("postgresql+psycopg://app:secret@localhost:5432/app")

    assert "secret" not in settings.safe_url
    assert "***" in settings.safe_url
