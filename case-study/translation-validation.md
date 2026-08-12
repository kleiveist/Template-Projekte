# English Translation Validation

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-12 |
| Audience | Case-study maintainers and reviewers |

## Purpose

This record captures the structural, build, and fidelity validation performed for the imported English case-study edition on 12 August 2026.

## Result

**PASS**

The independent English edition is complete. Both rendering modes built
successfully, and the German and English source trees retained equivalent
document structures. Stable edition entry points now select the rendering
mode without editing the shared `main.tex` files.

## Scope

- Main document and title-page metadata: translated and localized
- Chapters 1--9, including all headings and scientific prose: translated
- Six research questions and their six answers: translated and cross-checked
- Beginner explanation layer: all 48 files translated with the consistent
  title `In simple terms:`
- Standalone and inline tables: translated
- Figures, TikZ node text, captions, and source notes: translated
- List of abbreviations and generated list headings: localized to English
- Bibliography: English APA localization enabled; project-specific notes and
  comments translated; original publication metadata retained
- LaTeX diagnostics and maintainability comments in the English copy:
  localized where relevant

## Structural comparison

| Element | German | English | Result |
|---|---:|---:|---|
| Chapter source files | 65 | 65 | Exact file-inventory match |
| Beginner-statement files | 48 | 48 | Exact file-inventory match |
| Figure source files | 18 | 18 | Exact file-inventory match |
| Standalone table source files | 9 | 9 | Exact file-inventory match |
| Main sections | 9 | 9 | Match |
| Subsections | 56 | 56 | Match |
| Research questions | 6 | 6 | Match |
| Research-question answers | 6 | 6 | Match |
| Figure environments | 18 | 18 | Match |
| Table environments, including inline tables | 11 | 11 | Match |
| Bibliography entries | 32 | 32 | Exact key match |
| Citation commands | 113 | 113 | Exact argument match |
| Labels | 94 | 94 | Exact argument match |
| Cross-references | 29 | 29 | Exact argument match |
| Shared-document inputs, including conditional statement inputs | 141 | 141 | Exact argument match |

Technical paths, profile-identifier sets, status tokens, citation keys, and
commit-hash sets were compared with the German master and retained. The
historical local-acceptance and external-CI evidence remains separately tied
to commits `1cdfb6e` and `a4487ac`.

## Build validation

The imported editions were validated with Tectonic 0.17.0 and Biber 2.17. In
the integrated project, the equivalent English build is started from the
repository root with:

```sh
python case-study/build.py --language en
```

For each mode, Tectonic completed the full TeX, Biber, TeX-rerun, and PDF
generation sequence.

| Check | Beginner enabled | Beginner disabled |
|---|---:|---:|
| Build exit status | PASS (0) | PASS (0) |
| PDF pages | 54 | 45 |
| Rendered `In simple terms:` boxes | 48 | 0 |
| LaTeX errors | 0 | 0 |
| Missing input files | 0 | 0 |
| Undefined references | 0 | 0 |
| Undefined citations | 0 | 0 |
| Overfull/underfull boxes | 0 | 0 |

The validated imported PDFs are:

- [English beginner edition](pdf/template-projects-case-study-en-beginner.pdf) -- beginner enabled, SHA-256
  `cbf13eed5ab416d961aa55dd796f671c1fd353d775791b2fb1e4496f454dd29d`
- [English scientific edition](pdf/template-projects-case-study-en-scientific.pdf) -- beginner disabled, SHA-256
  `205d1724e7e02aab966229525e183d2b18cf17fec61b330a1d3c8c120681f0a4`

An all-page visual review and full-size spot checks of tables, diagrams,
captions, lists, and beginner boxes found no clipping or margin overflow.

### Reviewed notices

The Tectonic/XeTeX run reports two non-document compatibility notices:

- `inputenc` is ignored by UTF-8-native engines.
- The bundled `biblatex-apa` language style uses the deprecated starred form
  of `\DeclareDelimAlias`.

Neither notice affects output or reference resolution. No translation-induced
layout warning remains.

## Residual German-language scan

- Source review: no unintended reader-facing German prose remains in the
  English `.tex` or `.bib` sources.
- Extracted text from both final PDFs: no hits for the project scan list of
  common German terms or phrases.
- Intentionally retained strings: the official project name
  `Template-Projekte`; internal directory, file-path, and label slugs such as
  `100_einleitung`, `200_anforderungen`, and `sec:architektur`; and the author
  name `Höst` in bibliography metadata.

## Fidelity review

Manual bilingual spot checks covered the requested high-risk sections,
figures and tables, all research-question answer pairs, profile composition,
PostgreSQL compatibility, CI and acceptance evidence, external-verification
gaps, and stated limitations. Claims, qualification, status values, versions,
URLs, dates, and quantitative facts remain content-equivalent to the German
master. No new finding or source was introduced.

## Related documents

- [Case-study overview](README.md)
- [PDF checksums](pdf/checksums.sha256)
