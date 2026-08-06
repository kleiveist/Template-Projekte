from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config.settings import BackendSettings, BackendSettingsError, load_backend_settings


def test_backend_settings_defaults_without_dotenv() -> None:
    settings = BackendSettings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.backend_host == "127.0.0.1"
    assert settings.backend_port == 8000
    assert settings.database_url is None


def test_backend_settings_load_and_type_process_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("BACKEND_HOST", "localhost")
    monkeypatch.setenv("BACKEND_PORT", "9100")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:5174,tauri://localhost")

    settings = BackendSettings(_env_file=None)

    assert settings.app_env == "test"
    assert settings.backend_host == "localhost"
    assert settings.backend_port == 9100
    assert settings.backend_cors_origins == ("http://localhost:5174", "tauri://localhost")


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("APP_ENV", "staging"),
        ("BACKEND_PORT", "0"),
        ("BACKEND_PORT", "not-a-port"),
        ("BACKEND_HOST", "https://localhost"),
    ],
)
def test_backend_settings_reject_invalid_values(monkeypatch, name: str, value: str) -> None:
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError):
        BackendSettings(_env_file=None)


def test_database_url_is_optional_for_backend_without_database(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = BackendSettings(_env_file=None)

    assert settings.database_url is None


def test_database_url_can_be_required_without_leaking_secret(monkeypatch) -> None:
    database_url = "postgresql+psycopg://app:very-secret@localhost:5432/app"
    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = load_backend_settings(require_database=True, require_postgres=True)

    assert settings.database_url is not None
    assert settings.database_url.get_secret_value() == database_url
    assert "very-secret" not in repr(settings)


def test_validation_errors_hide_secret_inputs(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_PORT", "invalid")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://app:very-secret@localhost:5432/app",
    )

    with pytest.raises(ValidationError) as exc_info:
        BackendSettings(_env_file=None)

    assert "very-secret" not in str(exc_info.value)


def test_required_database_url_reports_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(BackendSettingsError, match="DATABASE_URL is required"):
        load_backend_settings(require_database=True)
