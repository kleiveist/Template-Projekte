# English Translation Validation

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-13 |
| Audience | Case-study maintainers and reviewers |

## Purpose

This record captures the structural, build, layout, and fidelity validation of
the current bilingual case-study publication on 13 August 2026.

## Result

**PASS**

The independent English edition remains complete after the provider-neutral
persistence extension. All four language/edition combinations built
successfully, and the German and English source trees retain equivalent
document structures. Stable edition entry points select the rendering mode
without editing the shared `main.tex` files.

## Scope

- Main document and title-page metadata: translated and localized
- Chapters 1--9, including all headings and scientific prose: translated
- Six research questions and their six answers: translated and cross-checked
- Beginner explanation layer: all 49 files translated with the consistent
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
| Chapter source files | 66 | 66 | Exact file-inventory match |
| Beginner-statement files | 49 | 49 | Exact file-inventory match |
| Figure source files | 18 | 18 | Exact file-inventory match |
| Standalone table source files | 9 | 9 | Exact file-inventory match |
| Main sections | 9 | 9 | Match |
| Subsections | 57 | 57 | Match |
| Research questions | 6 | 6 | Match |
| Research-question answers | 6 | 6 | Match |
| Figure environments | 18 | 18 | Match |
| Table environments, including inline tables | 11 | 11 | Match |
| Bibliography entries | 33 | 33 | Exact key match |
| Citation commands | 117 | 117 | Exact argument match |
| Labels | 95 | 95 | Exact argument match |
| Cross-references | 29 | 29 | Exact argument match |
| Shared-document inputs, including conditional statement inputs | 143 | 143 | Exact argument match |

Technical paths, profile-identifier sets, status tokens, citation keys, and
commit-hash sets were compared with the German master and retained. The new
persistence source is tied to commit `7257776`; the historical local-acceptance
and external-CI evidence remains separately tied to commits `1cdfb6e` and
`a4487ac`.

## Build validation

The current editions were validated with Tectonic 0.17.0 and Biber 2.17. In
the integrated project, the English build is started from the
repository root with:

```sh
python case-study/build.py --language en
```

For each mode, Tectonic completed the full TeX, Biber, TeX-rerun, and PDF
generation sequence.

| Check | Beginner enabled | Beginner disabled |
|---|---:|---:|
| Build exit status | PASS (0) | PASS (0) |
| PDF pages (English) | 55 | 46 |
| Rendered `In simple terms:` boxes | 49 | 0 |
| LaTeX errors | 0 | 0 |
| Missing input files | 0 | 0 |
| Undefined references | 0 | 0 |
| Undefined citations | 0 | 0 |
| New-content clipping or overlap in targeted visual review | 0 | 0 |

The validated current PDFs are:

- [English beginner edition](pdf/template-projects-case-study-en-beginner.pdf) -- beginner enabled, SHA-256
  `43db4a9bf120938a2fee469b32a6de8542998b0d29ea0e3ddc04f4a5c8c61319`
- [English scientific edition](pdf/template-projects-case-study-en-scientific.pdf) -- beginner disabled, SHA-256
  `f71ca8f2459dc61424750fd83e7e95ac3be55617ca9a5cbf494a0ccf00276956`

The German editions contain 55 beginner and 46 scientific pages. Relative to
the preceding release, page counts changed from 55/45 to 55/46 in German and
from 54/45 to 55/46 in English; every edition therefore remains within the
accepted one-page growth limit.

A targeted visual review covered the table of contents, sections 3.7 and 3.8,
the new beginner box, the transition into chapter 4, and all bibliography
pages in all four PDFs. Full-size spot checks found no clipping, overlap,
broken page transition, isolated heading, or margin overflow.

### Reviewed notices

The Tectonic/XeTeX run reports two non-document compatibility notices:

- `inputenc` is ignored by UTF-8-native engines.
- The bundled `biblatex-apa` language style uses the deprecated starred form
  of `\DeclareDelimAlias`.

Neither notice affects output or reference resolution. The build also reports
pre-existing overfull and underfull box warnings in shared content. The new
commit-fixed bibliography URL is line-breakable, remains inside the page
boundary, and caused no annotation-boundary warning in the final build.

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

Manual bilingual spot checks covered the provider-neutral persistence section,
its beginner explanation, the related architecture/profile/assessment/transfer
passages, the changed system-architecture figure, and the affected research
question. The four storage classes, source-of-truth responsibility, and future
extension paths have equivalent qualification in both languages. Claims,
status values, versions, URLs, dates, and quantitative facts remain
content-equivalent to the German master; the persistence source is the only
new bibliography entry.

## Related documents

- [Case-study overview](README.md)
- [PDF checksums](pdf/checksums.sha256)
