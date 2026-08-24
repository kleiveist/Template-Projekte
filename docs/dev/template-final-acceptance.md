<!-- AUTO-GENERATED:backlink START -->
[← Back](dev.md)
<!-- AUTO-GENERATED:backlink END -->
# Template v1.0.0 final acceptance

| Field | Value |
| --- | --- |
| Status | Candidate validation blocked by unavailable Release Validation dispatch; not published |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Maintainers, reviewers, and release operators |
| Version | `1.0.0` |
| Published release tag | None |
| Intended future tag | `v1.0.0` |
| Historical architecture baseline | `461fc7519e0db638330904a7496c488e8a0d18bc` |
| Related ATP | N/A — repository-wide release acceptance |

## Purpose and authoritative identity

This protocol defines the technical and documentary validation of the reusable web, cloud, and desktop template candidate at version 1.0.0. The historical baseline above is a comparison point, not the release target or validated migration baseline. While no tag exists, the authoritative validated candidate is the common `headSha` of the successful required GitHub Actions runs and the final operator report. If a tag is later published, its commit is resolved with:

```sh
git rev-parse 'v1.0.0^{}'
```

The exact final SHA is deliberately not embedded in a file that participates in that commit. It is recorded in Git, GitHub Actions evidence, and the final operator report. A future annotated tag, GitHub Release, or external release manifest must identify that same SHA.

Candidate validation is `PASS` only when every technical condition in [Validation and publication decisions](#validation-and-publication-decisions) is true for one common commit. Publication is a separate decision: while the tag is absent, lightweight, points elsewhere, or lacks complete same-SHA evidence, version 1.0.0 remains `NOT PUBLISHED`; no earlier green run may substitute for either decision.

## Scope

Acceptance includes:

- the master CLI, configuration, quality policy, architecture checks, tests, builds, and release gate;
- all five generated profiles and the two safely rejected PostgreSQL-incompatible combinations;
- all three valid PostgreSQL combinations against a real disposable PostgreSQL service;
- frontend, FastAPI, SQLAlchemy, Alembic, Psycopg, Tauri, Rust, Compose, and production dependency locks;
- the portable Syn/WASI Rust analyzer, its provenance, reproducible build, and Wasmtime host;
- Core, profile, PostgreSQL, desktop, documentation, and release-validation workflows; and
- English repository documentation, the bilingual case study, four PDF editions, provenance, and checksums.

It does not certify a generated product's business rules, production credentials, provider deployment, signing, notarization, updater, authentication, privacy declarations, backups, or operational support. Those remain product-owned decisions.

## Required validation environments

This table defines the pinned or hosted environments required by the acceptance protocol. It is not a claim that every row has executed on the current candidate. The actual local environment, unavailable prerequisites, and executed results are recorded in [ATP-0001](../atp/active/ATP-0001-template-lifecycle.md); unavailable local native, container, and database paths require successful exact-HEAD workflow evidence.

| Area | Required environment or evidence source |
| --- | --- |
| Browser and tooling | Node.js 24.19.0; npm 11; dedicated `tools/.venv` with Wasmtime 47.0.1 |
| Python application matrix | CPython 3.11.16 with isolated backend and tooling environments |
| Rust and Tauri | Rust 1.97.1; `wasm32-wasip1`; Tauri CLI 2.11.4; WebKitGTK 4.1 on Linux |
| Database | PostgreSQL 16.15 on a disposable non-default local port |
| Deployment model | Docker Compose 5.4.0 model validation |
| Remote native matrix | GitHub-hosted Ubuntu, macOS, and Windows runners on the candidate commit |

Local Docker image assembly depends on access to the Docker daemon. When the operator account cannot access the daemon, provider-neutral image assembly must be proven by successful Core and Release Validation jobs on the candidate commit and the local limitation remains explicit.

## Code quality and architecture result

The public gate is:

```sh
python tools/control.py quality
```

The accepted result is `PASS` with zero errors and zero suppressed findings. Warnings and strong warnings remain visible and non-blocking; they are not promoted, hidden, or cleared with exceptions. No manual exception is present in the candidate baseline.

The central policy enforces these boundaries:

| Metric | Warning | Strong warning | Error |
| --- | ---: | ---: | ---: |
| File code LOC | 601 | 751 | 901 |
| Physical file lines | 1201 | N/A | N/A |
| Function code LOC | 51 | 81 | 121 |
| Class code LOC | 301 | 501 | 701 |
| Complexity | 11 | 16 | 21 |
| Nesting | 4 | 5 | 6 |
| Parameters | 6 | 9 | 11 |

Exactly 900 code lines are allowed with a strong warning. Exactly 901 code lines produce the unsuppressible `CQ001 ERROR` and a non-zero exit code. A file below 900 code lines is not automatically clean or well-architected.

The gate also validates exception records, configured excludes, backend/frontend/tooling dependency direction, thin transport boundaries, Ruff, ESLint, Prettier, TypeScript, rustfmt, Clippy, Cargo compilation, and fail-closed Python, TypeScript, and Rust AST metrics.

### Portable Rust analyzer

Rust syntax and scope metrics use the committed `rust_quality_analyzer.wasm`, compiled from the adjacent Syn 2.0.119 crate for `wasm32-wasip1`. The accepted 535,787-byte artifact has SHA-256 `7a27cb02a9392b62c487b4ce73a03524d7260b804c0c49eb4520ceb1a1cacfd8`. Provenance binds it to the exact Rust 1.97.1 compiler commit, target and dependency versions, and a source digest over `build.py`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, and `src/**/*.rs`.

The versioned path-remapping contract canonicalizes source, user-home, Cargo-home, Cargo-target, Rust-sysroot, and dependency roots after inherited compiler, flag, target, and release-profile overrides are removed. Broad roots are remapped before more specific roots. Three relocated builds on the pinned Rust 1.97.1 Linux builder—the registry layout, alternate homes and targets containing spaces, and an in-tree vendored layout—produced identical bytes. This is Linux release-builder evidence, not a cross-OS byte-identity guarantee. Core CI and Release Validation rebuild and compare on Ubuntu; macOS and Windows Desktop jobs execute the checked-in artifact without rebuilding it.

`build.py --check` must reproduce the same bytes. The host requires the exact Wasmtime 47.0.1 distribution, verifies every digest and the ABI before execution, uses a strict UTF-8 subprocess contract, inherits no environment, preopens no directories, applies memory and instance limits, and fails closed on invalid syntax, payload drift, or fuel exhaustion.

The analyzer artifact and provenance must be copied byte-for-byte into every generated profile. Web-only consumers run it without a native Rust installation.

## Master acceptance commands

The operator executes these public paths on the same working tree. Every locally applicable path must succeed; an unavailable native, container, or service prerequisite is recorded as `BLOCKED` and must be supplied by the corresponding exact-HEAD workflow rather than reported as a local pass:

```sh
python tools/control.py install --skip-playwright
python tools/control.py doctor
python tools/control.py config doctor
python tools/control.py quality
python tools/control.py version check
python tools/control.py test --suite all --report
python tools/control.py build web
python tools/control.py docs check
python tools/control.py tauri doctor
python tools/control.py build desktop --dry-run --no-clean
```

The analyzer crate additionally passes locked format, Clippy, check, test, relocated and vendored reproducible WASI-build, private-path exclusion, real-host, malformed-syntax, ABI, digest-drift, large-input, and resource-limit tests. The external PyGitIndex regeneration is run after documentation changes; the independent `docs check` must then report no semantic drift. After the candidate commit is created and the tree is clean, `python tools/control.py release check` must also pass.

Feature-disabled suites may report `SKIP`. An enabled missing dependency, unavailable configured database, syntax failure, quality error, or failed build remains a failure.

## Required profile matrix

Every row must be generated into a fresh target and run install, Doctor, configuration Doctor, Quality, the profile-aware full test suite, and the production web build. Desktop rows additionally run Tauri Doctor and the desktop dry-run; cloud rows validate their Compose model. The `PASS` cells below are acceptance requirements, not current candidate results; current results and blockers are recorded in ATP-0001 and the external operator report.

| Profile | Generate | Doctor and config | Quality | Tests | Web build | Desktop checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `web-only` | PASS | PASS | PASS | PASS | PASS | N/A |
| `web-cloud` | PASS | PASS | PASS | PASS | PASS | N/A |
| `desktop-local` | PASS | PASS | PASS | PASS | PASS | PASS |
| `desktop-cloud` | PASS | PASS | PASS | PASS | PASS | PASS |
| `full-platform` | PASS | PASS | PASS | PASS | PASS | PASS |

The generator must leave the master unchanged, copy the governance policy and agent instructions, preserve the dedicated tooling runtime, omit disabled technologies, and reject non-empty or unsafe targets.

## Required PostgreSQL matrix

Each valid row must use a real PostgreSQL 16.15 connection, configuration validation, `SELECT 1`, Alembic upgrade/current checks, API and database tests, the complete profile suite, Quality, web build, and container-model validation. Desktop rows also run Tauri checks. The `PASS` cells below are the required acceptance outcome; actual exact-HEAD PostgreSQL workflow evidence is recorded externally.

| Generated variant | Connection | Migration | API and profile tests | Quality | Result |
| --- | ---: | ---: | ---: | ---: | ---: |
| `web-cloud + postgres` | PASS | PASS | PASS | PASS | PASS |
| `desktop-cloud + postgres` | PASS | PASS | PASS | PASS | PASS |
| `full-platform + postgres` | PASS | PASS | PASS | PASS | PASS |

`web-only + postgres` and `desktop-local + postgres` must return a non-zero exit code, explain the backend requirement, and leave no partial target. A skipped database suite is not evidence for this matrix. Application startup never runs migrations, and the template intentionally contains no product business schema.

## Documentation and version result

The README, governance policy, tooling, CI, release, architecture, project-profile, and acceptance documents are synchronized with the real CLI and version 1.0.0. The English and German case-study sources preserve historical commit context while their release addenda describe the current governed process consistently. All four PDFs must match their provenance and checksums.

The following canonical project-version values equal `1.0.0`:

- `VERSION`;
- the frontend root package and lockfile package;
- Tauri configuration;
- the Rust root package and lockfile package; and
- the FastAPI application version exposed at runtime.

Dependency, schema, ABI, and document-format versions are not project-version mirrors.

## GitHub Actions result

Remote acceptance is commit-bound. For the candidate commit identified by the final operator report—and, after publication, the commit peeled from `v1.0.0`—the following checks must all have `status=completed` and `conclusion=success`:

- all six Core CI jobs, including Code Quality & Architecture and Documentation Check;
- all five Profile Matrix jobs;
- PostgreSQL master integration and all three generated PostgreSQL jobs;
- all three unsigned Desktop CI jobs on Linux, macOS, and Windows; and
- Release Validation, including its reusable desktop candidates.

The exact run IDs, URLs, events, and full common SHA belong in external run evidence and the final operator report rather than this self-participating file. A successful run on an older SHA or a skipped required job does not validate the candidate. After publication, a failed tag-triggered job makes the release result `NOT RELEASED`.

## Historical workflow-run disposition

The public snapshot recorded on 2026-08-23 contained 41 runs: 39 failures and two successes. Every failure was inspected and classified before cleanup. Thirty-seven runs exposed historical project or workflow defects and were retained as category A evidence. Core run `31127208973` was retained as category B infrastructure evidence because its runner failed internally and that snapshot contained no later complete Core success. PostgreSQL run `31127208974` was classified as the sole category C cleanup candidate because run `31128760336` was its later successful replacement. No category D run was identified.

This dated inventory is retained as historical disposition, not as current candidate evidence. No run is deleted during candidate preparation: API-authenticated cleanup is unavailable, Release Validation is incomplete, and cleanup is unnecessary for validation. A future deletion of run `31127208974` remains optional and may occur only after all final same-SHA workflows are green and its commit, cause, replacement, and deletion result are recorded externally. All other failed runs, both historical successes, final-candidate runs, tag runs, release evidence, and required artifacts are retained. Logs and Git history are never edited or rewritten.

## Known limitations

- The template produces unsigned verification packages. Signing, notarization, publication, and updater activation remain product-specific.
- Playwright remains an explicit optional skip until a generated product supplies concrete end-to-end requirements and tests.
- Local Docker image assembly is not claimed where the operator lacks daemon permission; same-SHA GitHub container jobs are mandatory release evidence.
- The template supplies infrastructure boundaries but intentionally no authentication, authorization, business model, provider deployment, or production data migration.

These limitations do not weaken a required quality, test, profile, database, desktop, documentation, or same-SHA release gate.

## Validation and publication decisions

The version 1.0.0 candidate is technically validated only if all of the following are simultaneously true:

1. the historical architecture baseline is an ancestor of the candidate commit;
2. all canonical versions equal `1.0.0`;
3. all locally applicable Quality, test, build, profile, and documentation checks pass, with locally unavailable PostgreSQL, native, and container paths supplied by the corresponding exact-HEAD required workflows;
4. the working tree is clean and `release check` passes;
5. every required GitHub workflow succeeds on exactly the candidate commit; and
6. workflow-run retention decisions are recorded without deleting or hiding current evidence.

When these conditions hold, the technical decision is **PASS — VALIDATED RELEASE CANDIDATE**. This is sufficient for a commit-pinned migration baseline but is not publication.

Version 1.0.0 is published only if the additional publication conditions also hold: `v1.0.0` is an annotated, non-forced tag whose peeled commit equals the validated common SHA; the pushed tag and every tag-triggered workflow pass; and any GitHub Release or external release manifest identifies the same tag and commit. Until then, the publication decision remains **NOT PUBLISHED**.

Current technical decision: **BLOCKED**. The candidate is synchronized to `origin/main`; local applicable gates, clean-tree `release check`, and the automatic exact-HEAD Core, Profile, PostgreSQL, and Desktop workflows passed. This environment has neither `gh` nor a GitHub API token, and unauthenticated Release Validation dispatch returned HTTP 401. Release Validation therefore has no run or successful conclusion on the candidate. Current publication decision: **NOT PUBLISHED**.

## Related documents

- [Framework architecture](../def/architecture.md)
- [Code quality and architecture governance](../def/code-quality.md)
- [Project profiles](../def/project-profiles.md)
- [Continuous Integration](../tools/ci.md)
- [Release and desktop packaging model](../tools/release-model.md)
- [Template-Projekte v1.0.0 release notes](../tools/release-notes-v1.0.0.md)

## Change log

| Date | Change | Author |
| --- | --- | --- |
| 2026-08-23 | Replaced the historical case-study acceptance with the commit-bound v1.0.0 release protocol. | Project team |
