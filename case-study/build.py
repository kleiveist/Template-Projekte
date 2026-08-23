from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

CASE_STUDY_DIR = Path(__file__).resolve().parent
SOURCE_DIR = CASE_STUDY_DIR / "source"
PDF_DIR = CASE_STUDY_DIR / "pdf"
CHECKSUM_PATH = PDF_DIR / "checksums.sha256"
PROVENANCE_PATH = PDF_DIR / "provenance.json"
SOURCE_SUFFIXES = frozenset({".bib", ".tex"})
STRUCTURAL_COMMAND_PATTERN = re.compile(
    r"\\(autocite|beginnerinput|input|label|pageref|parencite|ref|textcite)\{([^}]*)\}"
)
ENVIRONMENT_PATTERN = re.compile(r"\\(begin|end)\{([^}]*)\}")
BIBLIOGRAPHY_KEY_PATTERN = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Document:
    language: str
    edition: str
    output_name: str

    @property
    def source_dir(self) -> Path:
        return SOURCE_DIR / self.language

    @property
    def entrypoint(self) -> Path:
        return self.source_dir / f"{self.edition}.tex"


DOCUMENTS = (
    Document("de", "beginner", "template-projects-case-study-de-beginner.pdf"),
    Document("de", "scientific", "template-projects-case-study-de-scientific.pdf"),
    Document("en", "beginner", "template-projects-case-study-en-beginner.pdf"),
    Document("en", "scientific", "template-projects-case-study-en-scientific.pdf"),
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the PDF editions of the Template Projects case study.")
    parser.add_argument(
        "--language",
        choices=("all", "de", "en"),
        default="all",
        help="language to build (default: all)",
    )
    parser.add_argument(
        "--edition",
        choices=("all", "beginner", "scientific"),
        default="all",
        help="edition to build (default: all)",
    )
    parser.add_argument(
        "--tectonic",
        metavar="PATH",
        help="Tectonic executable (default: resolve tectonic from PATH)",
    )
    parser.add_argument(
        "--biber",
        metavar="PATH",
        help="Biber executable (default: resolve biber from PATH)",
    )
    evidence = parser.add_mutually_exclusive_group()
    evidence.add_argument(
        "--verify",
        action="store_true",
        help="verify bilingual sources and reviewed PDF checksums/provenance without building",
    )
    evidence.add_argument(
        "--record",
        action="store_true",
        help="record checksums and source provenance after all four PDFs have been reviewed",
    )
    return parser.parse_args(argv)


def selected_documents(language: str, edition: str) -> tuple[Document, ...]:
    return tuple(
        document
        for document in DOCUMENTS
        if language in ("all", document.language) and edition in ("all", document.edition)
    )


def resolve_executable(explicit_path: str | None, command: str, label: str) -> str:
    if explicit_path:
        candidate = Path(explicit_path).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
        if candidate.is_file():
            raise PermissionError(f"{label} executable is not executable: {candidate}")
        raise FileNotFoundError(f"{label} executable does not exist: {candidate}")

    executable = shutil.which(command)
    if executable:
        return executable
    raise FileNotFoundError(f"{label} was not found. Install {label} or pass --{command} <path>.")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write_texts(entries: tuple[tuple[Path, str], ...]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for destination, content in entries:
            descriptor, name = tempfile.mkstemp(
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                text=True,
            )
            temporary = Path(name)
            staged.append((temporary, destination))
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _destination in staged:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def source_digest(document: Document) -> str:
    digest = hashlib.sha256()
    paths = sorted(path for path in document.source_dir.rglob("*") if path.is_file() and path.suffix in SOURCE_SUFFIXES)
    for path in paths:
        relative = path.relative_to(document.source_dir).as_posix().encode()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _source_inventory(language: str) -> dict[Path, str]:
    root = SOURCE_DIR / language
    return {path.relative_to(root): path.read_text(encoding="utf-8") for path in root.rglob("*") if path.is_file()}


def _structural_signature(
    text: str,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    commands = [(match.group(1), match.group(2).strip()) for match in STRUCTURAL_COMMAND_PATTERN.finditer(text)]
    environments = [(match.group(1), match.group(2).strip()) for match in ENVIRONMENT_PATTERN.finditer(text)]
    return commands, environments


def validate_source_parity() -> None:
    german = _source_inventory("de")
    english = _source_inventory("en")
    if german.keys() != english.keys():
        missing_english = sorted(str(path) for path in german.keys() - english.keys())
        missing_german = sorted(str(path) for path in english.keys() - german.keys())
        raise RuntimeError(
            f"Bilingual source inventory mismatch: missing English={missing_english}; missing German={missing_german}"
        )

    for relative in sorted(german):
        if relative.suffix != ".tex":
            continue
        if _structural_signature(german[relative]) != _structural_signature(english[relative]):
            raise RuntimeError(f"Bilingual LaTeX structure mismatch: {relative}")

    german_keys = set(BIBLIOGRAPHY_KEY_PATTERN.findall(german[Path("references.bib")]))
    english_keys = set(BIBLIOGRAPHY_KEY_PATTERN.findall(english[Path("references.bib")]))
    if german_keys != english_keys:
        raise RuntimeError("Bilingual bibliography key mismatch.")


def record_release_evidence() -> None:
    missing = [document.output_name for document in DOCUMENTS if not (PDF_DIR / document.output_name).is_file()]
    if missing:
        raise RuntimeError(f"Cannot record release evidence; PDFs missing: {', '.join(missing)}")

    checksums = [f"{_sha256(PDF_DIR / document.output_name)}  {document.output_name}" for document in DOCUMENTS]
    provenance = {
        "schema_version": 1,
        "documents": {
            document.output_name: {
                "edition": document.edition,
                "language": document.language,
                "pdf_sha256": _sha256(PDF_DIR / document.output_name),
                "source_sha256": source_digest(document),
            }
            for document in DOCUMENTS
        },
    }
    _atomic_write_texts(
        (
            (CHECKSUM_PATH, "\n".join(checksums) + "\n"),
            (PROVENANCE_PATH, json.dumps(provenance, indent=2, sort_keys=True) + "\n"),
        )
    )
    print(f"Wrote {CHECKSUM_PATH}")
    print(f"Wrote {PROVENANCE_PATH}")


def verify_provenance() -> None:
    try:
        provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read provenance manifest: {exc}") from exc
    if not isinstance(provenance, dict):
        raise TypeError("Invalid provenance manifest schema.")
    if provenance.get("schema_version") != 1 or not isinstance(provenance.get("documents"), dict):
        raise RuntimeError("Invalid provenance manifest schema.")

    records = provenance["documents"]
    expected_names = {document.output_name for document in DOCUMENTS}
    if set(records) != expected_names:
        raise RuntimeError("Provenance manifest document set does not match the release matrix.")
    if any(not isinstance(records[file_name], dict) for file_name in expected_names):
        raise RuntimeError("Invalid provenance manifest document record.")
    failures: list[str] = []
    for document in DOCUMENTS:
        record = records[document.output_name]
        if record.get("language") != document.language or record.get("edition") != document.edition:
            failures.append(f"identity mismatch: {document.output_name}")
        if record.get("source_sha256") != source_digest(document):
            failures.append(f"source checksum mismatch: {document.output_name}")
        if record.get("pdf_sha256") != _sha256(PDF_DIR / document.output_name):
            failures.append(f"provenance PDF checksum mismatch: {document.output_name}")
    if failures:
        raise RuntimeError("; ".join(failures))


def _read_checksum_manifest() -> dict[str, str]:
    try:
        lines = CHECKSUM_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"Could not read checksum manifest: {exc}") from exc

    checksums: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        fields = line.split(maxsplit=1)
        if len(fields) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", fields[0]) is None:
            raise RuntimeError(f"Invalid checksum entry on line {line_number}.")
        digest, file_name = fields
        file_name = file_name.removeprefix("*")
        if file_name in checksums:
            raise RuntimeError(f"Duplicate checksum entry on line {line_number}: {file_name}")
        checksums[file_name] = digest.lower()
    return checksums


def _pdf_inventory_failures(expected_names: set[str]) -> list[str]:
    published_names = {path.name for path in PDF_DIR.glob("*.pdf")}
    failures: list[str] = []
    unexpected = sorted(published_names - expected_names)
    missing = sorted(expected_names - published_names)
    if unexpected:
        failures.append(f"unexpected PDFs: {', '.join(unexpected)}")
    if missing:
        failures.append(f"published PDFs missing: {', '.join(missing)}")
    return failures


def _manifest_inventory_failures(actual_names: set[str], expected_names: set[str]) -> list[str]:
    failures: list[str] = []
    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    if missing:
        failures.append(f"manifest entries missing: {', '.join(missing)}")
    if extra:
        failures.append(f"unexpected manifest entries: {', '.join(extra)}")
    return failures


def verify_checksums() -> None:
    checksums = _read_checksum_manifest()

    expected_names = {document.output_name for document in DOCUMENTS}
    failures = _pdf_inventory_failures(expected_names)
    for file_name, expected_digest in checksums.items():
        path = PDF_DIR / file_name
        if path.parent != PDF_DIR or not path.is_file():
            failures.append(f"missing: {file_name}")
            continue
        actual_digest = _sha256(path)
        if actual_digest != expected_digest.lower():
            failures.append(f"checksum mismatch: {file_name}")
            continue
        print(f"OK: pdf/{file_name}")

    failures.extend(_manifest_inventory_failures(set(checksums), expected_names))
    if failures:
        raise RuntimeError("; ".join(failures))


def build(documents: tuple[Document, ...], tectonic: str, biber: str) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PATH"] = os.pathsep.join((str(Path(biber).parent), environment.get("PATH", "")))

    with tempfile.TemporaryDirectory(prefix="template-projects-case-study-") as temporary:
        temporary_dir = Path(temporary)
        completed_builds: list[tuple[Path, Path]] = []

        for document in documents:
            build_dir = temporary_dir / f"{document.language}-{document.edition}"
            build_dir.mkdir()
            print(f"Building {document.language}/{document.edition} ...", flush=True)
            completed = subprocess.run(
                [tectonic, "--outdir", str(build_dir), document.entrypoint.name],
                cwd=document.source_dir,
                env=environment,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Tectonic failed for {document.language}/{document.edition} with exit code {completed.returncode}."
                )

            generated_pdf = build_dir / f"{document.edition}.pdf"
            if not generated_pdf.is_file():
                raise RuntimeError(f"Tectonic did not create the expected file: {generated_pdf}")
            completed_builds.append((generated_pdf, PDF_DIR / document.output_name))

        for generated_pdf, destination in completed_builds:
            shutil.copy2(generated_pdf, destination)
            print(f"Wrote {destination.relative_to(CASE_STUDY_DIR)}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.verify:
            validate_source_parity()
            verify_checksums()
            verify_provenance()
            return 0
        if args.record:
            validate_source_parity()
            record_release_evidence()
            return 0
        documents = selected_documents(args.language, args.edition)
        tectonic = resolve_executable(args.tectonic, "tectonic", "Tectonic")
        biber = resolve_executable(args.biber, "biber", "Biber")
        build(documents, tectonic, biber)
    except (OSError, RuntimeError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
