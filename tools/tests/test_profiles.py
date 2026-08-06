from __future__ import annotations

from pathlib import Path

import pytest

from tools import control
from tools.profiles import loader, validator

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / "profiles"


def test_all_declared_profiles_load() -> None:
    catalog = loader.load_catalog(PROFILES_DIR)

    assert list(sorted(catalog.profiles)) == [
        "desktop-cloud",
        "desktop-local",
        "full-platform",
        "web-cloud",
        "web-only",
    ]


def test_unknown_profile_is_rejected() -> None:
    catalog = loader.load_catalog(PROFILES_DIR)

    with pytest.raises(validator.ProfileLookupError):
        loader.resolve_profile(catalog, "unknown-profile")


def test_invalid_feature_dependencies_are_detected(tmp_path) -> None:
    root = tmp_path / "repo"
    profiles_dir = root / "profiles"
    docs_dir = root / "docs"
    profiles_dir.mkdir(parents=True)
    docs_dir.mkdir()

    (profiles_dir / "features.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                "",
                "[core]",
                'paths = ["docs"]',
                "",
                "[features.frontend]",
                'name = "Frontend"',
                'description = "Frontend runtime"',
                'paths = []',
                "",
                "[features.tauri]",
                'name = "Tauri"',
                'description = "Desktop shell"',
                'paths = []',
                'requires = ["frontend"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (profiles_dir / "broken-profile.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                'id = "broken-profile"',
                'name = "Broken profile"',
                'description = "Missing required frontend feature"',
                'features = ["tauri"]',
                "",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(validator.CatalogValidationError, match="requires feature 'frontend'"):
        loader.load_catalog(profiles_dir, validate_paths=False)


def test_each_profile_activates_expected_features() -> None:
    catalog = loader.load_catalog(PROFILES_DIR)

    expected = {
        "web-only": ("frontend",),
        "web-cloud": ("frontend", "backend", "cloud"),
        "desktop-local": ("frontend", "tauri"),
        "desktop-cloud": ("frontend", "backend", "tauri", "cloud"),
        "full-platform": ("frontend", "backend", "tauri", "cloud"),
    }

    for profile_id, features in expected.items():
        resolved = loader.resolve_profile(catalog, profile_id)
        assert resolved.features == features


def test_profile_configuration_can_be_extended_without_breaking_loading(tmp_path) -> None:
    root = tmp_path / "repo"
    profiles_dir = root / "profiles"
    docs_dir = root / "docs"
    profiles_dir.mkdir(parents=True)
    docs_dir.mkdir()

    (profiles_dir / "features.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                "",
                "[core]",
                'paths = ["docs"]',
                "",
                "[features.frontend]",
                'name = "Frontend"',
                'description = "Frontend runtime"',
                'paths = []',
                'future_flag = "safe-to-ignore"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (profiles_dir / "extensible.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                'id = "extensible"',
                "order = 15",
                'name = "Extensible"',
                'description = "Allows future metadata"',
                'features = ["frontend"]',
                'notes = "ignored extension field"',
                "",
                "[metadata]",
                'owner = "template-team"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    catalog = loader.load_catalog(profiles_dir, validate_paths=False)
    resolved = loader.resolve_profile(catalog, "extensible")

    assert resolved.profile_id == "extensible"
    assert resolved.features == ("frontend",)


def test_init_command_scaffolds_selected_profile(tmp_path) -> None:
    target = tmp_path / "desktop-local-project"

    assert control.main(
        [
            "init",
            "--profile",
            "desktop-local",
            "--target-dir",
            str(target),
        ]
    ) == 0

    assert (target / "frontend").exists()
    assert (target / "src-tauri").exists()
    assert (target / "tools").exists()
    assert (target / "docs").exists()
    assert (target / "shared").exists()
    assert (target / "profiles").exists()
    assert not (target / "backend").exists()
    assert 'id = "desktop-local"' in (target / "project-profile.toml").read_text(encoding="utf-8")
    frontend_profile = (target / "frontend" / "src" / "project-profile.ts").read_text(encoding="utf-8")
    assert 'export const activeProfileId = "desktop-local";' in frontend_profile
    assert '"tauri"' in frontend_profile
    assert '"backend"' not in frontend_profile


def test_init_command_supports_interactive_profile_selection(monkeypatch, tmp_path) -> None:
    target = tmp_path / "web-only-project"
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")

    assert control.main(["init", "--target-dir", str(target)]) == 0
    assert 'id = "web-only"' in (target / "project-profile.toml").read_text(encoding="utf-8")


def test_init_command_dry_run_does_not_write_files(tmp_path) -> None:
    target = tmp_path / "web-cloud-project"

    assert control.main(
        [
            "init",
            "--profile",
            "web-cloud",
            "--target-dir",
            str(target),
            "--dry-run",
        ]
    ) == 0

    assert not target.exists()
