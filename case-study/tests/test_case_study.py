from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CASE_STUDY_DIR = ROOT / "case-study"
BUILD_SCRIPT = CASE_STUDY_DIR / "build.py"

if not BUILD_SCRIPT.is_file():
    pytest.skip("Master-only case study is not part of generated projects", allow_module_level=True)


def load_build_module():
    spec = importlib.util.spec_from_file_location("case_study_build", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_case_study_document_matrix_and_entrypoints() -> None:
    build = load_build_module()

    assert {(document.language, document.edition, document.output_name) for document in build.DOCUMENTS} == {
        ("de", "beginner", "template-projects-case-study-de-beginner.pdf"),
        ("de", "scientific", "template-projects-case-study-de-scientific.pdf"),
        ("en", "beginner", "template-projects-case-study-en-beginner.pdf"),
        ("en", "scientific", "template-projects-case-study-en-scientific.pdf"),
    }
    assert len(build.selected_documents("en", "all")) == 2
    assert len(build.selected_documents("all", "scientific")) == 2
    assert all(document.entrypoint.is_file() for document in build.DOCUMENTS)


def test_case_study_language_sources_keep_matching_structure() -> None:
    de_root = CASE_STUDY_DIR / "source" / "de"
    en_root = CASE_STUDY_DIR / "source" / "en"
    de_inventory = {path.relative_to(de_root) for path in de_root.rglob("*") if path.is_file()}
    en_inventory = {path.relative_to(en_root) for path in en_root.rglob("*") if path.is_file()}

    assert de_inventory == en_inventory
    assert len(list((de_root / "workspace" / "chapters").rglob("*.tex"))) == 66
    assert len(list((de_root / "workspace" / "statement").rglob("*.tex"))) == 49
    assert len(list((de_root / "workspace" / "figures").rglob("*.tex"))) == 18
    assert len(list((de_root / "workspace" / "tables").rglob("*.tex"))) == 9


def test_case_study_published_pdf_checksums() -> None:
    completed = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--verify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.count("OK: pdf/") == 4


def test_case_study_checksum_verification_detects_modified_pdf(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    build = load_build_module()
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    lines: list[str] = []
    for document in build.DOCUMENTS:
        content = document.output_name.encode()
        (pdf_dir / document.output_name).write_bytes(content)
        lines.append(f"{hashlib.sha256(content).hexdigest()}  {document.output_name}")
    (pdf_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (pdf_dir / build.DOCUMENTS[0].output_name).write_bytes(b"changed")
    monkeypatch.setattr(build, "PDF_DIR", pdf_dir)
    monkeypatch.setattr(build, "CHECKSUM_PATH", pdf_dir / "checksums.sha256")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        build.verify_checksums()


def test_case_study_checksum_verification_detects_unexpected_pdf(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    build = load_build_module()
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    lines: list[str] = []
    for document in build.DOCUMENTS:
        content = document.output_name.encode()
        (pdf_dir / document.output_name).write_bytes(content)
        lines.append(f"{hashlib.sha256(content).hexdigest()}  {document.output_name}")
    (pdf_dir / "obsolete-copy.pdf").write_bytes(b"duplicate")
    (pdf_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(build, "PDF_DIR", pdf_dir)
    monkeypatch.setattr(build, "CHECKSUM_PATH", pdf_dir / "checksums.sha256")

    with pytest.raises(RuntimeError, match="unexpected PDFs: obsolete-copy.pdf"):
        build.verify_checksums()
