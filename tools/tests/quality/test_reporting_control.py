from __future__ import annotations

import argparse
import json

import pytest

from tools.quality import control
from tools.quality.model import CheckResult, Finding, RULES, Severity
from tools.quality.reporter import print_report


def _finding(severity: Severity) -> Finding:
    return Finding(
        RULES["CQ001"],
        severity,
        "example.py",
        "File contains too many code lines.",
        actual=901 if severity is Severity.ERROR else 601,
        threshold=900 if severity is Severity.ERROR else 600,
    )


@pytest.mark.parametrize(
    ("severity", "expected_exit"),
    [(Severity.WARNING, 0), (Severity.STRONG_WARNING, 0), (Severity.ERROR, 1)],
)
def test_quality_exit_code_depends_only_on_blocking_results(
    monkeypatch,
    capsys,
    severity: Severity,
    expected_exit: int,
) -> None:
    monkeypatch.setattr(
        control,
        "_run",
        lambda _args, _root: [CheckResult("Size", findings=[_finding(severity)])],
    )
    args = argparse.Namespace(output_format="text")

    assert control.main(args) == expected_exit
    assert "Quality gate:" in capsys.readouterr().out


def test_failed_external_tool_fails_the_gate(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        control,
        "_run",
        lambda _args, _root: [CheckResult("Python lint", passed=False, detail="Ruff failed")],
    )

    assert control.main(argparse.Namespace(output_format="text")) == 1
    assert "QUALITY TOOL ERROR" in capsys.readouterr().out


def test_json_report_contains_stable_rule_ids_and_summary(capsys) -> None:
    print_report([CheckResult("Size", findings=[_finding(Severity.ERROR)], files_checked=1)], "json")

    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["status"] == "FAIL"
    assert payload["summary"]["errors"] == 1
    assert payload["checks"][0]["findings"][0]["rule_id"] == "CQ001"
