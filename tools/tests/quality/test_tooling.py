from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.quality.model import CheckResult, QualityConfig, Severity
from tools.quality.scanner import ScopeMetric, SourceMetrics
from tools.quality import tooling
from tools.quality.typescript import TypeScriptAnalysis, TypeScriptClass, add_class_findings


def _python_metric(tmp_path: Path) -> SourceMetrics:
    path = tmp_path / "sample.py"
    path.write_text("def measured():\n    return True\n", encoding="utf-8")
    return SourceMetrics(
        path,
        "sample.py",
        2,
        frozenset({1, 2}),
        (ScopeMetric("function", "measured", 1, 2, 2),),
    )


@pytest.mark.parametrize(
    ("code", "message", "rule_id", "expected"),
    [
        ("C901", "`measured` is too complex (21 > 10)", "CQ102", Severity.ERROR),
        ("PLR1702", "Too many nested blocks (5 > 3)", "CQ103", Severity.STRONG_WARNING),
        (
            "PLR0913",
            "Too many arguments in function definition (8 > 5)",
            "CQ104",
            Severity.WARNING,
        ),
    ],
)
def test_ruff_metrics_are_classified_from_central_limits(
    monkeypatch,
    tmp_path: Path,
    quality_config: QualityConfig,
    code: str,
    message: str,
    rule_id: str,
    expected: Severity,
) -> None:
    payload = [
        {
            "code": code,
            "filename": str(tmp_path / "sample.py"),
            "location": {"row": 1, "column": 1},
            "message": message,
        }
    ]
    monkeypatch.setattr(tooling, "_ruff", lambda _root: "ruff")
    monkeypatch.setattr(
        tooling,
        "_run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["ruff"], 1, stdout=json.dumps(payload), stderr=""),
    )

    result = tooling.run_python_metrics(tmp_path, [_python_metric(tmp_path)], quality_config)

    assert result.status == ("FAIL" if expected is Severity.ERROR else "PASS")
    assert [(finding.rule.rule_id, finding.severity) for finding in result.findings] == [(rule_id, expected)]


def test_duplicate_ruff_nesting_diagnostics_collapse_to_the_highest_depth(
    monkeypatch,
    tmp_path: Path,
    quality_config: QualityConfig,
) -> None:
    payload = [
        {
            "code": "PLR1702",
            "filename": str(tmp_path / "sample.py"),
            "location": {"row": 2, "column": 1},
            "message": f"Too many nested blocks ({depth} > 3)",
        }
        for depth in (4, 5)
    ]
    monkeypatch.setattr(tooling, "_ruff", lambda _root: "ruff")
    monkeypatch.setattr(
        tooling,
        "_run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["ruff"], 1, stdout=json.dumps(payload), stderr=""),
    )

    result = tooling.run_python_metrics(tmp_path, [_python_metric(tmp_path)], quality_config)

    assert len(result.findings) == 1
    assert result.findings[0].actual == 5
    assert result.findings[0].symbol == "measured"


@pytest.mark.parametrize(
    ("eslint_rule", "message", "rule_id", "expected"),
    [
        ("complexity", "Function has a complexity of 21. Maximum allowed is 10.", "CQ102", Severity.ERROR),
        ("max-depth", "Blocks are nested too deeply (4). Maximum allowed is 3.", "CQ103", Severity.WARNING),
        ("max-params", "Function has too many parameters (9). Maximum allowed is 5.", "CQ104", Severity.STRONG_WARNING),
        (
            "max-lines-per-function",
            "Function has too many lines (121). Maximum allowed is 50.",
            "CQ101",
            Severity.ERROR,
        ),
    ],
)
def test_eslint_metrics_are_classified_from_central_limits(
    monkeypatch,
    tmp_path: Path,
    quality_config: QualityConfig,
    eslint_rule: str,
    message: str,
    rule_id: str,
    expected: Severity,
) -> None:
    frontend = tmp_path / "frontend"
    source = frontend / "src/sample.ts"
    source.parent.mkdir(parents=True)
    source.write_text("export const value = true;\n", encoding="utf-8")
    metric = SourceMetrics(source, "frontend/src/sample.ts", 1, frozenset({1}), ())
    payload = [
        {
            "filePath": str(source),
            "messages": [{"ruleId": eslint_rule, "message": message, "line": 1}],
        }
    ]
    monkeypatch.setattr(tooling, "_frontend_binary", lambda _root, _name: "eslint")
    monkeypatch.setattr(
        tooling,
        "_run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["eslint"], 0, stdout=json.dumps(payload), stderr=""),
    )

    result = tooling.run_typescript_metrics(tmp_path, [metric], quality_config)

    assert result.findings[0].rule.rule_id == rule_id
    assert result.findings[0].severity is expected
    assert result.status == ("FAIL" if expected is Severity.ERROR else "PASS")


def test_clippy_receives_central_hard_limits(
    monkeypatch,
    tmp_path: Path,
    quality_config: QualityConfig,
) -> None:
    (tmp_path / "src-tauri").mkdir()
    (tmp_path / "src-tauri/Cargo.toml").write_text("[package]\nname='test'\n", encoding="utf-8")
    captured: dict[str, str | list[str]] = {}

    def fake_cargo(root, arguments, name, *, env=None):
        captured["arguments"] = arguments
        captured["config"] = (Path(env["CLIPPY_CONF_DIR"]) / "clippy.toml").read_text(encoding="utf-8")
        return CheckResult(name)

    monkeypatch.setattr(tooling, "_cargo_command", fake_cargo)

    result = tooling.run_rust_lint(tmp_path, quality_config)

    assert result.status == "PASS"
    assert "too-many-arguments-threshold = 10" in captured["config"]
    assert "too-many-lines-threshold = 120" in captured["config"]
    assert "cognitive-complexity-threshold = 20" in captured["config"]
    assert "clippy::too_many_lines" in captured["arguments"]


@pytest.mark.parametrize(("line_count", "expected"), [(700, Severity.STRONG_WARNING), (701, Severity.ERROR)])
def test_typescript_class_line_hard_boundary(
    tmp_path: Path,
    quality_config: QualityConfig,
    line_count: int,
    expected: Severity,
) -> None:
    path = tmp_path / "frontend/src/class.ts"
    metric = SourceMetrics(
        path,
        "frontend/src/class.ts",
        line_count,
        frozenset(range(1, line_count + 1)),
        (),
    )
    analysis = TypeScriptAnalysis(
        (TypeScriptClass("frontend/src/class.ts", "Measured", 1, line_count),),
        (),
    )
    result = CheckResult("Size")

    add_class_findings(result, analysis, [metric], quality_config)

    assert result.findings[0].severity is expected
    assert result.status == ("FAIL" if expected is Severity.ERROR else "PASS")
