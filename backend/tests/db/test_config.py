from __future__ import annotations

import pytest

from app.db.config import DatabaseConfigurationError, load_database_settings, parse_database_url


def test_load_database_settings_reads_database_url() -> None:
    settings = load_database_settings({"DATABASE_URL": "sqlite+pysqlite:///:memory:"})

    assert settings.url.drivername == "sqlite+pysqlite"
    assert settings.url.database == ":memory:"


def test_load_database_settings_rejects_missing_url() -> None:
    with pytest.raises(DatabaseConfigurationError, match="DATABASE_URL is required"):
        load_database_settings({})


def test_parse_database_url_rejects_invalid_value() -> None:
    with pytest.raises(DatabaseConfigurationError, match="valid SQLAlchemy"):
        parse_database_url("not a database url")


def test_safe_url_hides_password() -> None:
    settings = parse_database_url("postgresql+psycopg://app:secret@localhost:5432/app")

    assert "secret" not in settings.safe_url
    assert "***" in settings.safe_url
