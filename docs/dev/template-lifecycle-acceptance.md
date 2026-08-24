<!-- AUTO-GENERATED:backlink START -->
[← Back](dev.md)
<!-- AUTO-GENERATED:backlink END -->
# Template lifecycle acceptance

| Field | Value |
| --- | --- |
| Status | Active |
| Acceptance | PASS — all LC-001 through LC-020 requirements passed |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Developers, reviewers, and acceptance owners |
| Related ATP | [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md) |

## Purpose

This document maps the reusable template lifecycle requirements to executed automated and acceptance evidence. It does not mark implementation as accepted merely because code or documentation exists.

## Scope

### Included

- provenance and deterministic state for generated products;
- safe legacy audit and adoption;
- BASE/LOCAL/INCOMING planning and merge behavior;
- declarative structural migrations;
- transactional update and rollback;
- profile, identity, version, Git, path, symlink, and secret boundaries;
- CLI, reports, documentation, CI, and regression gates; and
- readiness for a later SunoDM pilot.

### Excluded

- migration of Suno Documentation Manager, FMDFlashcard, or BlobFin;
- product-specific logic or user-data transformation;
- remote source resolution and GitHub automation;
- general profile migration; and
- automatic conflict resolution.

## Evidence policy

Only an executed check with its real result can move an item from `NOT RUN`. A code path, test definition, or workflow step is not by itself passing evidence. Use only `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN` in this matrix. Record exact commands, exit codes, test counts, and report paths in [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md).

## Acceptance matrix

| ID | Requirement | Planned evidence | Status | Current evidence |
| --- | --- | --- | --- | --- |
| `LC-001` | New products store complete template provenance. | All-profile generation tests and generated CI status output | PASS | Focused generation tests and the five-profile local matrix passed provenance assertions. |
| `LC-002` | State and baseline manifests are deterministic. | Repeated-generation and manifest serialization tests | PASS | State, manifest, repeated-generation, sorting, and digest tests passed. |
| `LC-003` | Template and product versions remain separate. | Update/version mirror tests and `version check` | PASS | End-to-end update assertions passed; root `version check` passed for all mirrors. |
| `LC-004` | Product identity survives updates. | Identity normalization and integration tests | PASS | Identity normalization, drift detection, and end-to-end preservation tests passed. |
| `LC-005` | Audit is non-destructive for legacy products. | Audit fixture plus tracked-tree hash comparison | PASS | Audit without state passed with unchanged tracked-tree evidence. |
| `LC-006` | Adoption changes only lifecycle metadata. | Clean legacy fixture and before/after path comparison | PASS | Adoption preview/apply tests proved that only the two lifecycle files are written. |
| `LC-007` | Planning uses BASE/LOCAL/INCOMING. | Planner unit cases and two-commit integration fixture | PASS | Planner cases A–J and the local two-commit integration scenario passed. |
| `LC-008` | Product-added files remain untouched. | Product-owned file planning and apply tests | PASS | Planner and integration tests preserved product-owned paths. |
| `LC-009` | Conflicts prevent every partial apply. | Overlapping edit integration test and tree digest comparison | PASS | Conflict and migration-destination collision tests proved zero partial writes. |
| `LC-010` | Binary files and file modes are safe. | Binary conflict and executable-mode tests | PASS | Binary and executable-mode planner/apply tests passed. |
| `LC-011` | Structural migrations are versioned and idempotent. | Registry uniqueness, ordering, idempotence, and state tests | PASS | Declarative registry, conditions, ordering, idempotence, ownership, and state tests passed. |
| `LC-012` | Apply is transactional and rollback-capable. | Injected apply failure and rollback tests | PASS | Mid-apply, staged migration, verifier, and report-finalizer failures all rolled back. |
| `LC-013` | State is updated only after complete success. | Write-order and failure-injection tests | PASS | Instrumented write-order and failure-injection tests passed. |
| `LC-014` | Repeating an update to the same commit is a no-op. | Successful update integration scenario repeated once | PASS | The repeated end-to-end update produced zero operations and no writes. |
| `LC-015` | Profiles and capabilities do not change silently. | Selection drift and architecture-change tests | PASS | Selection drift was rejected; an architecture change required a declared migration and confirmation. |
| `LC-016` | All five profiles contain valid lifecycle metadata. | Five-entry CI matrix with status and verify | PASS | Five profiles and three PostgreSQL variants passed status, JSON provenance assertions, and verify with zero drift. |
| `LC-017` | Status and verify work without network access. | Offline subprocess tests and generated CI execution | PASS | Network-denial tests and all local generated-profile checks passed. |
| `LC-018` | Git, path, symlink, and secret boundaries are enforced. | Local Git fixtures and negative security tests | PASS | Git race, path traversal, external symlink, protected runtime, secret redaction, and dirty-tree tests passed. |
| `LC-019` | CLI, documentation, and reports are complete. | CLI help/JSON tests, docs check, and report schema tests | PASS | CLI/report/readme tests passed; PyGitIndex regeneration completed and `docs check` validated 31 pages. |
| `LC-020` | Existing quality, CI, and release gates remain intact. | Quality, complete tests, workflow guards, builds, and release check | PASS | Local applicable gates and clean-tree `release check` passed. Core CI `32718326180`, Desktop CI `32718326136`, PostgreSQL Integration `32718326135`, Profile Matrix `32718326078`, and Release Validation `32731628645` all passed on release commit `a09c0b9`. |

## Required automated coverage

Focused tests live under `tools/tests/template_lifecycle/` and are included automatically by:

```sh
python tools/control.py test --suite tools
```

The test fixtures use only local temporary Git repositories. They must cover clean and dirty generation, deterministic manifests, version and identity preservation, all planner cases, binary and mode behavior, migrations, source validation, paths with spaces, UTF-8 names, CRLF/LF handling, symlink rejection, transactional rollback, adoption, audit, CLI help, JSON output, and both successful and conflicting end-to-end updates.

## Verification

The final acceptance execution records the actual result of each applicable command:

```sh
python tools/control.py doctor
python tools/control.py config doctor
python tools/control.py quality
python tools/control.py test --suite tools
python tools/control.py test --suite all
python tools/control.py docs check
python tools/control.py version check
python tools/control.py build web
python tools/control.py container validate
python tools/control.py build desktop --dry-run --no-clean
git diff --check
```

The five generated profiles additionally run lifecycle status and verify, quality, and the complete applicable suite. Desktop profiles run Tauri diagnostics and the desktop dry-run. Backend profiles run configuration diagnostics. Valid PostgreSQL combinations run against the existing isolated service matrix.

`release check` is executed on the clean candidate commit and recorded in the external operator report. A dirty-tree failure before that commit is release-state evidence, not a lifecycle functional failure, and must not be reported as a passing release gate.

## Previous blockers and current disposition

| Previous blocker | Current disposition |
| --- | --- |
| WebKitGTK, JavaScriptCoreGTK, and appindicator were unavailable locally. | The local limitation remains documented. Exact-SHA Desktop CI and Release Validation supplied successful native Linux, macOS, and Windows evidence. |
| Docker was unavailable locally. | The local limitation remains documented. Exact-SHA Core CI and Release Validation supplied successful container validation and build evidence. |
| No disposable PostgreSQL service or `DATABASE_URL_TEST` was available. | The local limitation remains documented. Exact-SHA PostgreSQL Integration supplied successful live-service, migration, API, and profile evidence. |
| The lifecycle implementation was intentionally uncommitted, so `release check` rejected the dirty tree. | The repository began this finalization clean at `f70d30959c856e8170e6699eff2c101d1c077be0`; the final clean candidate passed `release check`. |
| GitHub and Desktop CI evidence existed only for earlier commits. | Resolved: all four automatic workflows and tag-triggered Release Validation passed on release commit `a09c0b9`; the exact run IDs are recorded in the completed ATP. |

## Decision rule

The lifecycle foundation is `READY FOR SUNODM PILOT` only when all `LC-001` through `LC-020` requirements have passing evidence and no unresolved safety or rollback defect remains. Otherwise the decision is `NOT READY FOR SUNODM PILOT`, with every blocker listed in ATP-0001 and the final implementation report.

Current decision: `READY FOR SUNODM PILOT`. LC-001 through LC-020 passed, and the five required workflows succeeded on the exact released commit `a09c0b9998881e3dbbbd6292fdd22715b402bee8`.

## Risks and limitations

- Local source resolution is the only supported source mechanism in version 1.
- No concrete product migration is included.
- Native Linux Tauri, container, and live PostgreSQL execution remained unavailable on the local acceptance host; exact-SHA workflows supplied that evidence.
- Desktop packages remain unsigned verification artifacts rather than production-signed product installers.
- The accepted release commit and workflow run IDs are recorded in the completed ATP and remain externally verifiable.

## Related documents

- [Template lifecycle](../def/template-lifecycle.md)
- [Template migrations](../tools/template-migrations.md)
- [Framework architecture](../def/architecture.md)
- [Project profiles](../def/project-profiles.md)
- [Continuous integration](../tools/ci.md)
- [ATP workflow](../atp/README.md)
- [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md)
