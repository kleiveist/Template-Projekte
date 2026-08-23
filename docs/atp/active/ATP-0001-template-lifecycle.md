<!-- AUTO-GENERATED:backlink START -->
[← Back](active.md)
<!-- AUTO-GENERATED:backlink END -->
# ATP-0001: Template lifecycle foundation

| Field | Value |
| --- | --- |
| Status | active |
| Owner | Project team |
| Created | 2026-08-23 |
| Executed | 2026-08-23 |
| Requirement | [Lifecycle acceptance](../../dev/template-lifecycle-acceptance.md) |
| Tested commit/build | `0736f1ffe993e83ce69c019b8888bf2b9f669ef1` plus the intentionally uncommitted lifecycle working tree; generated-profile snapshot `40d10782d53a8931926cf42395d774c0796b87f0` |
| Environment | Linux x86_64; Python 3.13.15 host; Node.js 24.19.0; Rust 1.97.1; Docker and native WebKitGTK development packages unavailable |

## Objective

Accept a reusable, deterministic, and rollback-safe template lifecycle foundation without migrating a concrete product or weakening existing repository gates.

## Scope

### Included

- lifecycle generation, audit, adoption, planning, update, verification, migrations, and reports;
- preservation of product source, identity, version, profile, capabilities, and user-data boundaries;
- local Git source and filesystem security boundaries;
- all five generated profiles and supported PostgreSQL variants; and
- existing quality, CI, documentation, desktop, and release regression gates.

### Excluded

- SunoDM, FMDFlashcard, and BlobFin migration;
- remote source, pull-request, publication, or release automation;
- product-data and database-data migration;
- general profile migration; and
- automatic conflict resolution.

## Risks

| Risk | Impact | Mitigation or test focus |
| --- | --- | --- |
| Product edits are mistaken for template content. | Product source can be overwritten or deleted. | Dynamic baseline ownership and BASE/LOCAL/INCOMING cases |
| An update fails after writing some paths. | Product and lifecycle state diverge. | Staging, operation journal, injected failures, and rollback verification |
| Identity or product version is normalized to template defaults. | Product releases and packaging become invalid. | Identity and version mirror assertions before and after update |
| A path, link, migration, or report escapes its root. | Local files or secrets can be exposed or modified. | Traversal, Windows path, symlink, protected-area, and secret tests |
| Existing CI pins or cross-platform probes regress. | Supported environments lose coverage. | Workflow regression tests and unchanged action/runtime pins |

## Preconditions

- [x] Required Python, Node.js, Rust, Docker, and platform dependencies are identified for each executed step.
- [x] The tested commit and complete working-tree state are recorded.
- [x] Focused tests use only disposable local Git repositories and no network.
- [ ] A disposable PostgreSQL service is available for database matrix evidence.
- [x] Test fixtures contain no secrets or production user data.

## Test data

| ID | Description | Source or setup |
| --- | --- | --- |
| TD-01 | Two-commit template history with compatible edits, an added file, and a declared path move | Temporary local Git repository created by integration tests |
| TD-02 | Product derived from TD-01 with custom identity, version, managed-file edit, and product-owned file | Temporary product Git repository created by integration tests |
| TD-03 | Overlapping edit that must conflict | Temporary local conflict fixture |
| TD-04 | Unsafe paths, external links, binary content, CRLF/LF, spaces, and UTF-8 names | Synthetic filesystem fixtures |
| TD-05 | All five profiles and three valid PostgreSQL combinations | Existing generated-project CI matrices |

## Acceptance steps

| ID | Action | Expected result | Actual result | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| `LC-001` | Generate managed products and inspect provenance. | Full template provenance is tracked. | Five profiles and three PostgreSQL variants reported generated, reproducible, valid provenance. | PASS | Focused generation tests and local matrix |
| `LC-002` | Repeat state and manifest generation. | Tracked metadata is deterministic. | Repeated state, manifest, and scaffold generation produced identical metadata. | PASS | State/manifest/generation tests |
| `LC-003` | Update a product with independent versions. | Product version and mirrors remain unchanged and valid. | End-to-end update preserved version `0.7.0`; root version mirrors passed. | PASS | Integration test and `version check` |
| `LC-004` | Update a product with custom identity. | All protected identity values remain product-owned. | Name, slug, identifier, binary, backend service, title, artifacts, and icon metadata remained intact. | PASS | Scaffold, verify, and integration tests |
| `LC-005` | Audit a legacy fixture. | Audit changes no tracked product path. | Audit completed without state and with an unchanged Git tree. | PASS | Audit tests |
| `LC-006` | Adopt a clean legacy fixture. | Only the two lifecycle metadata files are written. | Preview wrote nothing; apply wrote only `.template/state.toml` and `baseline.json`. | PASS | Adoption tests |
| `LC-007` | Plan the two-commit fixture. | Operations derive from BASE/LOCAL/INCOMING. | Planner cases and the two-commit update scenario passed. | PASS | Planner/integration tests |
| `LC-008` | Add product-owned files before update. | They remain unchanged and outside the plan. | Product-owned fixtures survived planning and apply byte-for-byte. | PASS | Planner/integration tests |
| `LC-009` | Plan and apply the conflict fixture. | Conflict returns non-zero and no product path changes. | Content and migration-destination conflicts blocked every write. | PASS | Planner/apply/integration tests |
| `LC-010` | Exercise binary and executable-mode cases. | Binary conflicts and modes follow explicit safe rules. | Binary and executable-mode cases passed. | PASS | Planner tests |
| `LC-011` | Run synthetic structural migrations twice. | Registry order is deterministic and IDs are idempotent. | Registry validation, declarative operations, postconditions, ownership, and repeat behavior passed. | PASS | Migration/apply tests |
| `LC-012` | Inject failures during apply and verify. | Every product and lifecycle path rolls back. | Staging, mid-apply, verify, and report-finalization failures restored all preimages. | PASS | Apply/report tests |
| `LC-013` | Observe state write order under failure injection. | State changes only after complete success. | Instrumentation observed product paths, baseline, then state; failures restored state. | PASS | Apply tests |
| `LC-014` | Repeat a successful update to the same commit. | Second update is a no-op. | Repeated update reported zero operations and left Git clean. | PASS | Integration/apply tests |
| `LC-015` | Introduce profile and capability drift. | Silent architecture changes are rejected. | Undeclared drift conflicted; declared migration plus confirmation was required. | PASS | Service/verify tests |
| `LC-016` | Generate and verify all five profiles. | Every profile has valid clean-source lifecycle metadata. | Five profiles and three valid PostgreSQL variants passed status/verify with final drift `0/0/0`. | PASS | Local generated-profile matrix and CI guards |
| `LC-017` | Disable network and run status/verify. | Both commands complete locally. | Network-denial fixtures and every generated profile passed. | PASS | Status/source tests and local matrix |
| `LC-018` | Exercise Git, path, symlink, and secret negative cases. | Every unsafe operation is rejected without disclosure. | Git race, traversal, external links, caches, credentials, reports, and dirty trees were rejected or redacted. | PASS | Security-focused lifecycle tests |
| `LC-019` | Exercise CLI help, JSON, reports, and documentation. | Interfaces and schemas are complete and valid. | CLI/report suites passed; documentation index/check passed. | PASS | Focused suite and docs commands |
| `LC-020` | Run existing quality, CI, release, and platform gates. | No existing guard is weakened or bypassed. | All non-native checks passed; native Tauri, Docker, live PostgreSQL, and clean-tree release evidence remain unavailable. | BLOCKED | Quality/all-suite/container/release outputs |

## Automated checks

```sh
python tools/control.py quality
python tools/control.py test --suite tools
python tools/control.py test --suite all
python tools/control.py docs check
python tools/control.py version check
python tools/control.py build web
python tools/control.py container validate
python tools/control.py build desktop --dry-run --no-clean
git diff --check
python tools/control.py release check
```

Generated-project, PostgreSQL, and native desktop matrix results must reference the same tested commit. Record exact commands, exit codes, test counts, workflow run IDs, and report paths after execution.

## Execution summary

| Check | Exit | Result |
| --- | ---: | --- |
| Focused lifecycle, CLI, CI, and documentation tests | 0 | 186 passed |
| `python tools/control.py test --suite tools` | 0 | 788 collected and passed |
| `python tools/control.py quality` | 1 | 184 files, 0 policy errors; every non-native adapter passed; Rust compiler and Clippy blocked by missing WebKitGTK packages |
| `python tools/control.py test --suite all` | 1 | Tools, schema, API, database, and frontend passed; PostgreSQL and E2E skipped by configuration; two native Tauri checks blocked by WebKitGTK |
| `python tools/control.py docs index` and `docs check` | 0 | Index generated; 31 pages checked |
| `python tools/control.py doctor` and `config doctor` | 0 | Valid; general doctor warned that Docker is unavailable |
| `python tools/control.py version check` | 0 | All seven product-version mirrors agree at `1.0.0` |
| `python tools/control.py build web` | 0 | Frontend build and release zip created in ignored output paths |
| `python tools/control.py build desktop --dry-run --no-clean` | 0 | Linux command and bundle plan validated without an artifact build |
| `python tools/control.py container validate` | 1 | All five container inputs exist; Docker executable unavailable |
| `python tools/control.py tauri doctor` | 1 | WebKitGTK and appindicator packages unavailable; additional AppImage tools warned |
| `python tools/control.py release check` | 1 | Version, identity, and Tauri security checks passed; intentionally dirty tree rejected |
| `git diff --check` | 0 | No whitespace errors |

The generated matrix used one clean local snapshot for five base profiles and the three valid PostgreSQL variants. Every init, status, JSON assertion, verify, install, post-quality zero-drift check, and applicable web or desktop dry-run passed. Web profile quality and complete suites passed. Desktop quality and complete suites reached only the native Rust checks before the same host-package block. Live PostgreSQL integration remained skipped because `DATABASE_URL_TEST` and a service were unavailable.

## Deviations

| ID | Description | Severity | Owner | Follow-up | Status |
| --- | --- | --- | --- | --- | --- |
| DEV-001 | Native Rust compiler, Clippy, Tauri tests, and Tauri doctor cannot complete without `webkit2gtk-4.1` and `javascriptcoregtk-4.1`; appindicator is also absent. | high | Environment owner | Install the documented Linux desktop development packages and rerun root plus desktop-profile gates. | open |
| DEV-002 | Docker is unavailable, so container validation cannot execute Docker/Compose probes. | medium | Environment owner | Provide Docker and rerun root plus cloud-profile container checks. | open |
| DEV-003 | No disposable PostgreSQL service or `DATABASE_URL_TEST` is available. | medium | Environment owner | Start the pinned PostgreSQL 16.15 Alpine service and rerun PostgreSQL integration suites. | open |
| DEV-004 | Release check correctly rejects the intentionally uncommitted implementation tree. | medium | Maintainer | Review and commit through the authorized workflow, then rerun `release check`; do not create a tag or release in this ATP. | open |

## Result

- Overall result: `BLOCKED`
- Summary: Lifecycle functionality and generated-profile metadata passed; external native, container, database-service, and clean-tree release evidence is incomplete.
- Residual risks: Native desktop compilation, live PostgreSQL integration, Docker validation, and the final clean-tree release gate remain open.
- Pilot readiness: `NOT READY FOR SUNODM PILOT`

## Sign-off

| Role | Name | Decision | Date |
| --- | --- | --- | --- |
| Acceptance owner | Pending | PENDING | Not yet signed |
