# Template Projects Case Study

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-23 |
| Audience | Maintainers, reviewers, and readers of the case study |

## Purpose

This directory contains the publishable case study for the Template Projects repository. It keeps the German and English LaTeX sources, the beginner and scientific editions, and the reviewed PDF artifacts together without adding master-specific material to generated product projects.

## Scope

The case study is maintained in German and English. The German LaTeX source is a publication artifact rather than project documentation; all build instructions and maintenance documentation remain in English. Imported LaTeX path identifiers remain unchanged where renaming them would obscure the verified correspondence between the language editions.

The imported source is based on the [`Latex-Template` repository at commit `a031406`](https://github.com/kleiveist/Latex-Template/commit/a031406). Nested repository metadata and duplicate source trees are intentionally not retained here.

## Published editions

| Language | Edition | PDF | Source entry point |
| --- | --- | --- | --- |
| German | Beginner explanations enabled | [PDF](pdf/template-projects-case-study-de-beginner.pdf) | [beginner.tex](source/de/beginner.tex) |
| German | Scientific text only | [PDF](pdf/template-projects-case-study-de-scientific.pdf) | [scientific.tex](source/de/scientific.tex) |
| English | Beginner explanations enabled | [PDF](pdf/template-projects-case-study-en-beginner.pdf) | [beginner.tex](source/en/beginner.tex) |
| English | Scientific text only | [PDF](pdf/template-projects-case-study-en-scientific.pdf) | [scientific.tex](source/en/scientific.tex) |

The four PDFs are the only canonical release artifacts. Their reviewed checksums are recorded in [checksums.sha256](pdf/checksums.sha256), while [provenance.json](pdf/provenance.json) binds each PDF checksum to the current language-source digest. The source history includes the German scientific artifact from upstream commit [`76b8efe`](https://github.com/kleiveist/Latex-Template/commit/76b8efe), the German beginner artifact from [`32c6eca`](https://github.com/kleiveist/Latex-Template/commit/32c6eca), and the English artifacts introduced with [`a031406`](https://github.com/kleiveist/Latex-Template/commit/a031406). The current artifacts are rebuilt and reviewed from the integrated entry points whenever published content changes.

## Source structure

```text
case-study/
├── build.py
├── pdf/                    Reviewed release PDFs and checksums
├── source/
│   ├── de/
│   │   ├── main.tex       Shared German document composition
│   │   ├── beginner.tex   Beginner-edition entry point
│   │   ├── scientific.tex Scientific-edition entry point
│   │   └── workspace/      Chapters, figures, statements, and tables
│   └── en/                 Equivalent English source structure
├── tests/                  Structure, entry-point, and artifact checks
└── translation-validation.md
```

Each language has one source tree. `main.tex` controls chapter order, `preamble.tex` owns shared typesetting settings, and `references.bib` owns the bibliography. The thin edition entry points select whether the 49 beginner explanations are rendered. The existing `workspace/{chapters,figures,statement,tables}` hierarchy remains unchanged so individual sections stay reusable and reviewable.

## Build

This is a master-maintenance helper and therefore intentionally lives beside the publication instead of in the product-facing `tools/control.py` dispatcher. Tectonic is the supported build engine because it coordinates the required TeX, Biber, and rerun sequence. Both `tectonic` and `biber` must be available, and TeX Gyre Heros must be installed as a system font so XeTeX can preserve the publication's Unicode glyphs. The current artifacts were validated with Tectonic 0.17.0 and Biber 2.17.

Build all four editions from the repository root:

```sh
python case-study/build.py
```

Build one language or edition:

```sh
python case-study/build.py --language en
python case-study/build.py --language de --edition scientific
```

If either executable is not on `PATH`, pass it explicitly:

```sh
python case-study/build.py \
  --tectonic <path-to-tectonic> \
  --biber <path-to-biber>
```

The build is isolated in a temporary directory and updates the selected files in `case-study/pdf/` only after every selected edition builds successfully. It does not leave LaTeX intermediates in the source trees. Generated PDFs are candidates until their content and layout have been reviewed and `pdf/checksums.sha256` has been refreshed.

## Maintenance workflow

1. Change content inside the applicable language source tree.
2. Keep the German and English file inventories structurally aligned.
3. Build both editions for every changed language.
4. Review tables, diagrams, references, citations, and page layout in the generated PDFs.
5. Update [translation-validation.md](translation-validation.md) when translated content changes.
6. After all four PDFs pass review, atomically refresh their checksums and source provenance with `python case-study/build.py --record`.

## Verification

Verify bilingual structural parity, the reviewed PDF checksums, and source/PDF provenance:

```sh
python case-study/build.py --verify
```

Verification fails if the German and English source inventories, structural LaTeX references, citation keys, or environment structure diverge. It also fails when a source changes after the reviewed PDFs were recorded, even if the PDF files themselves still match the older checksum manifest.

Verify the build interface without changing an artifact:

```sh
python case-study/build.py --help
```

## Related documents

- [English translation validation](translation-validation.md)
- [Documentation standard](../docs/README.md)
- [Template final acceptance](../docs/dev/template-final-acceptance.md)
