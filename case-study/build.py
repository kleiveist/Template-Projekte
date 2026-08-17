from __future__ import annotations

import argparse
import hashlib
import os
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
    parser.add_argument(
        "--verify",
        action="store_true",
        help="verify published PDFs against pdf/checksums.sha256 without building",
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


def verify_checksums() -> None:
    try:
        lines = CHECKSUM_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"Could not read checksum manifest: {exc}") from exc

    expected_names = {document.output_name for document in DOCUMENTS}
    actual_names: set[str] = set()
    failures: list[str] = []

    published_names = {path.name for path in PDF_DIR.glob("*.pdf")}
    unexpected_pdfs = sorted(published_names - expected_names)
    missing_pdfs = sorted(expected_names - published_names)
    if unexpected_pdfs:
        failures.append(f"unexpected PDFs: {', '.join(unexpected_pdfs)}")
    if missing_pdfs:
        failures.append(f"published PDFs missing: {', '.join(missing_pdfs)}")

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        fields = line.split(maxsplit=1)
        if len(fields) != 2 or len(fields[0]) != 64:
            raise RuntimeError(f"Invalid checksum entry on line {line_number}.")
        expected_digest, file_name = fields
        file_name = file_name.removeprefix("*")
        actual_names.add(file_name)
        path = PDF_DIR / file_name
        if path.parent != PDF_DIR or not path.is_file():
            failures.append(f"missing: {file_name}")
            continue
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest != expected_digest.lower():
            failures.append(f"checksum mismatch: {file_name}")
            continue
        print(f"OK: pdf/{file_name}")

    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        if missing:
            failures.append(f"manifest entries missing: {', '.join(missing)}")
        if extra:
            failures.append(f"unexpected manifest entries: {', '.join(extra)}")
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
            verify_checksums()
            return 0
        documents = selected_documents(args.language, args.edition)
        tectonic = resolve_executable(args.tectonic, "tectonic", "Tectonic")
        biber = resolve_executable(args.biber, "biber", "Biber")
        build(documents, tectonic, biber)
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
