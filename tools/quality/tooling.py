from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.process import prepare_command
from tools.quality.model import CheckResult, Finding, QualityConfig, RULES, ScopeLimits, Severity
from tools.quality.scanner import SourceMetrics

PYTHON_LINE_LENGTH = 120


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            prepare_command(command),
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(command, 127, stdout="", stderr=str(exc))


def _executable(candidates: list[Path], fallback: str) -> str | None:
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return shutil.which(fallback)


def _ruff(root: Path) -> str | None:
    return _executable(
        [root / "tools/.venv/bin/ruff", root / "tools/.venv/Scripts/ruff.exe"],
        "ruff",
    )


def _frontend_binary(root: Path, name: str) -> str | None:
    return _executable(
        [root / f"frontend/node_modules/.bin/{name}", root / f"frontend/node_modules/.bin/{name}.cmd"],
        name,
    )


def _tool_result(name: str, completed: subprocess.CompletedProcess[str], *, missing_action: str) -> CheckResult:
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part and part.strip())
    if completed.returncode == 0:
        return CheckResult(name, detail="completed successfully", output=output)
    if completed.returncode == 127:
        detail = f"required tool is unavailable. Action: {missing_action}"
    else:
        detail = f"command failed with exit code {completed.returncode}"
    return CheckResult(name, passed=False, detail=detail, output=output)


def _python_paths(metrics: list[SourceMetrics], root: Path) -> list[str]:
    return [str(source.path.relative_to(root)) for source in metrics if source.path.suffix.lower() == ".py"]


def _frontend_exists(root: Path) -> bool:
    return (root / "frontend/package.json").is_file()


def _rust_exists(root: Path) -> bool:
    return (root / "src-tauri/Cargo.toml").is_file()


def run_python_lint(root: Path, metrics: list[SourceMetrics]) -> CheckResult:
    paths = _python_paths(metrics, root)
    if not paths:
        return CheckResult("Python lint", detail="no Python sources present")
    executable = _ruff(root)
    if executable is None:
        return CheckResult(
            "Python lint",
            passed=False,
            detail="Ruff is unavailable. Action: run 'python tools/control.py install'.",
        )
    completed = _run(
        [executable, "check", "--isolated", "--select", "E4,E7,E9,F,B", *paths],
        cwd=root,
    )
    return _tool_result(
        "Python lint",
        completed,
        missing_action="run 'python tools/control.py install'",
    )


def run_python_format(root: Path, metrics: list[SourceMetrics]) -> CheckResult:
    paths = _python_paths(metrics, root)
    if not paths:
        return CheckResult("Python formatting", detail="no Python sources present")
    executable = _ruff(root)
    if executable is None:
        return CheckResult(
            "Python formatting",
            passed=False,
            detail="Ruff is unavailable. Action: run 'python tools/control.py install'.",
        )
    completed = _run(
        [
            executable,
            "format",
            "--check",
            "--isolated",
            "--line-length",
            str(PYTHON_LINE_LENGTH),
            *paths,
        ],
        cwd=root,
    )
    return _tool_result(
        "Python formatting",
        completed,
        missing_action="run 'python tools/control.py install'",
    )


def _run_frontend_script(root: Path, script: str, name: str) -> CheckResult:
    if not _frontend_exists(root):
        return CheckResult(name, detail="frontend is not enabled in this project")
    npm = shutil.which("npm")
    if npm is None:
        return CheckResult(name, passed=False, detail="npm is unavailable. Action: install Node.js and npm.")
    completed = _run([npm, "run", script], cwd=root / "frontend")
    return _tool_result(name, completed, missing_action="install Node.js and run 'python tools/control.py install'")


def run_frontend_lint(root: Path) -> CheckResult:
    return _run_frontend_script(root, "lint", "TypeScript lint")


def run_frontend_format(root: Path) -> CheckResult:
    return _run_frontend_script(root, "format:check", "Frontend formatting")


def run_typescript_check(root: Path) -> CheckResult:
    return _run_frontend_script(root, "typecheck", "TypeScript compiler")


def _cargo_command(
    root: Path,
    arguments: list[str],
    name: str,
    *,
    env: dict[str, str] | None = None,
) -> CheckResult:
    if not _rust_exists(root):
        return CheckResult(name, detail="Tauri is not enabled in this project")
    cargo = shutil.which("cargo")
    if cargo is None:
        return CheckResult(name, passed=False, detail="Cargo is unavailable. Action: install the Rust toolchain.")
    completed = _run([cargo, *arguments], cwd=root, env=env)
    return _tool_result(name, completed, missing_action="install Rust with rustfmt and Clippy")


def run_rust_format(root: Path) -> CheckResult:
    return _cargo_command(
        root,
        ["fmt", "--all", "--manifest-path", "src-tauri/Cargo.toml", "--", "--check"],
        "Rust formatting",
    )


def run_rust_lint(root: Path, config: QualityConfig) -> CheckResult:
    if not _rust_exists(root):
        return CheckResult("Rust Clippy", detail="Tauri is not enabled in this project")
    with tempfile.TemporaryDirectory(prefix="template-clippy-") as temporary:
        config_directory = Path(temporary)
        (config_directory / "clippy.toml").write_text(
            "\n".join(
                [
                    f"too-many-arguments-threshold = {config.parameters.maximum}",
                    f"too-many-lines-threshold = {config.function.maximum}",
                    f"cognitive-complexity-threshold = {config.complexity.maximum}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["CLIPPY_CONF_DIR"] = str(config_directory)
        return _cargo_command(
            root,
            [
                "clippy",
                "--locked",
                "--manifest-path",
                "src-tauri/Cargo.toml",
                "--all-targets",
                "--",
                "-D",
                "warnings",
                "-W",
                "clippy::too_many_lines",
                "-W",
                "clippy::cognitive_complexity",
            ],
            "Rust Clippy",
            env=environment,
        )


def run_rust_check(root: Path) -> CheckResult:
    return _cargo_command(
        root,
        ["check", "--locked", "--manifest-path", "src-tauri/Cargo.toml"],
        "Rust compiler",
    )


def _relative_filename(filename: str, root: Path) -> str:
    path = Path(filename)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _actual_from_ruff(message: str) -> int | None:
    match = re.search(r"\((\d+)\s*>\s*\d+\)", message)
    return int(match.group(1)) if match else None


def _symbol_from_message(message: str) -> str | None:
    match = re.search(r"`([^`]+)`", message)
    return match.group(1) if match else None


def _python_function_at(
    metrics: list[SourceMetrics],
    relative_path: str,
    line: int | None,
) -> str | None:
    if line is None:
        return None
    candidates = [
        scope
        for source in metrics
        if source.relative_path == relative_path
        for scope in source.scopes
        if scope.kind == "function" and scope.start_line <= line <= scope.end_line
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda scope: scope.end_line - scope.start_line).symbol


def _ruff_metric_finding(
    item,
    *,
    root: Path,
    metrics: list[SourceMetrics],
    mapping: dict[str, tuple[str, ScopeLimits]],
) -> tuple[tuple[str, str, str | None] | None, Finding | None, str]:
    code = item.get("code")
    if code not in mapping:
        return None, None, ""
    message = str(item.get("message", ""))
    actual = _actual_from_ruff(message)
    if actual is None:
        return None, None, f"could not read the measured value from Ruff {code}: {message}"
    rule_id, limits = mapping[code]
    severity = limits.classify(actual)
    if severity is None:
        return None, None, ""
    location = item.get("location") or {}
    relative = _relative_filename(str(item.get("filename", "")), root)
    line = location.get("row")
    symbol = _symbol_from_message(message) or _python_function_at(metrics, relative, line)
    threshold = (
        limits.maximum
        if severity is Severity.ERROR
        else (limits.strong_warning if severity is Severity.STRONG_WARNING else limits.warning)
    )
    finding = Finding(
        RULES[rule_id],
        severity,
        relative,
        message,
        actual,
        threshold,
        symbol=symbol,
        line=line,
    )
    return (rule_id, relative, symbol), finding, ""


def run_python_metrics(
    root: Path,
    metrics: list[SourceMetrics],
    config: QualityConfig,
) -> CheckResult:
    result = CheckResult("Python complexity")
    paths = _python_paths(metrics, root)
    if not paths:
        result.detail = "no Python sources present"
        return result
    executable = _ruff(root)
    if executable is None:
        result.passed = False
        result.detail = "Ruff is unavailable. Action: run 'python tools/control.py install'."
        return result
    command = [
        executable,
        "check",
        "--isolated",
        "--preview",
        "--output-format",
        "json",
        "--select",
        "C901,PLR0913,PLR1702",
        "--config",
        f"lint.mccabe.max-complexity={config.complexity.warning}",
        "--config",
        f"lint.pylint.max-args={config.parameters.warning - 1}",
        "--config",
        f"lint.pylint.max-nested-blocks={config.nesting.warning - 1}",
        *paths,
    ]
    completed = _run(command, cwd=root)
    if completed.returncode not in {0, 1}:
        result.passed = False
        result.detail = f"Ruff metric analysis failed with exit code {completed.returncode}"
        result.output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        return result
    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        result.passed = False
        result.detail = f"Ruff metric output was not valid JSON: {exc}"
        result.output = completed.stdout or completed.stderr
        return result
    mapping: dict[str, tuple[str, ScopeLimits]] = {
        "C901": ("CQ102", config.complexity),
        "PLR1702": ("CQ103", config.nesting),
        "PLR0913": ("CQ104", config.parameters),
    }
    findings: dict[tuple[str, str, str | None], Finding] = {}
    for item in payload:
        key, finding, error = _ruff_metric_finding(item, root=root, metrics=metrics, mapping=mapping)
        if error:
            result.passed = False
            result.detail = error
            continue
        if key is None or finding is None:
            continue
        existing = findings.get(key)
        if existing is None or int(existing.actual or 0) < int(finding.actual or 0):
            findings[key] = finding
    result.findings.extend(findings.values())
    return result


_ESLINT_ACTUAL_PATTERNS = {
    "complexity": re.compile(r"complexity of (\d+)", re.IGNORECASE),
    "max-depth": re.compile(r"nested too deeply \((\d+)\)", re.IGNORECASE),
    "max-params": re.compile(r"too many parameters \((\d+)\)", re.IGNORECASE),
    "max-lines-per-function": re.compile(r"too many lines \((\d+)\)", re.IGNORECASE),
}


def _eslint_sources(metrics: list[SourceMetrics], root: Path) -> list[str]:
    extensions = {".js", ".jsx", ".ts", ".tsx"}
    frontend = root / "frontend"
    return [
        str(source.path.relative_to(frontend))
        for source in metrics
        if source.path.suffix.lower() in extensions and source.path.is_relative_to(frontend)
    ]


def run_typescript_metrics(
    root: Path,
    metrics: list[SourceMetrics],
    config: QualityConfig,
) -> CheckResult:
    result = CheckResult("TypeScript complexity")
    paths = _eslint_sources(metrics, root)
    if not paths:
        result.detail = "no JavaScript or TypeScript sources present"
        return result
    eslint = _frontend_binary(root, "eslint")
    if eslint is None:
        result.passed = False
        result.detail = "ESLint is unavailable. Action: run 'python tools/control.py install'."
        return result
    rules = {
        "complexity": ["warn", config.complexity.warning],
        "max-depth": ["warn", config.nesting.warning - 1],
        "max-params": ["warn", config.parameters.warning - 1],
        "max-lines-per-function": [
            "warn",
            {"max": config.function.warning, "skipBlankLines": True, "skipComments": True},
        ],
    }
    completed = _run(
        [eslint, "--format", "json", "--rule", json.dumps(rules, separators=(",", ":")), *paths],
        cwd=root / "frontend",
    )
    if completed.returncode not in {0, 1}:
        result.passed = False
        result.detail = f"ESLint metric analysis failed with exit code {completed.returncode}"
        result.output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        return result
    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        result.passed = False
        result.detail = f"ESLint metric output was not valid JSON: {exc}"
        result.output = completed.stdout or completed.stderr
        return result
    mapping: dict[str, tuple[str, ScopeLimits]] = {
        "complexity": ("CQ102", config.complexity),
        "max-depth": ("CQ103", config.nesting),
        "max-params": ("CQ104", config.parameters),
        "max-lines-per-function": ("CQ101", config.function),
    }
    for file_result in payload:
        relative = _relative_filename(str(file_result.get("filePath", "")), root)
        for message in file_result.get("messages", []):
            eslint_rule = message.get("ruleId")
            if eslint_rule not in mapping:
                continue
            match = _ESLINT_ACTUAL_PATTERNS[eslint_rule].search(str(message.get("message", "")))
            if match is None:
                result.passed = False
                result.detail = f"could not read the measured value from ESLint {eslint_rule}"
                continue
            actual = int(match.group(1))
            rule_id, limits = mapping[eslint_rule]
            severity = limits.classify(actual)
            if severity is None:
                continue
            result.findings.append(
                Finding(
                    RULES[rule_id],
                    severity,
                    relative,
                    str(message.get("message", "")),
                    actual,
                    limits.maximum
                    if severity is Severity.ERROR
                    else (limits.strong_warning if severity is Severity.STRONG_WARNING else limits.warning),
                    line=message.get("line"),
                )
            )
    return result
