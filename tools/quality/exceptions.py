from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

from tools.quality.model import CheckResult, ExceptionEntry, Finding, RULES, Severity


def validate_exceptions(
    root: Path,
    entries: tuple[ExceptionEntry, ...],
    *,
    today: date | None = None,
) -> tuple[CheckResult, tuple[ExceptionEntry, ...]]:
    result = CheckResult("Exceptions")
    current_date = today or date.today()
    valid: list[ExceptionEntry] = []
    for entry in entries:
        try:
            expiration = date.fromisoformat(entry.expires)
        except ValueError:
            result.findings.append(
                Finding(
                    RULES["EX001"],
                    Severity.ERROR,
                    "config/code-quality.toml",
                    f"Exception for {entry.rule_id} at {entry.path} has an invalid ISO expiration date.",
                    actual=entry.expires,
                    threshold="YYYY-MM-DD",
                    symbol=entry.symbol,
                )
            )
            continue
        if not (root / entry.path).is_file():
            result.findings.append(
                Finding(
                    RULES["EX001"],
                    Severity.ERROR,
                    "config/code-quality.toml",
                    f"Exception for {entry.rule_id} references a file that does not exist: {entry.path}.",
                    actual=entry.path,
                    symbol=entry.symbol,
                )
            )
            continue
        if expiration < current_date:
            result.findings.append(
                Finding(
                    RULES["EX002"],
                    Severity.ERROR,
                    entry.path,
                    f"Exception for {entry.rule_id} expired on {entry.expires}.",
                    actual=entry.expires,
                    threshold=current_date.isoformat(),
                    symbol=entry.symbol,
                )
            )
            continue
        valid.append(entry)
    return result, tuple(valid)


def _matching_exception(finding: Finding, entries: tuple[ExceptionEntry, ...]) -> ExceptionEntry | None:
    for entry in entries:
        if entry.rule_id != finding.rule.rule_id or entry.path != finding.path:
            continue
        if entry.symbol is not None and entry.symbol != finding.symbol:
            continue
        return entry
    return None


def apply_exceptions(results: list[CheckResult], entries: tuple[ExceptionEntry, ...]) -> None:
    for result in results:
        updated: list[Finding] = []
        for finding in result.findings:
            exception = _matching_exception(finding, entries)
            if exception is None:
                updated.append(finding)
                continue
            explanation = f"{exception.reason} (expires {exception.expires})"
            updated.append(replace(finding, suppressed_reason=explanation))
        result.findings = updated
