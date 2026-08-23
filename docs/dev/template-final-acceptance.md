<!-- AUTO-GENERATED:backlink START -->
[← Back](dev.md)
<!-- AUTO-GENERATED:backlink END -->
# Template v1.0.0 final acceptance

| Field | Value |
| --- | --- |
| Status | Active release protocol |
| Owner | Project team |
| Last review | 2026-08-23 |
| Audience | Maintainers, reviewers, and release operators |
| Version | `1.0.0` |
| Release tag | `v1.0.0` |
| Baseline commit | `461fc7519e0db638330904a7496c488e8a0d18bc` |
| Related ATP | N/A — repository-wide release acceptance |

## Purpose and authoritative identity

This protocol defines the technical and documentary acceptance of the reusable web, cloud, and desktop template as version 1.0.0. The baseline above is the comparison point, not the automatic release target. The authoritative release commit is the commit peeled from the annotated tag:

```sh
git rev-parse 'v1.0.0^{}'
```

The exact final SHA is deliberately not embedded in a file that participates in that commit. It is recorded in the annotated tag, the GitHub Release, the operator's release manifest under `.report/release-v1.0.0/`, and the final release report.

The result is `PASS` only when every condition in [Final decision](#final-decision) is true for that one peeled commit. If the tag is absent, is lightweight, points elsewhere, or lacks complete same-SHA evidence, the result is `NOT RELEASED`; no earlier green run may substitute for it.

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

## Verified environments

| Area | Release environment |
| --- | --- |
| Browser and tooling | Node.js 24.19.0; npm 11; dedicated `tools/.venv` with Wasmtime 47.0.1 |
| Python application matrix | CPython 3.11.16 with isolated backend and tooling environments |
| Rust and Tauri | Rust 1.97.1; `wasm32-wasip1`; Tauri CLI 2.11.4; WebKitGTK 4.1 on Linux |
| Database | PostgreSQL 16.15 on a disposable non-default local port |
| Deployment model | Docker Compose 5.4.0 model validation |
| Remote native matrix | GitHub-hosted Ubuntu, macOS, and Windows runners on the release commit |

Local Docker image assembly depends on access to the Docker daemon. When the operator account cannot access the daemon, provider-neutral image assembly must be proven by successful Core and Release Validation jobs on the release commit and the local limitation remains explicit.

## Code quality and architecture result

The public gate is:

```sh
python tools/control.py quality
```

The accepted result is `PASS` with zero errors and zero suppressed findings. Warnings and strong warnings remain visible and non-blocking; they are not promoted, hidden, or cleared with exceptions. No manual exception is present in the release baseline.

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

The final candidate is accepted locally only after these public paths succeed on the same working tree:

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

The analyzer crate additionally passes locked format, Clippy, check, test, relocated and vendored reproducible WASI-build, private-path exclusion, real-host, malformed-syntax, ABI, digest-drift, large-input, and resource-limit tests. The external PyGitIndex regeneration is run after documentation changes; the independent `docs check` must then report no semantic drift. After the release commit is created and the tree is clean, `python tools/control.py release check` must also pass.

Feature-disabled suites may report `SKIP`. An enabled missing dependency, unavailable configured database, syntax failure, quality error, or failed build remains a failure.

## Profile matrix

Every row is generated into a fresh target and runs install, Doctor, configuration Doctor, Quality, the profile-aware full test suite, and the production web build. Desktop rows additionally run Tauri Doctor and the desktop dry-run; cloud rows validate their Compose model.

| Profile | Generate | Doctor and config | Quality | Tests | Web build | Desktop checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `web-only` | PASS | PASS | PASS | PASS | PASS | N/A |
| `web-cloud` | PASS | PASS | PASS | PASS | PASS | N/A |
| `desktop-local` | PASS | PASS | PASS | PASS | PASS | PASS |
| `desktop-cloud` | PASS | PASS | PASS | PASS | PASS | PASS |
| `full-platform` | PASS | PASS | PASS | PASS | PASS | PASS |

The generator must leave the master unchanged, copy the governance policy and agent instructions, preserve the dedicated tooling runtime, omit disabled technologies, and reject non-empty or unsafe targets.

## PostgreSQL matrix

Each valid row uses a real PostgreSQL 16.15 connection, configuration validation, `SELECT 1`, Alembic upgrade/current checks, API and database tests, the complete profile suite, Quality, web build, and container-model validation. Desktop rows also run Tauri checks.

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

Remote acceptance is commit-bound. For the commit peeled from `v1.0.0`, the following checks must all have `status=completed` and `conclusion=success`:

- all six Core CI jobs, including Code Quality & Architecture and Documentation Check;
- all five Profile Matrix jobs;
- PostgreSQL master integration and all three generated PostgreSQL jobs;
- all three unsigned Desktop CI jobs on Linux, macOS, and Windows; and
- Release Validation, including its reusable desktop candidates.

The exact run IDs, URLs, events, and full common SHA belong in the release manifest and GitHub Release rather than this self-participating file. A successful run on an older SHA, a skipped required job, or a failed tag-triggered job makes the release result `NOT RELEASED`.

## Historical workflow-run disposition

The pre-release public snapshot contains 41 runs: 39 failures and two successes. Every failure was inspected and classified before cleanup. Thirty-seven runs expose historical project or workflow defects and are retained as category A evidence. Core run `31127208973` is retained as category B infrastructure evidence because its runner failed internally and the snapshot contained no later complete Core success. PostgreSQL run `31127208974` is the sole category C cleanup candidate because run `31128760336` is its later successful replacement. No category D run was identified.

Run `31127208974` may be deleted only after all final same-SHA workflows above are green. Its commit, cause, replacement, and deletion result must be recorded in the release manifest. All other failed runs, both historical successes, final-candidate runs, tag runs, release evidence, and required artifacts are retained. Logs and Git history are never edited or rewritten.

## Known limitations

- The template produces unsigned verification packages. Signing, notarization, publication, and updater activation remain product-specific.
- Playwright remains an explicit optional skip until a generated product supplies concrete end-to-end requirements and tests.
- Local Docker image assembly is not claimed where the operator lacks daemon permission; same-SHA GitHub container jobs are mandatory release evidence.
- The template supplies infrastructure boundaries but intentionally no authentication, authorization, business model, provider deployment, or production data migration.

These limitations do not weaken a required quality, test, profile, database, desktop, documentation, or same-SHA release gate.

## Final decision

Version 1.0.0 is released only if all of the following are simultaneously true:

1. the baseline commit is an ancestor of the release commit;
2. all canonical versions equal `1.0.0`;
3. the final local Quality, test, build, profile, PostgreSQL, Tauri, and documentation checks pass;
4. the working tree is clean and `release check` passes;
5. every required GitHub workflow succeeds on exactly the release commit;
6. the sole category C cleanup decision is recorded and no current failure is hidden;
7. `v1.0.0` is an annotated, non-forced tag whose peeled commit equals that common SHA;
8. the pushed tag and any tag-triggered workflow pass; and
9. the GitHub Release and release manifest identify the same tag and commit.

When these conditions hold, the decision is **PASS — TEMPLATE-PROJEKTE v1.0.0 RELEASED**. Otherwise it is **NOT RELEASED**, and the missing condition remains explicit.

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
