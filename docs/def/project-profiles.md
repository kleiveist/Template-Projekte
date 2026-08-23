<!-- AUTO-GENERATED:backlink START -->
[← Back](def.md)
<!-- AUTO-GENERATED:backlink END -->
# Project profiles

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-23 |
| Audience | Developers and architects |
| Related ATP | [ATP-0001](../atp/active/ATP-0001-template-lifecycle.md) |

## Purpose

This document defines how the repository models project profiles. A profile is a reusable preset over shared features. It is not a separate template implementation and does not prescribe how a product persists user data.

## Scope

### Included

- feature and profile terminology;
- declarative profile definitions under `profiles/`;
- the active project manifest in `project-profile.toml`;
- the scaffold flow behind `python tools/control.py init`;
- lifecycle preservation of the selected profile and optional capabilities; and
- the current baseline profile set.

### Excluded

- product-specific feature modules;
- database implementation details, authentication, Docker, CI/CD, or deployment details; and
- post-generation renaming or branding automation.

## Definitions

| Term | Meaning |
| --- | --- |
| Core | Shared repository content copied into every generated project, for example `docs/`, `tools/`, `shared/`, and root metadata files |
| Feature | A reusable technical capability, such as `frontend`, `backend`, `tauri`, or `cloud` |
| Profile | A named preset that enables a validated feature combination |
| Optional capability | An additive feature selected with `--with` after choosing a platform profile |
| Active project profile | The machine-readable manifest at `project-profile.toml` used by tooling inside the current project root |

Profiles define project structure, not runtime environments or product-data persistence. `development`, `test`, and `production` use the same profile with different environment values. Ports, hosts, URLs, secrets, user-data formats, and sources of truth never belong in `project-profile.toml`.

## Single-repository strategy

The repository remains one master template. It does not branch into separate template repositories for web, desktop, or cloud variants.

The reasons are:

- code, tooling, and documentation stay in one maintenance stream;
- feature dependencies are validated once instead of duplicated across repositories;
- new capabilities such as `postgres`, `auth`, `docker`, or `redis` can be introduced as additive features; and
- profiles remain small presets over the same core instead of becoming long-lived forks.

## Declarative files

`profiles/features.toml` defines shared core paths, feature metadata, and feature dependencies.

Each `profiles/<profile-id>.toml` file defines:

- `id`
- `name`
- `description`
- `features`
- `order`

Feature definitions can additionally declare `optional`, `selectable`, `requires`, and owned scaffold `paths`. Runtime-variable definitions in `config/environment.toml` can declare `required_features`; the generator renders matching safe examples into `.env.example`. Optional capabilities are never hardcoded into platform profile files.

Example:

```toml
schema_version = 1
id = "desktop-cloud"
order = 40
name = "Desktop + Cloud"
description = "Tauri desktop client backed by a FastAPI cloud API."
features = ["frontend", "backend", "tauri", "cloud"]
```

The active project manifest adds `optional_features` and stores the fully resolved `features` list in `project-profile.toml`.

## Current profiles

| Profile | Frontend | FastAPI | Tauri | Cloud | Current `postgres` capability | Enabled profile features |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `web-only` | Yes | No | No | No | Not compatible | `frontend` |
| `web-cloud` | Yes | Yes | No | Yes | Optional | `frontend`, `backend`, `cloud` |
| `desktop-local` | Yes | No | Yes | No | Not compatible | `frontend`, `tauri` |
| `desktop-cloud` | Yes | Yes | Yes | Yes | Optional | `frontend`, `backend`, `tauri`, `cloud` |
| `full-platform` | Yes | Yes | Yes | Yes | Optional | `frontend`, `backend`, `tauri`, `cloud` |

The master repository selects `postgres` in its own `project-profile.toml` so its complete optional implementation and tests are available for maintenance. This does not modify the `full-platform` preset: a generated full-platform project includes PostgreSQL only when `--with postgres` is supplied.

## Profile and persistence independence

Platform selection and persistence design are separate decisions:

- `desktop-local` includes `frontend + tauri` and no persistence provider. It implies neither JSON nor SQLite. A derived product can later choose no persistence, local files, an embedded database, or a product-specific solution.
- `desktop-cloud` includes a client and backend but no database provider by default. It implies neither a local store nor PostgreSQL. `--with postgres` adds the existing server-side SQL path; any local or offline store remains a separate product decision.
- `web-cloud` and `full-platform` can also select `postgres`, but PostgreSQL becomes authoritative only when the product architecture names it as the source of truth.
- `web-only` has no backend and cannot select the current backend-bound `postgres` capability. This compatibility rule does not prescribe a product-data format.

If a product combines local and remote storage, it documents which store is authoritative and defines any synchronization, revision, and conflict behavior. See [Provider-neutral persistence architecture](persistence-architecture.md) for the decision framework.

## Feature dependency rules

The current baseline validates these dependencies:

- `tauri` requires `frontend`
- `cloud` requires `backend`
- `database` provides server-side SQL infrastructure and requires `backend`
- `postgres` requires `database`

Future features extend the same dependency model, for example `auth` requiring `backend`.

Optional dependency resolution is transitive. `--with postgres` adds `database`, but it does not silently add the non-optional `backend` platform feature. Therefore backend-enabled profiles accept PostgreSQL while `web-only` and `desktop-local` reject it with a clear dependency error.

Example resolution:

```text
web-cloud + postgres
= frontend + backend + cloud + database + postgres
```

Invalid combinations are rejected with explicit errors. Example:

```text
Feature 'tauri' requires feature 'frontend'.
```

Catalog paths must be relative, use forward slashes, stay inside the master repository, and avoid `.` or `..` segments. Unknown dependencies and dependency cycles are rejected before generation.

## Generator model

`python tools/control.py init` resolves a profile, builds a scaffold plan from core paths plus enabled feature paths, then writes a derived project into `.generated/<profile-id>` by default or an explicit `--target-dir`.

Use repeated `--with` flags for optional capabilities:

```sh
python tools/control.py init --profile web-cloud --with postgres
python tools/control.py init --profile desktop-cloud --name CustomerApp --identifier com.customer.app
```

The generated project receives:

- shared core paths from `profiles/features.toml`;
- feature-owned directories such as `frontend/`, `backend/`, or `src-tauri/`;
- the copied `profiles/` definitions for future reference;
- a generated `project-profile.toml` manifest; and
- tracked `.template/state.toml` provenance and a deterministic `.template/baseline.json` scaffold manifest.

The shared core deliberately includes the governance and release surface: `AGENTS.md`, `VERSION`, `config/`, `docs/`, `shared/`, and `tools/`. Consequently every derived project carries the same code-quality policy, architecture checks, command entry point, and version contract. Feature selection removes disabled runtime implementations; it does not remove the controls used to verify the resulting project.

When `--name` is supplied, the generator also derives or validates the project slug and updates package, backend, Compose, Tauri, and Cargo identity metadata. A customized Tauri project requires an explicit reverse-domain `--identifier`. This avoids shipping known template identities accidentally.

For profiles without `tauri`, the generator also removes the Tauri npm script and CLI dependency from the copied frontend package metadata and lockfile. This keeps disabled desktop tooling out of web dependency installation without maintaining a second frontend template.

The generator does not clone separate template repositories. It also does not mutate the master template root.

Lifecycle metadata is created after all profile filtering, environment-example rendering, identity replacement, and metadata normalization. `init --dry-run` writes neither the scaffold nor lifecycle files. A clean template checkout records `provenance = "generated"`; a development scaffold from uncommitted template content records `provenance = "working-tree"` and cannot be updated automatically until it is explicitly re-adopted against a clean commit.

Master repository tests validate that every catalog path exists. Each generator run validates the selected scaffold plan before writing files. A derived project loads the same catalog without requiring paths owned by disabled features, then validates its active feature selection from `project-profile.toml`. This distinction lets reduced projects keep shared tooling while intentionally omitting inactive layers.

## Tooling behavior

The shared tooling reads `project-profile.toml` and adjusts behavior:

- `install` skips disabled runtime layers and prepares the dedicated `tools/.venv` with Pytest, JSON Schema validation, Ruff,
  and Wasmtime independently of any backend virtualenv. Every profile receives the checksum-verified Syn/WASI Rust analyzer
  and the root `.gitattributes` contract that preserves its LF build inputs on Windows, so shared Rust source scanning remains
  available without imposing a native Rust toolchain on Rust-free profiles;
- `doctor` reports disabled layers as intentionally inactive;
- `run` starts only enabled services;
- `stop` inspects only ports owned by enabled services;
- `build desktop` and `tauri ...` reject disabled desktop workflows cleanly;
- `db ...` rejects projects without `database` and delegates explicit migrations to Alembic when enabled;
- `quality` always enforces shared file, architecture and tooling rules, while language-specific adapters run only for enabled technologies;
- `test --suite all` selects the applicable tool, frontend, backend, database and Tauri suites without treating disabled layers as missing;
- `version check` and `version sync` inspect or update only version mirrors owned by enabled components; and
- frontend starter code uses a generated profile module to hide the backend status check when the backend feature is disabled.

Profile awareness must never weaken repository governance. In particular, the hard `CQ001` error for a handwritten source file above 900 code lines remains unsuppressible in every generated project.

## Lifecycle invariants

An ordinary template update preserves `profile` and `optional_features`. It must not silently enable a backend, Tauri, PostgreSQL, or another capability, remove an enabled capability, or switch between platform profiles. A changed meaning of a resolved profile is an architecture change and requires an explicit lifecycle migration with documented preconditions and postconditions.

The lifecycle state records both the selected optional capabilities and the fully resolved feature set. `template status` warns about drift; `template verify` fails unsafe or inconsistent state. Adoption records an existing project's declared selection without changing product source files. General interactive profile migration is intentionally outside version 1.

## Extension path

To add a future capability:

1. establish a realistic reusable use case and a concrete technical contract;
2. extend `profiles/features.toml` with the implemented feature, optional metadata, and dependencies;
3. attach owned paths only when the feature introduces dedicated scaffold content or behavior;
4. mark it selectable when users should choose it with `--with`, without adding it to platform profile presets; and
5. add tests and documentation in the same change.

This keeps profile growth additive rather than architectural. Do not add empty catalog entries for documentation-only concepts. Future candidates such as `local-files`, `embedded-database`, or `sqlite` enter the catalog only when they become real reusable capabilities.

## Verification

The profile workflow generates all five presets into fresh target directories. It then installs their selected dependencies and applies this matrix:

| Profile | Lifecycle status and verify | Quality and all applicable tests | Web build | Container validation | Tauri doctor and desktop dry-run |
| --- | ---: | ---: | ---: | ---: | ---: |
| `web-only` | Required | Required | Required | Not applicable | Not applicable |
| `web-cloud` | Required | Required | Required | Required | Not applicable |
| `desktop-local` | Required | Required | Required | Not applicable | Required |
| `desktop-cloud` | Required | Required | Required | Required | Required |
| `full-platform` | Required | Required | Required | Required | Required |

PostgreSQL verification is a separate three-entry matrix because the capability requires an existing backend:

| Profile with `--with postgres` | Database upgrade and tests | Container validation | Desktop dry-run |
| --- | ---: | ---: | ---: |
| `web-cloud` | Required | Required | Not applicable |
| `desktop-cloud` | Required | Required | Required |
| `full-platform` | Required | Required | Required |

`web-only --with postgres` and `desktop-local --with postgres` must fail dependency validation; they are negative compatibility cases, not skipped positive cases. Desktop-native packaging is additionally verified on Linux, macOS, and Windows, with unsigned artifacts retained as build evidence. The exact CI job and artifact matrix is documented in [Continuous integration](../tools/ci.md).

Representative local checks are:

```sh
python tools/control.py init --profile web-only --dry-run
python tools/control.py init --profile desktop-cloud --dry-run
python tools/control.py init --profile web-cloud --with postgres --dry-run
python tools/control.py quality
python tools/control.py test --suite tools
```

Run lifecycle checks from an actual generated-project root:

```sh
python tools/control.py template status
python tools/control.py template verify
```

Generation and validation must leave the master repository unchanged; CI closes each matrix entry with `git diff --exit-code`.

## Related documents

- [Framework architecture](architecture.md)
- [Template lifecycle](template-lifecycle.md)
- [Provider-neutral persistence architecture](persistence-architecture.md)
- [Database feature](database-feature.md)
- [Runtime configuration](configuration.md)
- [Deployment architecture](deployment-architecture.md)
- [Tooling Guide](../tools/tooling.md)
- [Template migrations](../tools/template-migrations.md)
- [Project README](../../README.md)
