<!-- AUTO-GENERATED:backlink START -->
[← Back](def.md)
<!-- AUTO-GENERATED:backlink END -->
# Project profiles

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-06 |
| Audience | Developers and architects |
| Related ATP | N/A — template-level profile model |

## Purpose

This document defines how the repository models project profiles. A profile is a reusable preset over shared features. It is not a separate template implementation.

## Scope

### Included

- feature and profile terminology;
- declarative profile definitions under `profiles/`;
- the active project manifest in `project-profile.toml`;
- the scaffold flow behind `python tools/control.py init`; and
- the current baseline profile set.

### Excluded

- product-specific feature modules;
- database, authentication, Docker, CI/CD, or deployment details; and
- post-generation renaming or branding automation.

## Definitions

| Term | Meaning |
| --- | --- |
| Core | Shared repository content copied into every generated project, for example `docs/`, `tools/`, `shared/`, and root metadata files |
| Feature | A reusable technical capability, such as `frontend`, `backend`, `tauri`, or `cloud` |
| Profile | A named preset that enables a validated feature combination |
| Active project profile | The machine-readable manifest at `project-profile.toml` used by tooling inside the current project root |

## Single-repository strategy

The repository remains one master template. It does not branch into separate template repositories for web, desktop, or cloud variants.

The reasons are:

- code, tooling, and documentation stay in one maintenance stream;
- feature dependencies are validated once instead of duplicated across repositories;
- new capabilities such as `sql`, `postgres`, `auth`, `docker`, or `redis` can be introduced as additive features; and
- profiles remain small presets over the same core instead of becoming long-lived forks.

## Declarative files

`profiles/features.toml` defines shared core paths, feature metadata, and feature dependencies.

Each `profiles/<profile-id>.toml` file defines:

- `id`
- `name`
- `description`
- `features`
- `order`

Example:

```toml
schema_version = 1
id = "desktop-cloud"
order = 40
name = "Desktop + Cloud"
description = "Tauri desktop client backed by a FastAPI cloud API."
features = ["frontend", "backend", "tauri", "cloud"]
```

The active project manifest uses the same core fields in `project-profile.toml`.

## Current profiles

| Profile | Frontend | FastAPI | Tauri | Cloud | Enabled features |
| --- | ---: | ---: | ---: | ---: | --- |
| `web-only` | Yes | No | No | No | `frontend` |
| `web-cloud` | Yes | Yes | No | Yes | `frontend`, `backend`, `cloud` |
| `desktop-local` | Yes | No | Yes | No | `frontend`, `tauri` |
| `desktop-cloud` | Yes | Yes | Yes | Yes | `frontend`, `backend`, `tauri`, `cloud` |
| `full-platform` | Yes | Yes | Yes | Yes | `frontend`, `backend`, `tauri`, `cloud` |

## Feature dependency rules

The current baseline validates these dependencies:

- `tauri` requires `frontend`
- `cloud` requires `backend`

Future features extend the same dependency model, for example `postgres` requiring `backend`.

Invalid combinations are rejected with explicit errors. Example:

```text
Feature 'tauri' requires feature 'frontend'.
```

## Generator model

`python tools/control.py init` resolves a profile, builds a scaffold plan from core paths plus enabled feature paths, then writes a derived project into `.generated/<profile-id>` by default or an explicit `--target-dir`.

The generated project receives:

- shared core paths from `profiles/features.toml`;
- feature-owned directories such as `frontend/`, `backend/`, or `src-tauri/`;
- the copied `profiles/` definitions for future reference; and
- a generated `project-profile.toml` manifest.

The generator does not clone separate template repositories. It also does not mutate the master template root.

## Tooling behavior

The shared tooling reads `project-profile.toml` and adjusts behavior:

- `install` skips disabled runtime layers;
- `doctor` reports disabled layers as intentionally inactive;
- `run` starts only enabled services;
- `build desktop` and `tauri ...` reject disabled desktop workflows cleanly; and
- frontend starter code uses a generated profile module to hide the backend status check when the backend feature is disabled.

## Extension path

To add a future capability:

1. extend `profiles/features.toml` with the new feature and its dependencies;
2. attach owned paths only when the feature introduces dedicated scaffold content;
3. update one or more profile presets; and
4. add tests and documentation in the same change.

This keeps profile growth additive rather than architectural.

## Verification

```sh
python tools/control.py init --profile web-only --dry-run
python tools/control.py init --profile desktop-cloud --dry-run
python tools/control.py test --suite tools
```

## Related documents

- [Framework architecture](architecture.md)
- [Tooling Guide](../tools/tooling.md)
- [Project README](../../README.md)
