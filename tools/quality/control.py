from __future__ import annotations

import argparse
from pathlib import Path

from tools import logger
from tools.quality.architecture import architecture_result
from tools.quality.config import DEFAULT_CONFIG_PATH, QualityConfigError, load_quality_config
from tools.quality.exceptions import apply_exceptions, validate_exceptions
from tools.quality.model import CheckResult
from tools.quality.reporter import print_report
from tools.quality.scanner import SourceScanError, scan_repository, size_result
from tools.quality.tooling import (
    run_frontend_format,
    run_frontend_lint,
    run_python_format,
    run_python_lint,
    run_python_metrics,
    run_rust_check,
    run_rust_format,
    run_rust_lint,
    run_typescript_check,
    run_typescript_metrics,
)
from tools.quality.typescript import TypeScriptAnalysis, add_class_findings, analyze_typescript

ROOT = Path(__file__).resolve().parents[2]
ACTIONS = ("check", "size", "complexity", "architecture", "lint", "format")


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "quality_command",
        nargs="?",
        choices=ACTIONS,
        default="check",
        help="focused check to run (default: check)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        metavar="PATH",
        help="quality policy path (default: config/code-quality.toml)",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
        help="report format (default: text)",
    )


def _needs_typescript_analysis(action: str) -> bool:
    return action in {"check", "size", "architecture"}


def _internal_results(
    action: str,
    root: Path,
    config,
    metrics,
    typescript: TypeScriptAnalysis | None,
) -> list[CheckResult]:
    results: list[CheckResult] = []
    if action in {"check", "size"}:
        sizes = size_result(metrics, config)
        if typescript is not None:
            add_class_findings(sizes, typescript, metrics, config)
        results.append(sizes)
    if action in {"check", "complexity"}:
        results.extend(
            [
                run_python_metrics(root, metrics, config),
                run_typescript_metrics(root, metrics, config),
            ]
        )
    if action in {"check", "architecture"}:
        results.append(architecture_result(root, config, metrics, typescript))
    return results


def _lint_results(action: str, root: Path, metrics, config) -> list[CheckResult]:
    if action not in {"check", "lint"}:
        return []
    return [
        run_python_lint(root, metrics),
        run_frontend_lint(root),
        run_typescript_check(root),
        run_rust_lint(root, config),
        run_rust_check(root),
    ]


def _format_results(action: str, root: Path, metrics) -> list[CheckResult]:
    if action not in {"check", "format"}:
        return []
    return [
        run_python_format(root, metrics),
        run_frontend_format(root),
        run_rust_format(root),
    ]


def _run(args: argparse.Namespace, root: Path) -> list[CheckResult]:
    config = load_quality_config(args.config, project_root=root)
    metrics = scan_repository(root, config)
    exception_result, valid_exceptions = validate_exceptions(root, config.exceptions)
    results = [exception_result]

    typescript: TypeScriptAnalysis | None = None
    if _needs_typescript_analysis(args.quality_command):
        typescript, analysis_result = analyze_typescript(root, metrics)
        results.append(analysis_result)

    results.extend(_internal_results(args.quality_command, root, config, metrics, typescript))
    results.extend(_lint_results(args.quality_command, root, metrics, config))
    results.extend(_format_results(args.quality_command, root, metrics))
    apply_exceptions(results, valid_exceptions)
    return results


def main(args: argparse.Namespace) -> int:
    try:
        results = _run(args, ROOT)
    except (QualityConfigError, SourceScanError) as exc:
        logger.fail(f"Quality gate configuration error: {exc}")
        return 2
    print_report(results, args.output_format)
    return 0 if all(result.status == "PASS" for result in results) else 1
