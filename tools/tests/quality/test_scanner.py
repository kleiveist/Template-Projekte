from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.quality.model import QualityConfig, Severity
from tools.quality.scanner import (
    code_line_numbers,
    discover_source_files,
    scan_file,
    size_result,
)


def _source_with_lines(count: int) -> str:
    return "\n".join(f"value_{index} = {index}" for index in range(count))


def _finding_for(result, rule_id: str):
    return next(
        (finding for finding in result.findings if finding.rule.rule_id == rule_id),
        None,
    )


@pytest.mark.parametrize(
    ("line_count", "expected"),
    [
        (599, None),
        (600, None),
        (601, Severity.WARNING),
        (750, Severity.WARNING),
        (751, Severity.STRONG_WARNING),
        (899, Severity.STRONG_WARNING),
        (900, Severity.STRONG_WARNING),
        (901, Severity.ERROR),
    ],
)
def test_file_code_line_boundaries_are_exact(
    tmp_path: Path,
    quality_config: QualityConfig,
    line_count: int,
    expected: Severity | None,
) -> None:
    path = tmp_path / "source.py"
    path.write_text(_source_with_lines(line_count), encoding="utf-8")
    result = size_result([scan_file(path, tmp_path)], quality_config)
    finding = _finding_for(result, "CQ001")

    assert (finding.severity if finding else None) is expected
    if finding:
        assert finding.actual == line_count


def test_python_blank_and_comment_only_lines_are_not_code(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    text = """# First line of a consecutive multiline comment.
# Second line of the comment.

value = 1  # An inline comment follows code.
"""
    path.write_text(text, encoding="utf-8")

    assert code_line_numbers(path, text) == frozenset({4})


def test_python_multiline_string_is_code_not_a_comment(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    text = '"""A module docstring\ncontinued on another line\n"""\n'
    path.write_text(text, encoding="utf-8")

    assert code_line_numbers(path, text) == frozenset({1, 2, 3})


@pytest.mark.parametrize("suffix", [".ts", ".tsx", ".js", ".jsx"])
def test_typescript_style_multiline_comments_are_not_code(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"sample{suffix}"
    text = """/* A block comment starts here.
 * Its middle line is comment-only.
 */
const value = 1; // Inline comments do not hide code.
/* comment */ const second = 2;
"""
    path.write_text(text, encoding="utf-8")

    assert code_line_numbers(path, text) == frozenset({4, 5})


def test_rust_multiline_and_nested_comments_are_not_code(tmp_path: Path) -> None:
    path = tmp_path / "sample.rs"
    text = """/* outer comment
   /* nested Rust comment */
   still part of the outer comment
*/
fn main() {} // Inline comments do not hide code.
"""
    path.write_text(text, encoding="utf-8")

    assert code_line_numbers(path, text) == frozenset({5})


def test_rust_raw_string_comment_markers_remain_code(tmp_path: Path) -> None:
    path = tmp_path / "sample.rs"
    text = 'let value = r#"/* text, not a comment */\n// still string content"#;\n'
    path.write_text(text, encoding="utf-8")

    assert code_line_numbers(path, text) == frozenset({1, 2})


@pytest.mark.parametrize(("physical_lines", "has_warning"), [(1200, False), (1201, True)])
def test_physical_line_warning_is_strictly_above_threshold(
    tmp_path: Path,
    quality_config: QualityConfig,
    physical_lines: int,
    has_warning: bool,
) -> None:
    path = tmp_path / "physical.py"
    path.write_text(
        "\n".join(["value = 1", *["# comment"] * (physical_lines - 1)]),
        encoding="utf-8",
    )
    metric = scan_file(path, tmp_path)
    finding = _finding_for(size_result([metric], quality_config), "CQ002")

    assert metric.physical_lines == physical_lines
    assert (finding is not None) is has_warning


def test_generated_dependencies_outputs_and_lockfiles_are_excluded(
    tmp_path: Path,
    quality_config: QualityConfig,
) -> None:
    source = replace(
        quality_config.source,
        extensions=(*quality_config.source.extensions, ".lock", ".json"),
    )
    config = replace(quality_config, source=source)
    included = ["src/kept.py", "tools/tauri/build/linux.py"]
    excluded = [
        "node_modules/library.py",
        ".generated/profile/generated.ts",
        "generated/protocol.rs",
        "build/output.py",
        "backend/build/output.py",
        "frontend/dist/bundle.js",
        "src-tauri/gen/commands.rs",
        "src-tauri/target/debug/build.rs",
        "Cargo.lock",
        "frontend/package-lock.json",
    ]
    for relative in [*included, *excluded]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("value = 1\n", encoding="utf-8")

    discovered = {path.relative_to(tmp_path).as_posix() for path in discover_source_files(tmp_path, config)}

    assert discovered == set(included)


def _python_function(code_lines: int) -> str:
    body = "\n".join(f"    value_{index} = {index}" for index in range(code_lines - 1))
    return f"def measured():\n{body}\n"


def _python_class(code_lines: int) -> str:
    body = "\n".join(f"    value_{index} = {index}" for index in range(code_lines - 1))
    return f"class Measured:\n{body}\n"


@pytest.mark.parametrize(
    ("line_count", "expected"),
    [
        (50, None),
        (51, Severity.WARNING),
        (80, Severity.WARNING),
        (81, Severity.STRONG_WARNING),
        (120, Severity.STRONG_WARNING),
        (121, Severity.ERROR),
    ],
)
def test_python_function_line_boundaries_are_exact(
    tmp_path: Path,
    quality_config: QualityConfig,
    line_count: int,
    expected: Severity | None,
) -> None:
    path = tmp_path / "function.py"
    path.write_text(_python_function(line_count), encoding="utf-8")
    metric = scan_file(path, tmp_path)
    finding = _finding_for(size_result([metric], quality_config), "CQ101")

    assert metric.scopes[0].code_lines == line_count
    assert (finding.severity if finding else None) is expected


@pytest.mark.parametrize(
    ("line_count", "expected"),
    [
        (300, None),
        (301, Severity.WARNING),
        (500, Severity.WARNING),
        (501, Severity.STRONG_WARNING),
        (700, Severity.STRONG_WARNING),
        (701, Severity.ERROR),
    ],
)
def test_python_class_line_boundaries_are_exact(
    tmp_path: Path,
    quality_config: QualityConfig,
    line_count: int,
    expected: Severity | None,
) -> None:
    path = tmp_path / "class.py"
    path.write_text(_python_class(line_count), encoding="utf-8")
    metric = scan_file(path, tmp_path)
    finding = _finding_for(size_result([metric], quality_config), "CQ201")

    assert metric.scopes[0].code_lines == line_count
    assert (finding.severity if finding else None) is expected
