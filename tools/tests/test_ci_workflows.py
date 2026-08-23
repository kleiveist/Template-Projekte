from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
NODE_WORKFLOW_SETUP_COUNTS = {
    "ci.yml": 2,
    "profiles.yml": 1,
    "postgres.yml": 1,
    "desktop.yml": 1,
    "release.yml": 1,
}
ARTIFACT_UPLOAD_COUNTS = {
    "ci.yml": 0,
    "profiles.yml": 0,
    "postgres.yml": 0,
    "desktop.yml": 1,
    "release.yml": 1,
}

pytestmark = pytest.mark.skipif(
    not WORKFLOWS.exists(),
    reason="Master-repository CI workflows are not scaffolded into derived projects",
)


def _workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def _action_versions(content: str, action: str) -> list[str]:
    pattern = re.compile(rf"(?m)^\s*uses:\s*{re.escape(action)}@([^\s#]+)\s*$")
    return pattern.findall(content)


def _steps_using(content: str, action: str) -> list[str]:
    steps = re.findall(r"(?ms)^      - .*?(?=^      - |\Z)", content)
    action_pattern = re.compile(rf"(?m)^        uses:\s*{re.escape(action)}@[^\s#]+\s*$")
    return [step for step in steps if action_pattern.search(step)]


def _step_named(content: str, name: str) -> str:
    steps = re.findall(r"(?ms)^      - .*?(?=^      - |\Z)", content)
    matches = [step for step in steps if f"name: {name}\n" in step]
    assert len(matches) == 1
    return matches[0]


@pytest.mark.parametrize(("name", "expected_setup_count"), NODE_WORKFLOW_SETUP_COUNTS.items())
def test_every_node_workflow_pins_node_24(name: str, expected_setup_count: int) -> None:
    content = _workflow(name)
    action_versions = _action_versions(content, "actions/setup-node")
    setup_steps = _steps_using(content, "actions/setup-node")

    assert action_versions == ["v7"] * expected_setup_count
    assert len(setup_steps) == expected_setup_count
    for step in setup_steps:
        node_versions = re.findall(r"(?m)^          node-version:\s*([^\s#]+)\s*$", step)
        assert node_versions == ['"24"']


def test_every_artifact_upload_uses_v7() -> None:
    for name, expected_upload_count in ARTIFACT_UPLOAD_COUNTS.items():
        action_versions = _action_versions(_workflow(name), "actions/upload-artifact")
        assert action_versions == ["v7"] * expected_upload_count


def test_ci_workflows_have_safe_common_policy() -> None:
    for name in ("ci.yml", "profiles.yml", "postgres.yml", "desktop.yml"):
        content = _workflow(name)
        assert "pull_request:" in content
        assert "push:" in content
        assert "workflow_dispatch:" in content
        assert "- main" in content
        assert "permissions:\n  contents: read" in content
        assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in content
        assert "timeout-minutes:" in content
        assert "continue-on-error" not in content
        assert "secrets." not in content
        assert "deploy" not in content.lower()
        assert "gh release" not in content.lower()
        assert "python tools/control.py release check" not in content


def test_core_ci_uses_supported_runtimes_and_public_tooling() -> None:
    content = _workflow("ci.yml")

    assert 'python-version: "3.11"' in content
    assert 'node-version: "24"' in content
    assert "name: Core / Code Quality & Architecture" in content
    assert (
        "rustup toolchain install 1.97.1 --profile minimal --component rustfmt,clippy --target wasm32-wasip1"
    ) in content
    assert "rustup default 1.97.1" in content
    assert "tools/quality/rust_analyzer/target" in content
    assert "tools/quality/rust_analyzer/Cargo.lock" in content
    assert "python tools/quality/rust_analyzer/build.py --check" in content
    assert "cargo clippy --manifest-path tools/quality/rust_analyzer/Cargo.toml" in content
    assert "tools/tests/quality/test_rust_syntax.py" in content
    assert "tools/tests/quality/test_rust_payload.py" in content
    assert "tools/tests/quality/test_rust_wasi_host.py" in content
    assert "python tools/control.py install --skip-backend --skip-playwright" in content
    assert "python tools/control.py quality" in content
    assert "tools/.venv/bin/python -m pytest -q tools/tests/quality/test_typescript_ast.py" in content
    assert content.count("needs: quality") == 5
    assert "name: Core / Documentation Check" in content
    assert "python tools/control.py docs check" in content
    assert "tools/.venv/bin/python -m pytest -q tools/tests/test_docs_index.py" in content
    assert "python tools/control.py test --suite tools" in content
    assert "python tools/control.py test --suite schema" in content
    assert "python tools/control.py test --suite api" in content
    assert "python tools/control.py test --suite database" in content
    assert "python tools/control.py test --suite frontend" in content
    assert "python tools/control.py build web" in content
    assert "python tools/control.py container validate" in content
    assert "python tools/control.py build container" in content
    assert "python tools/control.py version check" in content
    assert "cache: pip" in content
    assert "cache: npm" in content
    assert "actions/checkout@v7" in content
    assert "actions/setup-python@v7" in content
    assert "actions/setup-node@v7" in content
    assert "actions/cache@v6" in content
    assert "\nenv:\n  DATABASE_URL:" not in content
    assert content.index("python tools/control.py quality") < content.index(
        "python tools/control.py test --suite tools"
    )
    assert content.index("python tools/control.py quality") < content.index("python tools/control.py build web")


def test_profile_matrix_generates_and_tests_every_profile() -> None:
    content = _workflow("profiles.yml")
    cargo_cache_step = _step_named(content, "Cache Cargo dependencies")

    assert "fail-fast: false" in content
    for profile_id in (
        "web-only",
        "web-cloud",
        "desktop-local",
        "desktop-cloud",
        "full-platform",
    ):
        assert f"profile: {profile_id}" in content
    assert "python tools/control.py init" in content
    assert "python tools/control.py doctor" in content
    assert "python tools/control.py config doctor" in content
    assert "python tools/control.py install --skip-playwright" in content
    assert "python tools/control.py test --suite all" in content
    assert "python tools/control.py build web" in content
    assert "python tools/control.py container validate" in content
    assert "python tools/control.py tauri doctor" in content
    assert "python tools/control.py build desktop --dry-run --no-clean" in content
    assert "python tools/control.py quality" in content
    assert ("rustup toolchain install 1.97.1 --profile minimal --component rustfmt,clippy") in content
    assert "actions/checkout@v7" in content
    assert "actions/setup-python@v7" in content
    assert "actions/setup-node@v7" in content
    assert "actions/cache@v6" in content
    assert ".generated/ci-${{ matrix.profile }}/src-tauri/target" in cargo_cache_step
    assert content.index("name: Generate profile project") < content.index("name: Cache Cargo dependencies")
    assert content.index("python tools/control.py quality") < content.index("python tools/control.py test --suite all")


def test_postgres_ci_uses_isolated_service_health_check_and_migration() -> None:
    content = _workflow("postgres.yml")
    generated_content = content.split("  generated-postgres:", maxsplit=1)[1]

    assert content.count("image: postgres:16.15-alpine3.24") == 2
    assert "POSTGRES_PASSWORD: test-password" in content
    assert "POSTGRES_DB: template_test" in content
    assert "DATABASE_URL_TEST:" in content
    assert "--health-cmd" in content
    assert "pg_isready" in content
    assert "sleep " not in content
    assert "python tools/control.py db upgrade" in content
    assert "python tools/control.py test --suite postgres" in content
    assert "--profile ${{ matrix.profile }}" in content
    assert "--with postgres" in content
    for profile_id in ("web-cloud", "desktop-cloud", "full-platform"):
        assert f"profile: {profile_id}" in content
    assert "python tools/control.py container validate" in content
    assert "python tools/control.py quality" in generated_content
    assert "python tools/control.py config doctor" in generated_content
    assert "python tools/control.py tauri doctor" in generated_content
    assert "python tools/control.py build desktop --dry-run --no-clean" in generated_content
    assert ("rustup toolchain install 1.97.1 --profile minimal --component rustfmt,clippy") in generated_content
    assert "actions/checkout@v7" in content
    assert "actions/setup-python@v7" in content
    assert "actions/setup-node@v7" in content
    assert generated_content.index("python tools/control.py quality") < generated_content.index(
        "python tools/control.py test --suite all"
    )


def test_desktop_ci_builds_unsigned_native_artifacts_on_each_platform() -> None:
    content = _workflow("desktop.yml")

    assert "workflow_call:" in content
    assert "ubuntu-latest" in content
    assert "macos-latest" in content
    assert "windows-latest" in content
    assert "target: linux" in content
    assert "target: macos" in content
    assert "target: windows" in content
    assert ("rustup toolchain install 1.97.1 --profile minimal --component rustfmt,clippy") in content
    assert "name: Install portable tooling runtime" in content
    assert "python tools/control.py install --skip-backend --skip-frontend --skip-playwright" in content
    assert "name: Verify the portable Rust analyzer runtime" in content
    analyzer_step = _step_named(content, "Verify the portable Rust analyzer runtime")
    assert "env:" in analyzer_step
    assert "DATABASE_URL: postgresql+psycopg://template_test:test-password@127.0.0.1:5432/template_test" in (
        analyzer_step
    )
    assert "run: python tools/control.py doctor" in analyzer_step
    assert "name: Verify UTF-8 Rust analyzer transport" in content
    assert "test_subprocess_transport_is_utf8_when_child_text_stdio_is_cp1252" in content
    assert "if:" not in _step_named(content, "Install portable tooling runtime")
    assert "if:" not in analyzer_step
    assert "if:" not in _step_named(content, "Verify UTF-8 Rust analyzer transport")
    assert "tools\\.venv\\Scripts\\python.exe -m pytest -q tools/tests/test_process.py" in content
    assert "python tools/control.py test --suite tauri" in content
    assert "python tools/control.py build desktop" in content
    assert "actions/upload-artifact@v7" in content
    assert "unsigned" in content.lower()
    assert "secrets." not in content
    assert "publish" not in content.lower()
    assert "deploy" not in content.lower()


def test_release_validation_is_explicit_and_never_publishes() -> None:
    content = _workflow("release.yml")

    assert "workflow_dispatch:" in content
    assert '"v*.*.*"' in content
    assert "timeout-minutes: 60" in content
    assert "branches:" not in content
    assert "python tools/control.py release check" in content
    assert "python tools/control.py quality" in content
    assert "tools/.venv/bin/python -m pytest -q tools/tests/test_docs_index.py" in content
    assert (
        "rustup toolchain install 1.97.1 --profile minimal --component rustfmt,clippy --target wasm32-wasip1"
    ) in content
    assert "python tools/quality/rust_analyzer/build.py --check" in content
    assert "python tools/control.py build web" in content
    assert "python tools/control.py build container" in content
    assert "uses: ./.github/workflows/desktop.yml" in content
    assert "permissions:\n  contents: read" in content
    assert "secrets." not in content
    assert "continue-on-error" not in content
    assert "publish" not in content.lower()
    assert "deploy" not in content.lower()
    assert content.index("python tools/control.py quality") < content.index("python tools/control.py test --suite all")
