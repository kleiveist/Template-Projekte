from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"


def test_frontend_exposes_stable_quality_scripts() -> None:
    package = json.loads((FRONTEND / "package.json").read_text(encoding="utf-8"))

    assert package["scripts"]["typecheck"] == "tsc --noEmit"
    assert package["scripts"]["lint"] == "eslint ."
    assert package["scripts"]["format:check"] == "prettier --check ."
    assert package["scripts"]["build"] == "npm run typecheck && vite build"

    dependencies = package["devDependencies"]
    for dependency in (
        "@eslint/js",
        "eslint",
        "eslint-config-prettier",
        "globals",
        "prettier",
        "typescript-eslint",
    ):
        assert dependency in dependencies
    assert dependencies["eslint"].startswith("^9.")
    assert dependencies["@eslint/js"].startswith("^9.")
    assert dependencies["prettier"].startswith("^3.")


def test_eslint_uses_flat_typescript_and_prettier_configuration() -> None:
    config = (FRONTEND / "eslint.config.js").read_text(encoding="utf-8")

    assert 'from "@eslint/js"' in config
    assert 'from "typescript-eslint"' in config
    assert 'from "eslint-config-prettier/flat"' in config
    assert 'ignores: ["coverage/**", "dist/**"]' in config

    # Governance thresholds come from config/code-quality.toml via the quality orchestrator.
    for duplicated_threshold_rule in (
        "complexity",
        "max-depth",
        "max-lines-per-function",
        "max-params",
    ):
        assert duplicated_threshold_rule not in config
