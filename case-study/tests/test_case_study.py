from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CASE_STUDY_DIR = ROOT / "case-study"
BUILD_SCRIPT = CASE_STUDY_DIR / "build.py"

if not BUILD_SCRIPT.is_file():
    pytest.skip(
        "Master-only case study is not part of generated projects",
        allow_module_level=True,
    )


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
    build = load_build_module()
    de_root = CASE_STUDY_DIR / "source" / "de"
    en_root = CASE_STUDY_DIR / "source" / "en"
    de_inventory = {path.relative_to(de_root) for path in de_root.rglob("*") if path.is_file()}
    en_inventory = {path.relative_to(en_root) for path in en_root.rglob("*") if path.is_file()}

    assert de_inventory == en_inventory
    assert len(list((de_root / "workspace" / "chapters").rglob("*.tex"))) == 66
    assert len(list((de_root / "workspace" / "statement").rglob("*.tex"))) == 49
    assert len(list((de_root / "workspace" / "figures").rglob("*.tex"))) == 18
    assert len(list((de_root / "workspace" / "tables").rglob("*.tex"))) == 9
    build.validate_source_parity()


def test_case_study_release_addendum_is_bilingual_and_non_self_referential() -> None:
    relative = Path("workspace/chapters/900_schluss/950.tex")
    german = (CASE_STUDY_DIR / "source" / "de" / relative).read_text(encoding="utf-8")
    english = (CASE_STUDY_DIR / "source" / "en" / relative).read_text(encoding="utf-8")

    assert "Freigabenachtrag v1.0.0" in german
    assert "Release validation addendum for v1.0.0" in english
    assert "461fc751" in german and "461fc751" in english
    assert "annotierte Tag \\texttt{v1.0.0}" in german
    assert "annotated \\texttt{v1.0.0} tag" in english
    assert "\\texttt{CQ001 ERROR} oberhalb von 900 LOC" in german
    assert "\\texttt{CQ001 ERROR} above 900 LOC" in english
    assert "historische Momentaufnahmen" in german
    assert "historical snapshots" in english
    assert "0d37943" not in german + english


def test_case_study_release_runtime_references_are_current() -> None:
    for language in ("de", "en"):
        language_root = CASE_STUDY_DIR / "source" / language
        source = "\n".join(path.read_text(encoding="utf-8") for path in language_root.rglob("*.tex"))

        assert "Node.js 20" not in source
        assert "Node~20" not in source
        assert "16.4-alpine3.20" not in source
        assert "Node~24" in source
        assert "16.15-alpine3.24" in source


def test_case_study_release_analyzer_references_are_current() -> None:
    tooling = Path("workspace/chapters/500_tooling_workflow/550.tex")
    statement = Path("workspace/statement/500_tooling_workflow/550.tex")
    stack = Path("workspace/tables/technology-stack.tex")
    conclusion = Path("workspace/chapters/900_schluss/950.tex")

    for language in ("de", "en"):
        language_root = CASE_STUDY_DIR / "source" / language
        tooling_text = (language_root / tooling).read_text(encoding="utf-8")
        statement_text = (language_root / statement).read_text(encoding="utf-8")
        stack_text = (language_root / stack).read_text(encoding="utf-8")
        conclusion_text = (language_root / conclusion).read_text(encoding="utf-8")

        for token in (
            "Syn~2.0.119",
            "Wasmtime~47.0.1",
            "rustc~1.97.1",
            "\\texttt{wasm32-wasip1}",
        ):
            assert token in tooling_text
            assert token in conclusion_text
        assert "Syn~2.0.119" in statement_text
        assert "Wasmtime~47.0.1" in statement_text
        for token in (
            "Syn 2.0.119",
            "Wasmtime 47.0.1",
            "rustc 1.97.1",
            "\\texttt{wasm32-wasip1}",
        ):
            assert token in stack_text

    german_stack = (CASE_STUDY_DIR / "source" / "de" / stack).read_text(encoding="utf-8")
    english_stack = (CASE_STUDY_DIR / "source" / "en" / stack).read_text(encoding="utf-8")
    assert "Tauri: mindestens 1.77, Edition 2021" in german_stack
    assert "Tauri: at least 1.77, edition 2021" in english_stack


def test_case_study_release_tooling_runtime_contract_is_current() -> None:
    install_chapter = Path("workspace/chapters/500_tooling_workflow/530.tex")
    install_statement = Path("workspace/statement/500_tooling_workflow/530.tex")
    outlook = Path("workspace/chapters/900_schluss/940.tex")

    expectations = {
        "de": (
            "Im v1.0.0-Freigabestand ist die Abweichung behoben",
            "für jedes Profil",
            "Im v1.0.0-Freigabestand sind die historischen",
            "Ruff in generierten Backendprofilen konsistent auffindbar zu",
        ),
        "en": (
            "In the v1.0.0 release state, the discrepancy is corrected",
            "for every profile",
            "In the v1.0.0 release state, the historical",
            "Ruff should be made consistently discoverable",
        ),
    }

    for language, (current_contract, every_profile, outlook_current, obsolete) in expectations.items():
        language_root = CASE_STUDY_DIR / "source" / language
        chapter_text = (language_root / install_chapter).read_text(encoding="utf-8")
        statement_text = (language_root / install_statement).read_text(encoding="utf-8")
        outlook_text = (language_root / outlook).read_text(encoding="utf-8")

        assert "461fc751" in chapter_text
        assert current_contract in chapter_text
        assert "\\path{tools/.venv}" in chapter_text
        assert every_profile in statement_text
        assert "\\path{tools/.venv}" in statement_text
        assert outlook_current in outlook_text
        assert obsolete not in outlook_text


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


def test_case_study_source_parity_detects_changed_structural_argument(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    build = load_build_module()
    source_dir = tmp_path / "source"
    for language in ("de", "en"):
        language_dir = source_dir / language
        language_dir.mkdir(parents=True)
        (language_dir / "main.tex").write_text(
            "\\label{sec:same}\n\\parencite{same-key}\n",
            encoding="utf-8",
        )
        (language_dir / "references.bib").write_text(
            "@online{same-key,\n  title = {Same}\n}\n",
            encoding="utf-8",
        )
    (source_dir / "en" / "main.tex").write_text(
        "\\label{sec:different}\n\\parencite{same-key}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(build, "SOURCE_DIR", source_dir)

    with pytest.raises(RuntimeError, match="Bilingual LaTeX structure mismatch"):
        build.validate_source_parity()


def test_case_study_provenance_detects_source_changes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    build = load_build_module()
    source_dir = tmp_path / "source"
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    for language in ("de", "en"):
        language_dir = source_dir / language
        language_dir.mkdir(parents=True)
        (language_dir / "main.tex").write_text("shared source\n", encoding="utf-8")
        (language_dir / "references.bib").write_text("", encoding="utf-8")
    for document in build.DOCUMENTS:
        (pdf_dir / document.output_name).write_bytes(document.output_name.encode())

    monkeypatch.setattr(build, "SOURCE_DIR", source_dir)
    monkeypatch.setattr(build, "PDF_DIR", pdf_dir)
    monkeypatch.setattr(build, "CHECKSUM_PATH", pdf_dir / "checksums.sha256")
    monkeypatch.setattr(build, "PROVENANCE_PATH", pdf_dir / "provenance.json")

    replacements: list[tuple[Path, Path]] = []
    replace = build.os.replace

    def tracked_replace(source: Path, destination: Path) -> None:
        replacements.append((Path(source), Path(destination)))
        replace(source, destination)

    monkeypatch.setattr(build.os, "replace", tracked_replace)

    build.record_release_evidence()
    assert [destination for _source, destination in replacements] == [
        pdf_dir / "checksums.sha256",
        pdf_dir / "provenance.json",
    ]
    assert all(source.parent == pdf_dir and not source.exists() for source, _destination in replacements)
    build.verify_checksums()
    build.verify_provenance()
    recorded = json.loads((pdf_dir / "provenance.json").read_text(encoding="utf-8"))
    assert set(recorded["documents"]) == {document.output_name for document in build.DOCUMENTS}

    (source_dir / "de" / "main.tex").write_text("changed source\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="source checksum mismatch"):
        build.verify_provenance()


def test_case_study_provenance_rejects_invalid_json_shapes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    build = load_build_module()
    provenance_path = tmp_path / "provenance.json"
    monkeypatch.setattr(build, "PROVENANCE_PATH", provenance_path)

    invalid_manifests = (
        [],
        {
            "schema_version": 1,
            "documents": {document.output_name: None for document in build.DOCUMENTS},
        },
    )
    for manifest in invalid_manifests:
        provenance_path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises((RuntimeError, TypeError), match="Invalid provenance manifest"):
            build.verify_provenance()
