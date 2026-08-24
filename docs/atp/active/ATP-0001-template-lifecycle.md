<!-- AUTO-GENERATED:backlink START -->
[← Back](active.md)
<!-- AUTO-GENERATED:backlink END -->
# ATP-0001: Template lifecycle foundation

| Field | Value |
| --- | --- |
| Status | active |
| Owner | Project team |
| Created | 2026-08-23 |
| Executed | 2026-08-23; finalization rerun 2026-08-24 |
| Requirement | [Lifecycle acceptance](../../dev/template-lifecycle-acceptance.md) |
| Tested commit/build | Previous execution: `0736f1ffe993e83ce69c019b8888bf2b9f669ef1` plus its recorded working tree. Finalization: candidate derived from clean `f70d30959c856e8170e6699eff2c101d1c077be0`; exact candidate SHA belongs in Git and the external operator report. |
| Environment | Linux x86_64; Python 3.13.9; Node.js 26.2.0; Rust 1.92.0; Tectonic 0.17.0; Biber 2.17; Docker, WebKitGTK 4.1, appindicator, a live PostgreSQL service, and a GitHub API credential unavailable |

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
- [ ] A disposable PostgreSQL service is available for local database matrix evidence; exact-HEAD CI is the required fallback.
- [x] Test fixtures contain no secrets or production user data.
- [x] The candidate is synchronized to `origin/main` and automatic exact-HEAD workflows are publicly observable.
- [ ] An authenticated GitHub API path is available for `workflow_dispatch` of Release Validation.

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
| `LC-019` | Exercise CLI help, JSON, reports, and documentation. | Interfaces and schemas are complete and valid. | CLI/report/readme suites passed; PyGitIndex regenerated navigation and `docs check` validated 31 pages. | PASS | Tool suite, focused ownership tests, and docs commands |
| `LC-020` | Run existing quality, CI, release, and platform gates. | No existing guard is weakened or bypassed. | Local applicable gates and the automatic exact-HEAD Core, Profile, PostgreSQL, and Desktop workflows passed. Release Validation has no push trigger, and its API dispatch returned HTTP 401 without a token. | BLOCKED | Local gate outputs and public exact-HEAD Actions metadata |

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
| Focused ownership, lifecycle, profile, traceability, onboarding, and documentation tests | 0 | 63 passed in the focused rerun |
| `python tools/control.py test --suite tools` | 0 | 790 passed, 1 skipped in the complete tooling and case-study suite |
| `python tools/control.py quality` | 0 | 185 files, 0 errors, 0 suppressed findings; all enabled adapters passed |
| `python tools/control.py test --suite all` | 1 | Tools, schema, API, database, and frontend passed; PostgreSQL and E2E skipped; native Tauri test linking failed for missing WebKitGTK/JavaScriptCoreGTK |
| `python tools/control.py docs index` and `docs check` | 0 | Index regenerated; 31 pages checked |
| `python tools/control.py doctor` and `config doctor` | 0 | Configuration valid with the explicit CI-style `DATABASE_URL`; general doctor warned that Docker is unavailable |
| `python tools/control.py version check` | 0 | All seven product-version mirrors agree at `1.0.0` |
| `python tools/control.py build web` | 0 | Frontend build and release zip created in ignored output paths |
| `python tools/control.py build desktop --dry-run --no-clean` | 0 | Linux command and bundle plan validated without an artifact build |
| `python tools/control.py container validate` | 1 | All five container inputs exist; Docker executable unavailable |
| `python tools/control.py tauri doctor` | 1 | WebKitGTK 4.1 and appindicator unavailable; additional AppImage tools warned |
| `python case-study/build.py --verify` and case-study tests | 0 | Four rebuilt PDFs match checksums and bilingual source provenance; 12 tests passed |
| Root `template status` / `template verify` | 0 / 1 | Status correctly identifies the master template; verify correctly rejects it because lifecycle state exists only in generated products. Generated profiles are the applicable verification targets. |
| `python tools/control.py release check` | 0 | Clean candidate passed every blocking check; unsigned signing remained an explicit warning. |
| `git diff --check` | 0 | No whitespace errors |

The previous generated matrix used one clean local snapshot for five base profiles and the three valid PostgreSQL variants. The 2026-08-24 finalization reran generator/lifecycle regression tests and proved that `LICENSE` is copied and present in deterministic baselines while master-only community governance is omitted without dangling README links. An initial clean candidate exposed that a master-only community-link test still opened the intentionally omitted pull-request template inside generated products; the follow-up makes that test skip only when the complete master community package is absent and adds a generated-context regression test. The five-profile clean-candidate matrix was then repeated with exact provenance and zero lifecycle drift. Both web profiles passed every applicable local gate; desktop profiles passed non-native gates while local native linking remained blocked. The automatic exact-HEAD Desktop and PostgreSQL workflows supplied the unavailable native and live-service evidence.

## Deviations

| ID | Description | Severity | Owner | Follow-up | Status |
| --- | --- | --- | --- | --- | --- |
| DEV-001 | Native Tauri tests and Tauri doctor cannot complete locally without WebKitGTK 4.1, JavaScriptCoreGTK 4.1, and appindicator. | high | Environment owner | Exact-HEAD Desktop CI supplied Linux, macOS, and Windows native evidence; install the packages only for equivalent local execution. | resolved by CI |
| DEV-002 | Docker is unavailable, so local container validation cannot execute Docker/Compose probes. | medium | Environment owner | Use exact-HEAD Core and Release Validation container jobs or provide Docker locally. | open |
| DEV-003 | No disposable local PostgreSQL service or `DATABASE_URL_TEST` is available. | medium | Environment owner | Exact-HEAD PostgreSQL Integration supplied the live PostgreSQL 16.15 evidence. | resolved by CI |
| DEV-004 | `gh`, GitHub tokens, and Git HTTPS credentials are unavailable. The candidate reached `origin/main` and automatic workflows ran, but Release Validation dispatch returned HTTP 401. | high | Repository owner | Connect an API-authenticated GitHub capability, dispatch `Release Validation` on the unchanged candidate ref, and verify its `headSha` and conclusion. | open |

## Result

- Overall result: `BLOCKED`
- Summary: Lifecycle functionality, ownership regression tests, documentation, versioning, quality, profiles, web build, case-study, and automatic exact-HEAD Core/Profile/PostgreSQL/Desktop evidence passed; Release Validation did not run.
- Residual risks: Release Validation remains absent because this environment cannot authenticate `workflow_dispatch`; its container and reusable desktop candidate paths are therefore not final evidence.
- Pilot readiness: `NOT READY FOR SUNODM PILOT`

## Sign-off

| Role | Name | Decision | Date |
| --- | --- | --- | --- |
| Acceptance owner | Pending | PENDING | Not yet signed |
