<!-- AUTO-GENERATED:backlink START -->
[← Back](tools.md)
<!-- AUTO-GENERATED:backlink END -->
# Continuous Integration

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Contributors and repository maintainers |
| Related ATP | [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md) |

## Purpose

This document defines the automated quality and security gates for the master template and the evidence required for a release candidate. Continuous integration detects regressions in governance, shared tooling, feature modules, profile generation, PostgreSQL integration, container builds, production web builds, native desktop packaging, dependencies, static analysis, and release validation before a change is accepted.

## Scope

Core, profile, PostgreSQL, desktop, and security workflows run for pull requests, pushes to `main`, or their documented subset of those events. They validate the repository and temporary generated projects. Security analysis also runs weekly. The separate release-validation workflow runs for a matching version tag or manual dispatch and can call the desktop workflow. A completed successful tag validation may trigger exact-SHA publication of the unsigned template evidence bundle. Deployment, signing, package-registry publication, application stores, and production database operations remain outside the automated baseline.

## Local and CI equivalence

GitHub Actions orchestrates the same public interface used by developers:

```text
GitHub Actions
      |
      v
python tools/control.py
      |
      +-- install
      +-- doctor / config doctor / tauri doctor
      +-- quality
      +-- test --suite <name>
      +-- db upgrade
      +-- template status / template verify
      +-- build web
      +-- container validate / build container
      +-- version check / release check
      +-- docs check
```

Project behavior remains in `tools/control.py` and its modules. Workflow YAML is responsible only for runtime setup, dependency caches, temporary service containers, command ordering, and job boundaries.

The local baseline is:

```sh
python tools/control.py install
python tools/control.py doctor
python tools/control.py config doctor
python tools/control.py quality
python tools/control.py test --suite all
python tools/control.py build web
python tools/control.py version check
python tools/control.py docs check
```

`test --suite all` reads `project-profile.toml`. Disabled features report `SKIP` and return success. Missing files or failed checks for enabled features report `FAIL` and return a non-zero exit code.

Tests that exercise generator capabilities outside a derived project's enabled feature set are skipped. The same tooling suite still runs in every generated project; only master-only source-completeness checks are excluded when the corresponding source modules were intentionally not scaffolded.

## Test levels

| Level | Coverage | Public command |
| --- | --- | --- |
| Governance | Repository metrics, architecture boundaries, lint, formatting, type/compiler checks, and exception policy | `python tools/control.py quality` |
| Core tests | Tooling, lifecycle, profiles, configuration, schema, FastAPI, SQLAlchemy, frontend, Tauri, and Rust | `python tools/control.py test --suite <name>` |
| Browser behavior | Playwright Chromium smoke coverage, the real frontend/backend HTTP boundary, and axe accessibility analysis | `python tools/control.py test --suite e2e` |
| External service tests | PostgreSQL connectivity and Alembic migration | `python tools/control.py test --suite postgres`, `python tools/control.py db upgrade` |
| Generated project tests | Real scaffolds for every supported profile | `python tools/control.py init`, followed by generated-project commands |
| Build verification | Vite, provider-neutral images, and native Tauri packages | `python tools/control.py build web`, `build container`, `build desktop` |
| Documentation consistency | Generated-index coverage, backlink structure, link targets, and navigation markers | `python tools/control.py docs check`; regenerate intentionally with `docs index` |

The frontend baseline has a committed Playwright configuration and smoke tests. CI installs Chromium with its Linux system dependencies, starts the profile's enabled services through the public test runner, and treats E2E or accessibility failures as blocking. Vitest enforces 100% statement, branch, function, and line coverage per governed frontend source file. Every production web build also enforces the committed raw-byte bundle budget.

## Workflows

The active workflow inventory is:

| Workflow | File | Pull request | Push to `main` | Manual | Weekly | Version tag | Reusable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Core CI | `.github/workflows/ci.yml` | Yes | Yes | Yes | No | No | No |
| Profile Matrix | `.github/workflows/profiles.yml` | Yes | Yes | Yes | No | No | No |
| PostgreSQL Integration | `.github/workflows/postgres.yml` | Yes | Yes | Yes | No | No | No |
| Desktop CI | `.github/workflows/desktop.yml` | Yes | Yes | Yes | No | No | Yes |
| Security | `.github/workflows/security.yml` | Yes | Yes | Yes | Yes | No | No |
| Release Validation | `.github/workflows/release.yml` | No | No | Yes | No | `v*.*.*` | No |
| Release Publication | `.github/workflows/release-publish.yml` | No | No | No | No | Completed tag validation | No |

### Core CI

`.github/workflows/ci.yml` separates failures into six jobs. The five verification jobs depend on the governance job:

| Check name | Responsibility |
| --- | --- |
| `Core / Code Quality & Architecture` | Central policy, source metrics, architecture rules, the reproducible Syn/WASI analyzer, Ruff, ESLint, Prettier, TypeScript, rustfmt, Clippy, and Cargo checks |
| `Core / Tooling, Profiles & Configuration` | CLI, generator, profile, configuration, and workflow regression tests |
| `Core / Documentation Check` | Read-only semantic navigation check plus focused documentation-tooling regressions |
| `Core / Backend, Database & Schema` | JSON Schema, FastAPI, and SQLAlchemy unit tests |
| `Core / Frontend, Browser & Web Build` | Vitest with enforced coverage, Playwright/axe browser tests over the real HTTP boundary, and a production Vite build with bundle budgets |
| `Core / Container Build` | Version and Compose validation plus backend and frontend image builds |

The five downstream jobs are independent and run in parallel after Quality succeeds. Native packages belong to Desktop CI. A warning or strong warning from a repository rule remains non-blocking, but an unsuppressed error or failed required tool makes Quality fail. In particular, `CQ001 ERROR` for a handwritten source file above 900 code lines cannot be suppressed by an exception.

### Profile Matrix

`.github/workflows/profiles.yml` generates `web-only`, `web-cloud`, `desktop-local`, `desktop-cloud`, and `full-platform` projects. Immediately after generation, each matrix entry runs `template status` and `template verify` from the generated root. A clean checkout must report generated, reproducible provenance and a valid deterministic baseline before dependency caches or product checks are trusted. Each entry then runs an initial structure doctor, dependency installation, Chromium setup, a prepared-environment doctor, the profile-aware complete suite including browser and accessibility checks, and a production web build with bundle-budget enforcement. Desktop entries also install Linux Tauri prerequisites, run Tauri doctor, and execute Cargo checks. Cloud entries validate their generated Compose model.

Every entry runs `python tools/control.py quality` after installation and before its final Doctor, tests, and build:

| Profile | Lifecycle | Quality | Tests | Web build | Container validation | Tauri checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `web-only` | Required | Required | Required | Required | N/A | N/A |
| `web-cloud` | Required | Required | Required | Required | Required | N/A |
| `desktop-local` | Required | Required | Required | Required | N/A | Required |
| `desktop-cloud` | Required | Required | Required | Required | Required | Required |
| `full-platform` | Required | Required | Required | Required | Required | Required |

On Debian-family Linux runners, `tauri install` refreshes apt metadata before a non-interactive install. It uses the Tauri v2 WebKitGTK 4.1 dependency set and selects the release-appropriate FUSE 2 package name (`libfuse2` on Ubuntu 22.04 and `libfuse2t64` on Ubuntu 24.04 and newer). Missing required compile-time libraries make `tauri doctor` fail; AppImage-only helpers remain warnings during check-only CI.

The matrix uses `fail-fast: false`. One broken preset therefore does not hide the status of the other presets.

### PostgreSQL Integration

`.github/workflows/postgres.yml` starts PostgreSQL 16 as an isolated service container with test-only credentials and a `pg_isready` health check. No external database is contacted.

The integration job performs this sequence:

```text
fresh temporary database
        |
        v
config doctor
        |
        v
Alembic upgrade head
        |
        v
PostgreSQL integration test
```

The same workflow generates `web-cloud`, `desktop-cloud`, and `full-platform` with `--with postgres`. Each generated project first runs lifecycle status and verification so CI proves that the optional `postgres` selection and its fully resolved `database` dependency are recorded. It then runs doctor, migration, Chromium-backed browser and accessibility checks as part of the complete profile-aware suite, the budgeted web build, and container-model validation. Desktop entries also run Tauri checks. `DATABASE_URL` and `DATABASE_URL_TEST` point only to the job-local service.

The PostgreSQL acceptance matrix is:

| Generated variant | Lifecycle | Real service connection | Migration | Quality | API/profile tests | Web build | Desktop checks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `web-cloud + postgres` | Required | Required | Required | Required | Required | Required | N/A |
| `desktop-cloud + postgres` | Required | Required | Required | Required | Required | Required | Required |
| `full-platform + postgres` | Required | Required | Required | Required | Required | Required | Required |

`web-only + postgres` and `desktop-local + postgres` are invalid combinations and must fail before a partial target is written. A skipped PostgreSQL suite without a real `DATABASE_URL_TEST` is not release evidence for this matrix.

Application startup never runs migrations. CI invokes `db upgrade` explicitly.

### Desktop CI

`.github/workflows/desktop.yml` uses a native matrix over Ubuntu, macOS, and Windows. Every runner installs the dedicated tooling environment, executes Doctor's real Wasmtime analyzer probe against the checked-in WASI artifact, and verifies the analyzer's explicit UTF-8 subprocess transport under a non-UTF-8 text-stdio setting. Desktop jobs do not rebuild that artifact. They then run the locked Tauri checks and build technically available native packages through `python tools/control.py build desktop`. Before `upload-artifact` sees any output tree, Linux and macOS create and validate a runner-local `tar.gz`, while Windows creates and validates a runner-local ZIP. Only that single prearchive is uploaded under the short-lived artifact name `desktop-<target>-unsigned`; the action never receives a raw bundle tree. The POSIX TAR therefore retains executable bits and case-sensitive paths even though the surrounding Actions artifact transport normalizes file modes. Normal Linux runs default to an unsigned DEB; the reusable and manually dispatched workflow accepts an explicit validated Linux bundle list. No job reads signing or notarization secrets.

| Runner | Target | Required evidence |
| --- | --- | --- |
| `ubuntu-latest` | Linux | Tauri Doctor, locked Rust checks/tests, unsigned DEB by default, mode-preserving TAR prearchive |
| `macos-latest` | macOS | Tauri Doctor, locked Rust checks/tests, native unsigned bundles, mode-preserving TAR prearchive |
| `windows-latest` | Windows | Tauri Doctor, locked Rust checks/tests, native unsigned bundles, validated ZIP prearchive |

The artifacts establish build compatibility and are not production releases. Ordinary Desktop CI artifacts remain only in the workflow artifact store. After exact-SHA tag validation, the separate template publisher may repackage the three platform artifact sets as explicitly unsigned GitHub Release evidence.

### Release Validation

`.github/workflows/release.yml` accepts `workflow_dispatch` and tags matching `v*.*.*`. It rebuilds and verifies the pinned WASI analyzer, runs `quality --release` and the full validation suite including Chromium smoke and axe accessibility checks, builds the budgeted web candidate, executes `release check`, and calls the same unsigned desktop workflow with `linux_bundles: deb,rpm,appimage`. The Linux job removes prior generated bundle outputs, requires a fresh nonempty DEB, RPM, and AppImage, and writes `.dist/desktop/linux/linux-bundles.json` plus `.dist/desktop/linux/SHA256SUMS`. Its validated `desktop-linux-unsigned.tar.gz` prearchive contains all three packages and both evidence files; that single file is the content of the aggregate `desktop-linux-unsigned` workflow artifact. The job summary lists package sizes and SHA-256 digests.

The validation job generates an SPDX JSON dependency SBOM, retains it with the web ZIP, and records both build-provenance and SBOM attestations through GitHub's OIDC-backed attestation service. Only that job receives `id-token: write` and `attestations: write`; contents remain read-only. The workflow does not upload directly to a GitHub Release.

These Linux packages are unsigned x86_64 verification candidates. They inherit the Ubuntu runner and glibc baseline and therefore do not prove runtime compatibility with every Linux distribution. ARM packages, Flatpak, and Snap are not part of this workflow. Product repositories may replace the unsigned template publisher with protected signing and product publication only after this gate.

### Release Publication

`.github/workflows/release-publish.yml` is the only automated publication path. It is triggered by a completed Release Validation workflow and continues only when that run was a successful tag push. Publication additionally requires `github.workflow_sha` to equal `workflow_run.head_sha`; maintainers therefore freeze `main` between the release commit, tag validation, and publication. A changed default branch fails instead of silently running a different publisher control plane. The publisher requires an annotated strict `v<major>.<minor>.<patch>` tag whose version matches `VERSION`, and proves locally and through the remote Git reference and annotated-tag objects that it resolves to that exact commit. Direct pushes, pull requests, manual dispatches, prerelease-looking tags, lightweight tags, version mismatches, moved tags, and failed validation runs cannot enter publication.

The read-only preparation job checks out publisher code from the candidate-bound `github.workflow_sha` and checks out the validated commit separately as a data source. It queries GitHub Actions with `actions: read`, accepting only completed successful `main` push runs from the exact governed workflow paths for Core CI, Desktop CI, PostgreSQL Integration, Profile Matrix, and Security on the same SHA. It separately validates the exact triggering Release Validation run ID, attempt number, path, tag, SHA, event, status, and conclusion. A same-named workflow at another path is not evidence. Missing, queued, cancelled, skipped, stale-SHA, manually dispatched, or failed runs stop publication.

Preparation downloads artifacts only from that completed Release Validation run. It validates the SPDX document, rejects symlinks and non-portable archive members, creates a tracked-source archive from the immutable commit, retains each validated native desktop prearchive byte-for-byte without extracting or ZIP-wrapping it, normalizes the byte-identical tested web candidate, retains the SPDX JSON SBOM, writes a machine-readable workflow evidence manifest, and calculates aggregate SHA-256 checksums. The Linux and macOS `tar.gz` files and the Windows ZIP therefore become the corresponding final desktop release assets directly. Keeping the POSIX prearchives opaque preserves their recorded executable modes through publication. Reviewed English notes under `.github/release-notes/v<version>.md` are extended at runtime with the full commit SHA and exact run-attempt links. The resulting same-run artifact is reverified by checksum and fixed filename inventory before the privileged job receives it.

Native Immutable Releases must be enabled in repository settings. An active tag ruleset must include `refs/tags/v*`, have no exclusions or bypass actors, and restrict both updates and deletion; this closes the draft-promotion interval before native release immutability protects the tag. `RELEASE_GOVERNANCE_TOKEN` is used only for REST `GET` requests and must let GitHub return both repository immutability state and ruleset bypass actors. GitHub returns bypass actors only to a caller with write access to that ruleset, so scope the credential to this repository, protect it as a release secret, and do not use it for publication.

The scoped `GITHUB_TOKEN` creates a draft only when no release exists, uploads the complete fixed asset set, verifies remote sizes and digests, rechecks the protected remote annotated tag, and only then publishes the draft. Bounded retries cover GitHub metadata propagation. Publication succeeds only when the release reports native immutability, the remote tag still resolves to the expected SHA, and `gh release verify` validates GitHub's release attestation for the tag, commit, and all assets. If immutability is unexpectedly absent, the workflow restores only its newly created release to draft and fails. A rerun never edits or replaces an existing release: it succeeds through a read-only resume path only when the existing release is already native immutable and its tag, notes, exact asset inventory, sizes, and SHA-256 digests all match.

The validation/publication split is intentional. A job inside Release Validation cannot prove that its own workflow has already completed. The `workflow_run` boundary lets publication include the completed Release Validation run itself in the exact-SHA evidence.

### Security

`.github/workflows/security.yml` runs CodeQL with `security-extended` queries for Python, JavaScript/TypeScript, and Rust. It analyzes pull requests, pushes to `main`, weekly scheduled runs, and manual dispatches. A separate pull-request-only Dependency Review job rejects newly introduced dependencies with high or critical known vulnerabilities across runtime, development, and unknown scopes.

Every external Action is pinned to a full 40-character commit SHA and carries its human-readable immutable release version as a comment. `.github/dependabot.yml` checks GitHub Actions, npm, both Python requirement roots, both Cargo roots, Dockerfiles, and Compose inputs every week. Minor and patch version updates are grouped into one routine-maintenance pull request per ecosystem. Major updates remain individual and therefore require a separate review of migration notes, compatibility impact, and full CI evidence. Ecosystems that support SemVer-specific cooldowns apply an additional 30-day buffer to those major updates; GitHub Actions, Docker, and Docker Compose keep the same individual-review policy without claiming an unsupported SemVer cooldown. At most three version-update pull requests may be open per ecosystem; this cap and supported cooldowns do not suppress Dependabot security updates. `.github/CODEOWNERS` routes workflow, policy, deployment, native, and tooling changes to the repository owner.

Repository settings are not encoded by workflow YAML. Maintainers must enable the Dependency Graph, Dependabot alerts and security updates, Code Scanning, Private Vulnerability Reporting, Secret Scanning with Push Protection, and a branch ruleset that requires the applicable Core, Profile, PostgreSQL, Desktop, and Security checks. The branch ruleset should require CODEOWNERS review for protected paths and disallow force pushes. Separately, release publication requires an active tag ruleset for `refs/tags/v*` with no exclusions or bypass actors and with both update and deletion restrictions. Record those settings in release evidence instead of claiming them from committed files alone.

### Portable Rust syntax analyzer

The checked-in `tools/quality/rust_analyzer/dist/rust_quality_analyzer.wasm` is built from the adjacent Syn 2.0.119 crate with Rust 1.97.1 for `wasm32-wasip1`. The release artifact is 535,787 bytes with SHA-256 `7a27cb02a9392b62c487b4ce73a03524d7260b804c0c49eb4520ceb1a1cacfd8`. `provenance.json` binds that digest to the exact `rustc 1.97.1 (8bab26f4f 2026-07-14)` build, target, dependency versions and lock digest, and a sorted source digest over `build.py`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, and `src/**/*.rs`.

The versioned path-remapping contract canonicalizes the source root, user home, Cargo home, Cargo target directory, Rust sysroot, and each dependency root. The build script removes inherited compiler wrappers, flags, target overrides, and release-profile overrides before installing its own deterministic settings. Remaps are passed through `CARGO_ENCODED_RUSTFLAGS` from broad roots to specific roots because the last matching `rustc` remap wins. It also rejects an artifact that still contains a private physical build path.

Three builds on the pinned Rust 1.97.1 Linux builder were byte-identical: the normal registry layout, relocated Cargo/source/target homes containing spaces, and an in-tree vendored dependency layout. This evidence is deliberately limited to those Linux builds; it does not claim byte identity across operating systems. Core CI and Release Validation rebuild and compare the artifact on Ubuntu, while the macOS and Windows Desktop jobs execute and validate only the checked-in artifact.

The Python host verifies the provenance values and the exact Wasmtime 47.0.1 distribution before every execution. It runs the module without inherited environment variables or preopened directories and with explicit memory, instance, table, and fuel limits. The parent/child ABI transports bytes and decodes stdin, stdout, and stderr as strict UTF-8, avoiding both locale-dependent encoding and Windows text-mode newline translation.

The root `.gitattributes` fixes all analyzer text inputs to LF and marks the WASM binary. It is part of every generated profile, so Windows `core.autocrlf` checkouts preserve the same byte-level source digest instead of producing a false provenance failure.

Core CI compiles, formats, lints, checks, and tests the analyzer crate, then runs:

```sh
python tools/quality/rust_analyzer/build.py --check
tools/.venv/bin/python -m pytest -q \
  tools/tests/quality/test_rust_syntax.py \
  tools/tests/quality/test_rust_payload.py \
  tools/tests/quality/test_rust_wasi_host.py
```

`build.py --check` rebuilds the module and fails if its bytes or provenance differ from the committed release artifact. The Desktop matrix independently executes the committed module through Doctor and the Unicode transport regression on Linux, macOS, and Windows without rebuilding it. Web-only users therefore need Python and the installed tooling environment, but no native Rust toolchain, to run the Rust source-policy scanner.

### Documentation Check

`Core / Documentation Check` is an active job in `.github/workflows/ci.yml` and depends on the quality gate. It runs `python tools/control.py docs check`, the focused documentation-maintenance tests, and `git diff --exit-code`. Release Validation repeats the semantic check and its focused tests for the release candidate.

`docs check` is a self-contained, read-only semantic validator. It does not require or invoke the external PyGitIndex script. It requires exactly one generated backlink block on every documentation page, validates the expected backlink destination, rejects missing, duplicate, stale, or repository-escaping generated targets, and compares every overview and root index with the Markdown pages it must cover. Any drift returns a non-zero exit code.

PyGitIndex remains the regeneration tool. After adding, moving, renaming, or removing Markdown pages, the authoring sequence is:

```sh
# Optional preview
python tools/control.py docs index --dry-run

# Intentional regeneration, followed by review
python tools/control.py docs index
git diff -- README.md docs

# Reproducible release gate
python tools/control.py docs check
```

The dry-run returning zero proves only that the preview command worked; it does not prove that no changes were proposed. CI deliberately runs the semantic checker rather than silently regenerating tracked files. Authored release, CI, architecture, quality, profile, and acceptance documents still require human review.

## Runtime versions

| Runtime | CI baseline |
| --- | --- |
| Python | 3.11 |
| Node.js | 24 LTS |
| Rust | 1.97.1, including `wasm32-wasip1` where the analyzer is rebuilt |
| PostgreSQL | 16.15 service container for integration tests |
| Wasmtime | 47.0.1 in the dedicated tooling environment |

These values pin the release-validation environment. Generated products may raise their own minimums, but the template's required workflows use the same exact Rust release so analyzer reproduction and native checks cannot drift with the moving stable channel.

The project baseline is kept on a supported LTS line. Official actions may use their own bundled Node.js runtime independently of the project-level Node.js 24 baseline.

## Dependency installation and caching

`control.py install` uses `npm ci` whenever `frontend/package-lock.json` exists and falls back to `npm install` only for projects without a lockfile. Cargo commands use `--locked` with `src-tauri/Cargo.lock`. Python keeps the existing requirements-file and virtual-environment strategy.

GitHub-hosted caches cover:

- pip downloads keyed by the relevant requirements files;
- npm downloads keyed by `frontend/package-lock.json`;
- Cargo registry, Git sources, and target output keyed by `src-tauri/Cargo.lock`.

Caches improve execution time but are never required for correctness.

The profile workflow intentionally generates the project before configuring the generated Cargo target cache. Lifecycle status and verification remain between those steps. Workflow regression tests protect that order together with the generated cache path.

## Permissions and secrets

Every workflow defaults to `contents: read`. CodeQL alone receives `security-events: write`. Release Validation receives `attestations: write` plus `id-token: write` only while generating candidate attestations. Release Publication separates read-only preparation from the final job, which alone receives `contents: write` and `attestations: read`; neither publication job receives OIDC or attestation write permission. The final job uses `RELEASE_GOVERNANCE_TOKEN` only for read-only proof of native Immutable Releases and non-bypassable `v*` tag protection, then uses the scoped `GITHUB_TOKEN` for draft creation, publication, and release-attestation verification. Pull requests from forks do not require repository secrets. PostgreSQL uses the temporary user, password, and database declared in workflow YAML; those values exist only inside an isolated CI run and are not production credentials.

The workflows do not use third-party cloud credentials, signing material, deployment tokens, or package-registry publication. Public GitHub Release creation is isolated to the completed-tag publisher. Although the governance-token actor must be able to expose ruleset bypass data, publisher code performs no mutating request with that token. Commands must not print database URLs or other secret values. Normal CI jobs run `git diff --exit-code` to detect unintended changes to versioned files.

## Failure handling

Jobs use explicit timeouts. Pull-request concurrency cancels an older run after a newer commit arrives, while `main` runs are not cancelled. Independent jobs remain parallel so GitHub reports the failing subsystem directly.

`PASS`, `SKIP`, and `FAIL` have distinct meanings:

- `PASS`: the selected check ran and completed successfully.
- `SKIP`: the active profile disables the feature or an optional suite is not configured.
- `FAIL`: an enabled feature is incomplete, configuration is invalid, or the executed check failed.

A configured but unreachable `DATABASE_URL_TEST` is a failure, not a skip.

Classify every non-successful release-relevant run before taking action:

| Category | Meaning | Action |
| --- | --- | --- |
| A | Current project, test, quality, build, or workflow defect | Fix it, add regression coverage, commit, and rerun all affected gates on the new SHA |
| B | Credible temporary GitHub runner, registry, or network incident | Rerun the failed jobs once and investigate recurrence instead of repeatedly calling it temporary |
| C | Historical failure on a superseded commit with a successful replacement | Retain until final CI is green, then record and optionally delete that one run |
| D | Historical run from an obsolete or replaced workflow | Identify its replacement, retain until final CI is green, then record and optionally delete that one run |
| E | Release, tag, artifact, or acceptance evidence | Retain; never delete |

Never delete an unexplained current failure, a run on the final release commit, a tag run, a successful release proof, or a run whose artifacts are still needed. Historical cleanup is by explicit run ID, never a blind bulk deletion. Record run ID, workflow, SHA, date, conclusion, cause, replacement run, and reason before deletion. Deleting a red historical run does not fix its cause and must not be used to rewrite the apparent project history.

## Same-commit release evidence

A release is commit-bound. All six Core CI jobs, Profile Matrix, PostgreSQL Integration, Desktop CI, the three CodeQL language jobs, and Release Validation must complete successfully for the same final candidate SHA. When the candidate entered `main` through a pull request, its Dependency Review job must also have passed before merge. A green run on an earlier commit is not evidence for a later tag. Automated publication additionally requires each workflow name to originate from its exact governed workflow path.

After pushing the candidate, list runs by the full SHA and rerun a failed or cancelled `main` push run when one exists. A manually dispatched run is useful diagnostics but is not governed publication evidence. If a required push run is absent, create and push a new candidate commit so the complete workflow set runs again. Confirm for every required run that `headSha` equals the candidate, `status` is `completed`, and `conclusion` is `success`. If any fix creates a new commit, discard the old candidate as release evidence and repeat the complete required set for the new SHA. Once tagging begins, freeze `main` until Release Publication completes; a newer default-branch commit deliberately invalidates the publisher-control equality check. Exact run IDs, attempts, and the final commit SHA are generated into publication notes and the evidence manifest after the commit and its runs exist; they cannot be embedded in the commit whose object ID they would change.

## Branch protection recommendation

Configure `main` branch protection after the workflows have completed stable repository runs. Require the actual checks shown by GitHub for:

- `Core / Code Quality & Architecture` and all five downstream `Core / ...` jobs, including `Core / Documentation Check`;
- all five `Profiles / ...` matrix jobs;
- `PostgreSQL / Integration & Migration`;
- all three `Profiles / ... + postgres` jobs; and
- all three `Desktop / ... / Unsigned Verification` jobs;
- `Security / Dependency Review`; and
- `Security / CodeQL / javascript-typescript`, `Security / CodeQL / python`, and `Security / CodeQL / rust`.

Require pull requests and current branch status before merge. Do not grant test workflows deployment or bypass privileges.

## Acceptance evidence

Automated tests and CI output provide repeatable technical evidence. They do not replace feature acceptance:

```text
Automated tests + CI evidence + acceptance testing = feature acceptance
```

Reference relevant CI runs from an ATP when they support an acceptance decision.

## Verification

Run the local equivalents from the repository root:

```sh
python tools/control.py test --suite tools
python tools/control.py quality
python tools/control.py test --suite schema
python tools/control.py test --suite api
python tools/control.py test --suite database
python tools/control.py test --suite frontend
python tools/control.py test --suite tauri
python tools/control.py build web
python tools/control.py container validate
python tools/control.py version check
python tools/control.py docs check
```

PostgreSQL verification additionally requires a disposable test database through `DATABASE_URL` and `DATABASE_URL_TEST`.

Run `template status` and `template verify` from a generated or adopted product root. The master template itself does not use product lifecycle state.

```sh
python tools/control.py template status
python tools/control.py template verify
```

## Related documents

- [Tooling Guide](tooling.md)
- [Framework Architecture](../def/architecture.md)
- [Project Profiles](../def/project-profiles.md)
- [Template Lifecycle](../def/template-lifecycle.md)
- [Database Feature](../def/database-feature.md)
- [Runtime Configuration](../def/configuration.md)
- [Deployment Architecture](../def/deployment-architecture.md)
- [Release Model](release-model.md)
- [Template Migrations](template-migrations.md)
- [ATP Workflow](../atp/README.md)
