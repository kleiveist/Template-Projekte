<!-- AUTO-GENERATED:backlink START -->
[← Back](tools.md)
<!-- AUTO-GENERATED:backlink END -->
# Tooling Guide

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Contributors and release operators |
| Related ATP | [ATP-0001](../atp/completed/ATP-0001-template-lifecycle.md) |

## Purpose

This guide explains the central entry point for profile-based project scaffolding, setup, development, code-quality and architecture governance, testing, optional database migrations, builds, Tauri, release validation, and documentation maintenance. It is designed for contributors returning after a long break as well as first-time users of the template.

## Scope

The guide covers `tools/control.py`, the interactive console, and all profile, web, API, desktop, test-report, and PyGitIndex workflows exposed through that command. Run every example from the repository root.

## Safe return after a break

A command without arguments displays help and does not modify files:

```sh
python tools/control.py
```

Use this sequence to restore context and prepare the environment:

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py quality
python tools/control.py run
```

`doctor` checks runtimes, dependencies, the active profile, effective configuration, and configured ports. `install` prepares enabled frontend and backend dependencies without creating or changing `.env`. Frontend installation uses `npm ci` when `package-lock.json` exists. The command always prepares a dedicated `tools/.venv` containing Pytest, JSON Schema validation, Ruff, and Wasmtime 47.0.1 for shared tests and quality checks; it never reuses the backend runtime for that tooling contract. The tracked Syn 2.0.119 Rust analyzer runs as a checksum-verified WASI module, so Rust-free profiles do not need a native Rust toolchain merely to enforce the shared scanner. `doctor` exercises that real analyzer path rather than checking only that a Python package can be imported. The committed frontend baseline configures Playwright, so `install` also prepares Chromium for frontend-enabled projects; CI adds the required Linux browser libraries. `quality` runs the complete policy and language-tool gate for enabled components. `run` starts the enabled local services. In foreground mode, `Ctrl+C` stops those processes.

## Command map

| Command | Effect | Detailed help |
| --- | --- | --- |
| `init` | Generate a derived project from a selected profile | `python tools/control.py init --help` |
| `template` | Inspect, adopt, plan, update, and verify template lifecycle state | `python tools/control.py template` |
| `doctor` | Inspect the development environment | `python tools/control.py doctor --help` |
| `install` | Install or repair project dependencies | `python tools/control.py install --help` |
| `console` | Open the guided interactive interface | `python tools/control.py console --help` |
| `run` | Start the enabled local services | `python tools/control.py run --help` |
| `stop` | Stop tracked development services | `python tools/control.py stop --help` |
| `quality` | Run code-quality and architecture governance checks | `python tools/control.py quality --help` |
| `test` | Select test suites and reports | `python tools/control.py test` |
| `build` | Select a web, desktop, or container build | `python tools/control.py build` |
| `container` | Diagnose and validate Docker/Compose deployment files | `python tools/control.py container` |
| `version` | Show, synchronize, or check the application version | `python tools/control.py version` |
| `release` | Run the non-publishing release gate | `python tools/control.py release` |
| `config` | Show or validate effective runtime configuration | `python tools/control.py config` |
| `db` | Diagnose optional database configuration and run Alembic | `python tools/control.py db` |
| `docs` | Check navigation semantically or regenerate it with PyGitIndex | `python tools/control.py docs` |
| `tauri` | Manage desktop diagnostics, development, and artifacts | `python tools/control.py tauri` |

Group commands display the next level of help when called without an action:

```sh
python tools/control.py build
python tools/control.py container
python tools/control.py config
python tools/control.py db
python tools/control.py docs
python tools/control.py template
python tools/control.py test
python tools/control.py tauri
python tools/control.py release
```

An unknown command displays the relevant help map, explains the error, and provides the next `--help` command.

The former root aliases `--doctor`, `--install`, `--run`, `--stop`, `--test`, and `--build` remain compatibility shims. New documentation and automation use the command map above.

## Initialize a derived project

Preview the available profiles and choose one interactively:

```sh
python tools/control.py init
```

Generate a specific profile non-interactively:

```sh
python tools/control.py init --profile web-only
python tools/control.py init --profile desktop-cloud --target-dir ../desktop-cloud-app
python tools/control.py init --profile full-platform --dry-run
python tools/control.py init --profile web-cloud --with postgres
python tools/control.py init --profile desktop-cloud --name CustomerApp --identifier com.customer.app
```

The command writes into `.generated/<profile-id>` by default, or `.generated/<profile-id>-<capability>` when `--with` is used, so the master template is not modified accidentally. Repeat `--with` or pass comma-separated feature IDs for multiple capabilities. Use `--target-dir` for a real destination outside the template workspace.

Profile definitions live under `profiles/`. The generated project receives an active `project-profile.toml` manifest, a profile-aware `.env.example`, and tracked `.template/state.toml` and `.template/baseline.json` lifecycle metadata. The shared tooling reads the profile manifest to skip disabled runtime layers and renders only relevant environment variables. Lifecycle state records the exact source commit after all scaffold transformations. A dry-run writes none of these files.

## Template lifecycle

Display the lifecycle command map without changing files:

```sh
python tools/control.py template
```

The available actions are:

| Action | Behavior |
| --- | --- |
| `status` | Read installed provenance, manifest validity, identity, version, and local drift |
| `audit` | Compare a legacy product with a selected target scaffold without requiring state |
| `adopt` | Preview or write lifecycle metadata for an existing product without changing product source |
| `plan` | Reconstruct BASE and INCOMING and produce deterministic operations and conflicts |
| `update` | Preview the plan, or stage, verify, and transactionally apply it with `--apply` |
| `verify` | Validate lifecycle state, manifest, profile, identity, versions, and safety invariants offline |

Read a managed product locally:

```sh
python tools/control.py template status
python tools/control.py template verify
python tools/control.py template status --format json
```

Legacy comparison and adoption require an explicit trusted local template source and identity inputs:

```sh
python tools/control.py template audit \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha> \
  --profile <profile-id> \
  --name "<Product Name>" \
  --slug <product-slug> \
  --identifier <reverse-domain-identifier>

python tools/control.py template adopt \
  --target-dir ../Product \
  --source-dir . \
  --baseline-ref <trusted-template-tag-or-sha> \
  --profile <profile-id> \
  --name "<Product Name>" \
  --slug <product-slug> \
  --identifier <reverse-domain-identifier> \
  --apply
```

Plan and apply a managed update:

```sh
python tools/control.py template plan \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha>

python tools/control.py template update \
  --target-dir ../Product \
  --source-dir . \
  --to-ref <trusted-template-tag-or-sha> \
  --apply
```

Writing requires `--apply`; without it, adoption and update remain previews. Apply requires a completely clean product worktree, including no untracked files. It re-resolves the target ref, blocks the entire update on a conflict, verifies a staging tree, writes lifecycle state last, and restores the original product on failure. It does not fetch, commit, push, merge, tag, release, change profiles, or run product database migrations.

Use `--report-dir` when a specific ignored report location is required. The default is `.report/template-lifecycle/<run-id>/` with a Markdown summary, versioned JSON plan and verification, a patch, and structured conflict data. Reports contain relative paths and omit protected files, environment dumps, and secrets.

Lifecycle command exit codes are `0` for successful help or operations, `1` for operational, conflict, migration, or verification failures, and `2` for invalid usage. Expected failures are reported without a traceback. See [Template lifecycle](../def/template-lifecycle.md) for ownership and transaction rules and [Template migrations](template-migrations.md) for the declarative registry.

## Interactive console

Start the guided interface with:

```sh
python tools/control.py console
```

The main menu is divided by intent:

| Section | Available workflows |
| --- | --- |
| Environment and dependency setup | Doctor, complete install, frontend-only install, backend-only install, install help |
| Development services | Foreground start, detached start, stop, service help |
| Tests and reports | Quick check, complete suite, individual suite, report generation, report cleanup, test map |
| Web and desktop builds | Web package, desktop dry-run, confirmed platform build, build map |
| Tauri desktop workflows | Doctor, structure test, full checks, prerequisite preview/install, development run, artifact previews, Tauri map |
| Documentation indexing | PyGitIndex preview, normal update, compact README update, documentation help |

Use `b` to return from a section and `q` to close the console. The console requires confirmation before dependency installation, report deletion, real native builds, Tauri prerequisite installation, or documentation updates. Read-only checks and dry-runs execute immediately.

The console delegates to the same `tools/control.py` commands documented here. It does not implement a separate hidden workflow, so every interactive action remains reproducible from the shell.

## Start and stop development services

```sh
# Foreground; Ctrl+C stops all enabled services
python tools/control.py run

# Background; PID and log files are stored under tools/.runtime
python tools/control.py run --detach

# Stop background services
python tools/control.py stop
```

Use `.env` for persistent local overrides. Use `--frontend-host`, `--frontend-port`, `--backend-host`, and `--backend-port` for one command invocation. CLI values have the highest priority. Run `python tools/control.py run --help` for every option.

`run` starts only the services enabled by `project-profile.toml`. For example, `web-only` starts the frontend only, while `full-platform` starts frontend and backend together. `stop` likewise inspects only the ports belonging to enabled services unless it is stopping processes already recorded by a detached run.

## Runtime configuration

Inspect effective values and their source:

```sh
python tools/control.py config show
python tools/control.py config doctor
```

Values resolve in this order:

1. CLI override;
2. process environment;
3. root `.env`;
4. template default from `config/environment.toml`.

`config show` displays only variables applicable to the active features and masks secrets. `config doctor` validates environment names, hosts, ports, public URLs, CORS origins, and feature-required values without opening connections or changing files. The general `doctor` includes this validation. Use `db doctor --connect` only for the optional read-only database connection probe.

The root `.env.example` is safe to commit. Local `.env` files are ignored and are never generated or overwritten by `install`. See [Runtime Configuration](../def/configuration.md) for the complete variable table and runtime boundaries.

## Quality and architecture governance

A bare quality command performs the complete gate:

```sh
python tools/control.py quality
```

Focused actions are available for diagnosis without defining a second policy:

```sh
python tools/control.py quality size
python tools/control.py quality complexity
python tools/control.py quality architecture
python tools/control.py quality lint
python tools/control.py quality format
python tools/control.py quality check --format json
```

The command loads `config/code-quality.toml`, scans handwritten source, validates controlled exceptions, checks configured architecture boundaries, and delegates language-specific work to Ruff, ESLint, Prettier, TypeScript, rustfmt, Clippy, and Cargo for the enabled profile. `WARNING` and `STRONG_WARNING` findings do not fail by themselves. An unsuppressed `ERROR`, invalid policy, failed required tool, or analysis failure returns a non-zero exit code. A `CQ001` file-size finding above 900 code lines is an unsuppressible error; a configured exception cannot turn 901 lines into an accepted file.

The dispatcher remains `tools/control.py`; parser construction lives in `tools/control_parser.py`, and policy loading, scanning, exception handling, reporting, architecture analysis, and tool adapters live under `tools/quality/`. Run the complete bare command before hand-off even when a focused action was used during investigation. See [Code quality and architecture governance](../def/code-quality.md) for thresholds and stable rule IDs.

## Tests and reports

```sh
python tools/control.py test --suite api
python tools/control.py test --suite frontend
python tools/control.py test --suite tools
python tools/control.py test --suite all
python tools/control.py test --suite all --report
```

| Suite | Content |
| --- | --- |
| `api` | FastAPI tests |
| `schema` | Shared JSON Schema and examples |
| `database` | SQLAlchemy configuration, engine, and session unit tests |
| `postgres` | PostgreSQL connection test; skipped without an available `DATABASE_URL_TEST` |
| `frontend` | Vitest unit tests with 100% per-file coverage thresholds for governed frontend modules |
| `e2e` | Playwright Chromium smoke tests over enabled services plus axe accessibility analysis |
| `tools` | Project CLI and Tauri helper tests |
| `tauri` | Tauri structure, `cargo check --locked`, and Rust tests |
| `all` | Every configured suite |

Reports are written under `.report/`. `python tools/control.py test --report done` removes only that generated report directory.

When the active project profile disables a feature, its affected suites report `SKIP` and return success. Missing tests or source files for an enabled feature report `FAIL`. PostgreSQL reports `SKIP` when `DATABASE_URL_TEST` is absent, but a configured invalid or unreachable test database reports `FAIL`.

## Database diagnostics and migrations

Database commands require the optional `database` capability. A project without it receives `Database feature is not enabled for this project.` and no traceback.

Set `DATABASE_URL` in the server process environment or root `.env`, then run the read-only diagnostics:

```sh
python tools/control.py db doctor
python tools/control.py db doctor --connect
python tools/control.py db current
```

The normal doctor validates configuration and imports only. `--connect` additionally opens a connection, executes `SELECT 1`, and closes it without modifying data.

Apply or revert migrations explicitly:

```sh
python tools/control.py db upgrade
python tools/control.py db downgrade
python tools/control.py db revision --message "add example"
```

FastAPI startup never runs these commands automatically. See [Database Feature](../def/database-feature.md) for configuration, dependency, and security details.

## Builds

Display the available build targets first:

```sh
python tools/control.py build
```

A web build creates `frontend/dist/` and `.dist/web/template-project-web.zip`:

```sh
python tools/control.py build web
```

Run Tauri diagnostics and a dry-run before the first native build:

```sh
python tools/control.py tauri doctor
python tools/control.py build desktop --dry-run --no-clean
python tools/control.py build desktop
python tools/control.py build desktop --target linux --bundles deb,rpm,appimage
```

Platform strategies and bundle options are documented by:

```sh
python tools/control.py build desktop --help
python tools/control.py tauri build --help
```

Linux bundle selectors are limited to `deb`, `rpm`, and `appimage`. The tooling normalizes case and whitespace, removes duplicates in a stable order, and rejects empty or unknown values. A successful real Linux build automatically verifies every requested format and writes `.dist/desktop/linux/linux-bundles.json` and `.dist/desktop/linux/SHA256SUMS`. Normal Desktop CI requests only `deb`; Release Validation explicitly requests `deb,rpm,appimage`.

The Tauri map also provides prerequisite setup, development mode, local AppImage installation, explicit artifact verification, and artifact collection. The generated Linux files are unsigned x86_64 verification candidates, not published packages or evidence of compatibility with every Linux distribution. See the [Release Model](release-model.md) for format purposes, runner and glibc limitations, and excluded distribution integrations.

Desktop build and `tauri` commands require the active profile to enable `tauri`. Otherwise they fail with a clear profile-based message.

Cloud-enabled profiles additionally support provider-neutral image builds:

```sh
python tools/control.py container doctor
python tools/control.py container validate
python tools/control.py build container
python tools/control.py build container --component backend
```

Version display, synchronization, and release validation remain separate from publication:

```sh
python tools/control.py version
python tools/control.py version sync
python tools/control.py version check
python tools/control.py release check
```

Bare `version` prints the product `VERSION` source of truth in a generated project. `version sync` updates enabled product component metadata, while `version check` compares it without writing. The installed template version and exact commit are separate fields in lifecycle state; `template update` never invokes `version sync`. `release check` validates version consistency, identity, Tauri security, tag context, and repository cleanliness; it neither creates a tag nor publishes a release.

See [Container Builds](container-builds.md) and [Release Model](release-model.md) for production boundaries, migrations, signing, and platform artifacts.

## Documentation checks and indexing

Run the self-contained semantic gate at any time:

```sh
python tools/control.py docs check
```

`docs check` is read-only and does not require PyGitIndex. It validates generated marker structure, expected backlinks, link targets, duplicate and stale entries, and the page coverage of directory and README navigation blocks. It returns non-zero when tracked navigation is inconsistent. Core CI exposes it as `Core / Documentation Check`, one of six active Core jobs, and Release Validation repeats it for the candidate SHA.

After adding, moving, renaming, or deleting Markdown files, optionally preview the index and backlink changes:

```sh
python tools/control.py docs index --dry-run
```

Apply the update intentionally, inspect the resulting diff, and run the semantic gate:

```sh
python tools/control.py docs index
git diff -- README.md docs
python tools/control.py docs check
```

The wrapper searches in this order:

1. the explicit `--script <path>` value;
2. `PYGITINDEX_PATH`;
3. a `PyGitIndex`, `PyGitIndex.py`, or `pygitindex` command on `PATH`;
4. known `Documents` or `Dokumente` locations below the current user's home directory.

The system script remains responsible for index files, README navigation, and backlinks. Because the installed script emits two German empty-state labels, the wrapper translates only those labels inside generated index markers. Authored prose is never rewritten by the normalizer.

Useful options:

```sh
python tools/control.py docs index --compact
python tools/control.py docs index --no-backlinks
python tools/control.py docs index --no-readme
python tools/control.py docs index --script /path/to/PyGitIndex.py
```

PyGitIndex is required only for regeneration. `docs index --dry-run` returning zero means the external preview completed; it does not mean that navigation was already current. CI and release validation use `docs check` so drift fails without silently rewriting tracked files. Do not manually edit blocks between `AUTO-GENERATED` markers.

## Troubleshooting

1. Repeat the failed command with `--help`.
2. Run `python tools/control.py doctor`.
3. Repair project dependencies with `python tools/control.py install`.
4. For desktop problems, also run `python tools/control.py tauri doctor`.
5. For lifecycle state or identity drift, run `python tools/control.py template status` followed by `template verify`; do not apply an update until verification and Git cleanliness are restored.
6. For navigation drift, run `python tools/control.py docs check`; for regeneration problems, run `python tools/control.py docs index --dry-run --script <path>`.
7. Rerun only the affected test suite, then run `--suite all` before hand-off.

Suites disabled by the active profile are reported as `SKIP` during `test --suite all`. Missing optional accelerators such as `uv` do not reduce the Doctor status. A configured browser suite is required for every frontend-enabled profile; a `FAIL` means the selected workflow did not complete successfully.

## Verification

After a tooling change, run at least:

```sh
python tools/control.py
python tools/control.py doctor
python tools/control.py config doctor
python tools/control.py init --profile web-only --dry-run
python tools/control.py template
python tools/control.py quality
python tools/control.py build
python tools/control.py docs
python tools/control.py test
python tools/control.py tauri
python tools/control.py version check
python tools/control.py release check
python tools/control.py docs check
python tools/control.py test --suite tools
python tools/control.py build desktop --dry-run --no-clean
```

From each generated or adopted product root, additionally run:

```sh
python tools/control.py template status
python tools/control.py template verify
```

## Related documents

- [Documentation Standard](../README.md)
- [Framework Architecture](../def/architecture.md)
- [Template Lifecycle](../def/template-lifecycle.md)
- [Database Feature](../def/database-feature.md)
- [Runtime Configuration](../def/configuration.md)
- [Project Profiles](../def/project-profiles.md)
- [Continuous Integration](ci.md)
- [Container Builds](container-builds.md)
- [Template Migrations](template-migrations.md)
- [Release Model](release-model.md)
- [ATP Workflow](../atp/README.md)
