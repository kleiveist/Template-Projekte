# English Translation Validation

| Field | Value |
| --- | --- |
| Status | PASS |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Case-study maintainers and reviewers |

## Purpose

This record captures the structural, substantive, build, artifact-freshness,
and targeted layout validation of the bilingual v1.0.0 case-study edition. The
historical governance analysis remains tied to technical baseline
`461fc7519e0db638330904a7496c488e8a0d18bc`; after successful exact-HEAD
validation, the exact candidate will be recorded in GitHub Actions evidence
and the final operator report rather than embedded in its own source. No
release tag is published.

## Result

**PASS**

The English edition now contains the governance material that was previously
present only in German, including its evidence qualifications and documented
limitations. Both languages also contain the concise v1.0.0 candidate-validation
addendum. The final candidate state is synchronized for Node 24, PostgreSQL
16.15, the dedicated tooling runtime, and the Rust analyzer built with rustc
1.97.1 and Syn 2.0.119 and executed through Wasmtime 47.0.1. All four
language/edition combinations built successfully, their reviewed checksums
were refreshed, and source/PDF provenance was recorded.

## Scope

- Main document and title-page metadata: translated and localized
- Chapters 1--9, including the full Governance v1 extension: translated
- Six research questions and their six answers: translated and cross-checked
- Beginner explanation layer: all 49 files translated with the consistent
  English title `In simple terms:`
- Standalone and inline tables: translated
- Figures, TikZ node text, captions, and source notes: translated
- List of abbreviations and generated list headings: localized to English
- Bibliography: exact key parity; English localization applied to project notes
- v1.0.0 candidate-validation addendum: bilingual and non-self-referential
- Historical Ruff-resolution failure and corrected v1.0.0 candidate `tools/.venv`
  contract: explicitly separated in both languages and beginner explanations
- Analyzer build/runtime contract: synchronized for the exact rustc 1.97.1
  commit, Syn 2.0.119, proc-macro2 1.0.107, `wasm32-wasip1`, Wasmtime 47.0.1,
  the source-input digest, versioned path remapping, private-path exclusion,
  and three relocated Linux builds; no cross-OS byte identity is claimed

## Structural comparison

| Element | German | English | Result |
|---|---:|---:|---|
| Chapter source files | 66 | 66 | Exact file-inventory match |
| Beginner-statement files | 49 | 49 | Exact file-inventory match |
| Figure source files | 18 | 18 | Exact file-inventory match |
| Standalone table source files | 9 | 9 | Exact file-inventory match |
| Main sections | 9 | 9 | Match |
| Subsections | 57 | 57 | Match |
| Research questions | 6 | 6 | Match |
| Research-question answers | 6 | 6 | Match |
| Figure environments | 18 | 18 | Match |
| Table environments, including inline tables | 15 | 15 | Match |
| Bibliography entries | 46 | 46 | Exact key match |
| Citation commands | 142 | 142 | Exact command and argument match |
| Labels | 99 | 99 | Exact argument match |
| Cross-references | 39 | 39 | Exact argument match |
| Shared-document inputs, including conditional statement inputs | 145 | 145 | Exact argument match |

`python case-study/build.py --verify` now enforces matching source inventories,
per-file structural LaTeX signatures, and bibliography keys before validating
the release artifacts. Regression tests also prove that a changed label or
source digest is rejected.

## Build and artifact validation

The four editions were rebuilt from the repository root on 24 August 2026 with
Tectonic 0.17.0, Biber 2.17, and staged TeX Gyre Heros fonts:

```sh
python case-study/build.py \
  --tectonic /tmp/.../tectonic \
  --biber /tmp/.../biber
python case-study/build.py --record
python case-study/build.py --verify
```

The temporary executable paths are abbreviated because they are environment
details, not repository contracts. Tectonic completed its TeX, Biber, rerun,
and PDF-generation sequence for every document.

| Check | German beginner | German scientific | English beginner | English scientific |
|---|---:|---:|---:|---:|
| Build exit status | PASS (0) | PASS (0) | PASS (0) | PASS (0) |
| PDF pages | 70 | 59 | 68 | 57 |
| Beginner boxes | 49 | 0 | 49 | 0 |
| Missing inputs | 0 | 0 | 0 | 0 |
| Undefined references or citations | 0 | 0 | 0 | 0 |

The reviewed PDFs and SHA-256 values are:

- [German beginner edition](pdf/template-projects-case-study-de-beginner.pdf):
  `82b475b38a3d71ab4df18d1f7a44574856a2c836a65961e470cc06ff83e29a7d`
- [German scientific edition](pdf/template-projects-case-study-de-scientific.pdf):
  `e1b8368834d2b6b65176d20000680f49ac456103e178b368ba4f8f806e1d8a5a`
- [English beginner edition](pdf/template-projects-case-study-en-beginner.pdf):
  `5dd368eabaaac34fb9b72b8e1a14cf969562db41241d36fbfe4bf3c9b7419d0e`
- [English scientific edition](pdf/template-projects-case-study-en-scientific.pdf):
  `c84f89dd54d1b6e49e5f5474f24ee3326d270fae3f32d8100a46585a4850857f`

The German source-tree digest is
`6bf452a92e787fc637463f00c61c85a80fcf725bf4e379d99021ee36fd846cf3`;
the English source-tree digest is
`e97801035be260d209122339012998e54c958c05dd48cd946a85c8bff88241b8`.
The machine-readable mapping in [provenance.json](pdf/provenance.json) binds
these source digests to each PDF checksum. Editing either language after the
recorded build now makes `--verify` fail even when an older PDF still matches
the checksum file. `--record` stages both evidence files, flushes them, and
publishes them through atomic replacements.

## Targeted layout review

Rendered full-page checks covered both title pages; the bilingual quality
threshold, language-tool, and technology-stack tables; Node 24 and PostgreSQL
16.15 references; the Syn/WASI/Wasmtime analyzer description; the historical
and corrected tooling-runtime contract; the governance control-flow diagrams;
the release addenda; updated beginner boxes in each language; and the final
bibliography pages. No clipping, overlap, broken diagram edge, blank spill
page, or margin escape was found on those pages.

The TeX engine still reports existing overfull and underfull box warnings in
shared content and warns that system font paths reduce cross-environment build
reproducibility. These notices are not hidden or reclassified as errors. They
did not prevent artifact creation, but the targeted review is not a claim that
every line on every page received a new manual visual inspection.

## Residual German-language scan

- Source scan: no hits for the selected common German reader-facing terms in
  English `.tex` or `.bib` sources.
- Extracted text from both English PDFs: no hits for the same scan list.
- Intentionally retained strings: the official project name
  `Template-Projekte`; stable internal path and label slugs such as
  `100_einleitung`, `200_anforderungen`, and `sec:architektur`; and personal
  names in bibliography metadata.

## Fidelity review

The English changes preserve the German edition's distinction among intended
policy, observed implementation, executed evidence, inference, and limitation.
In particular, the historical Ruff-resolution, exception-validation, CQ001,
native-library, documentation, and CI findings remain attributed to baseline
`461fc751`. The installation chapter now also records that the candidate state
always provides the dedicated `tools/.venv`; this correction does not rewrite
the historical profile failures as passes. The v1.0.0 addendum separately
records the candidate criteria that close those gaps.

## Related documents

- [Case-study overview](README.md)
- [PDF checksums](pdf/checksums.sha256)
- [PDF/source provenance](pdf/provenance.json)
