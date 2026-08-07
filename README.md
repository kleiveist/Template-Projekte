# Full-Stack Project Template

This repository is the master template for applications built with Vite and TypeScript, FastAPI, and Tauri 2. It keeps one shared core and provides project profiles instead of separate template repositories.

## Start here

Most developers should generate a new product project from this repository and then work in the generated project. Do not build product features directly in the cloned master template.

```text
Product development (normal path)
Master template -> choose a profile -> generate a project -> change directory -> install -> run

Template maintenance
Master template -> doctor -> install -> test or develop the template itself
```

The complete first-time product workflow is:

```text
git clone
    -> cd Template-Projekte
    -> python tools/control.py doctor
    -> python tools/control.py init
    -> cd into the generated project
    -> python tools/control.py doctor
    -> python tools/control.py install
    -> python tools/control.py run
    -> start product development
```

### What you need installed

Always required:

- Git
- Python 3.11 or newer
- Node.js 20 or newer with npm

Required for desktop profiles:

- Rust Stable
- The [platform-specific Tauri prerequisites](https://v2.tauri.app/start/prerequisites/)

Required only for specific workflows:

- Docker with Docker Compose for container builds or local production simulation
- A reachable PostgreSQL service when using the optional `postgres` capability
- The system `PyGitIndex.py` script only when regenerating documentation navigation

Optional tools are not required for an ordinary web project. Start with `doctor`; its messages identify missing requirements and distinguish them from optional tooling.

### Path A: Create a product from the template

This is the normal path for a new application.

#### Step 1: Clone the template

```sh
git clone https://github.com/kleiveist/Template-Projekte.git
cd Template-Projekte
```

All commands in this guide run from the root of the current repository or generated project.

#### Step 2: Check your environment

```sh
python tools/control.py doctor
```

`doctor` is read-only: it checks tools, the active profile, project files, runtime configuration, dependencies, and relevant ports without changing project files. It is also the first command to run when something does not work.

Warnings about explicitly optional tooling do not mean that every workflow is blocked. For example, Docker is not needed to run the normal Vite and FastAPI development services.

#### Step 3: Inspect the command map (optional)

```sh
python tools/control.py
```

The command prints the available workflows and does not modify files. Every command also supports `--help`.

#### Step 4: Choose a project profile

| If you want to build... | Choose |
| --- | --- |
| Browser-only frontend | `web-only` |
| Browser app with FastAPI backend | `web-cloud` |
| Local desktop application | `desktop-local` |
| Desktop app with cloud backend | `desktop-cloud` |
| Browser + desktop + backend | `full-platform` |

Start the guided profile and optional-capability selection with:

```sh
python tools/control.py init
```

Without `--target-dir`, the generated project is written to `.generated/<profile-id>` (or `.generated/<profile-id>-<capability>`). The completed command prints the exact destination. For example, after selecting `web-only`:

```sh
cd .generated/web-only
```

For a product directory next to the template, use an explicit destination. A web product with a backend can be generated with:

```sh
python tools/control.py init \
  --profile web-cloud \
  --name MyProject \
  --target-dir ../MyProject
```

Desktop products with a custom name also require a reverse-domain Tauri identifier:

```sh
python tools/control.py init \
  --profile desktop-cloud \
  --name MyProject \
  --identifier com.example.myproject \
  --target-dir ../MyProject
```

PostgreSQL is an optional capability, not a separate project profile. Add it only to a backend-enabled profile:

```sh
python tools/control.py init --profile web-cloud --with postgres
```

See [Project profiles](docs/def/project-profiles.md) for the complete feature model and compatibility rules.

#### Step 5: Change into the generated project

After either explicit `../MyProject` example above, run:

```sh
cd ../MyProject
```

This directory is now the product project. Product code, configuration, tests, and commits belong here. The original `Template-Projekte` directory remains the master template.

#### Step 6: Check the generated project

```sh
python tools/control.py doctor
```

The generated `project-profile.toml` records the selected profile and resolved features. The tooling reads it and checks or starts only the relevant application layers:

- a web-only project does not require FastAPI, Rust, or Tauri;
- a desktop project requires Rust and the platform-specific Tauri prerequisites;
- PostgreSQL is relevant only when the `postgres` capability was selected; and
- Docker is optional unless a container workflow is used.

For a detailed check of desktop system prerequisites, use `python tools/control.py tauri doctor` after the general project doctor.

#### Step 7: Install dependencies

```sh
python tools/control.py install
```

`install` is the public setup command. It installs only the frontend, backend, shared tooling, and optional browser-test components relevant to the active project. You do not need to begin with separate `npm install`, `pip install`, or Cargo commands.

#### Step 8: Start development

```sh
python tools/control.py run
```

`run` starts the enabled Vite frontend and, when present, FastAPI backend in the foreground. Press `Ctrl+C` to stop all processes started by the command.

The default development addresses are:

| Available in | Address |
| --- | --- |
| Every current profile: frontend | `http://127.0.0.1:5173` |
| Profiles with a backend: API | `http://127.0.0.1:8000` |
| Profiles with a backend: health | `http://127.0.0.1:8000/api/health` |
| Profiles with a backend: readiness | `http://127.0.0.1:8000/api/ready` |

`web-only` and `desktop-local` do not include a backend, so they do not expose the API, health, or readiness addresses. To open the native shell of a desktop profile, use `python tools/control.py tauri run --foreground`; the central `run` command remains the service-development entry point.

Frontend code is under `frontend/`. Backend code, when enabled, is under `backend/`. Confirm the active profile in `project-profile.toml`, then run the complete configured test set with:

```sh
python tools/control.py test --suite all
```

### Guided console

If you do not remember CLI options, open the guided menus:

```sh
python tools/control.py console
```

The console provides guided access to setup, development services, tests, builds, Tauri, and documentation. It is an alternative interface to the same commands, not a separate workflow.

### Something does not work?

Run these checks in order:

1. Diagnose the environment and active profile:

   ```sh
   python tools/control.py doctor
   ```

2. Validate effective configuration:

   ```sh
   python tools/control.py config doctor
   ```

3. Inspect the general or command-specific help:

   ```sh
   python tools/control.py --help
   python tools/control.py <command> --help
   ```

4. Continue with the [Tooling Guide](docs/tools/tooling.md) for detailed diagnostics and command reference.

### Path B: Develop the master template

This path is for maintainers changing and testing the reusable template itself. It does not generate a customer or product project.

```sh
git clone https://github.com/kleiveist/Template-Projekte.git
cd Template-Projekte

python tools/control.py doctor
python tools/control.py install
python tools/control.py test --suite all
```

Use `python tools/control.py run` when developing the master template's reference application locally. Template maintainers can also use the focused commands described in the [Tooling Guide](docs/tools/tooling.md).

## Included stack

| Area | Technology | Responsibility |
| --- | --- | --- |
| Web frontend | Vite 6, TypeScript 5, Vitest | Browser user interface and frontend tests |
| Backend | FastAPI, Uvicorn, Pytest | HTTP API and API tests |
| Optional database | SQLAlchemy 2.x, Alembic, PostgreSQL, Psycopg 3 | Server-side persistence and explicit migrations |
| Desktop | Tauri 2, Rust | Native desktop shell for the web frontend |
| Tooling | Python | Shared setup, development, testing, build, and documentation workflows |

## Project profiles and runtime behavior

Profiles are reusable presets over shared features. The master repository contains all feature modules, while a generated project's `project-profile.toml` tells `install`, `doctor`, `run`, `test`, and build commands which components are active.

Runtime values are separate from profiles. Use `python tools/control.py config show` to inspect masked effective values and `python tools/control.py config doctor` to validate them. See [Runtime configuration](docs/def/configuration.md) for value priority and security boundaries.

PostgreSQL support adds SQLAlchemy, Alembic, and Psycopg only when selected with `--with postgres`. See [Database feature](docs/def/database-feature.md). Cloud-enabled profiles include provider-neutral Docker boundaries; Docker remains optional for ordinary local development. See [Deployment architecture](docs/def/deployment-architecture.md) and [Container builds](docs/tools/container-builds.md).

## Project structure

```text
backend/             FastAPI application and API tests (backend profiles only)
config/              Declarative runtime environment contract
deployment/          Provider-neutral Docker and Compose baseline (cloud profiles only)
docs/                Documentation rules, architecture, and acceptance plans
frontend/            Vite and TypeScript application and frontend tests
profiles/            Declarative feature and profile definitions
project-profile.toml Active feature preset for the current project root
shared/              Framework-neutral contracts, examples, and shared assets
src-tauri/           Tauri configuration and Rust application (desktop profiles only)
tools/control.py     Shared project CLI entry point
```

## Detailed documentation

The README answers “How do I start?” The linked guides answer “How does it work?”

- [Tooling Guide](docs/tools/tooling.md): complete command and console reference
- [Project profiles](docs/def/project-profiles.md): profiles, features, and generation rules
- [Runtime configuration](docs/def/configuration.md): environment contract and precedence
- [Database feature](docs/def/database-feature.md): optional PostgreSQL and migrations
- [Framework architecture](docs/def/architecture.md): component boundaries
- [Deployment architecture](docs/def/deployment-architecture.md): production units and health contracts
- [Continuous Integration](docs/tools/ci.md): automated profile and platform checks
- [Release model](docs/tools/release-model.md): validation and desktop packaging
- [Documentation Standard](docs/README.md): repository language and authoring rules

English is the only documentation language for this repository and projects derived from it. A new or changed feature is complete only when its code, tests, acceptance evidence, and affected documentation are updated together.

## Documentation index

<!-- AUTO-GENERATED:docs-index START -->

## 📄 Files
- ⏭️ (no Markdown files in the project root)

# DOCS
- 📚 [Docs Home](docs/index.md)
- 📝 [<Document title>](docs/DOCUMENT-TEMPLATE.md)

## 📁 ATP
- 🗂️ [Overview](docs/atp/atp.md)
- 📝 [ATP-<ID>: <Acceptance title>](docs/atp/ATP-TEMPLATE.md)

## 📁 DEF
- 🗂️ [Overview](docs/def/def.md)
- 📝 [Framework architecture](docs/def/architecture.md)
- 📝 [Runtime configuration](docs/def/configuration.md)
- 📝 [Database feature](docs/def/database-feature.md)
- 📝 [Deployment architecture](docs/def/deployment-architecture.md)
- 📝 [Project profiles](docs/def/project-profiles.md)

## 📁 DEV
- 🗂️ [Overview](docs/dev/dev.md)
- 📝 [Template final acceptance](docs/dev/template-final-acceptance.md)

## 📁 Tools
- 🗂️ [Overview](docs/tools/tools.md)
- 📝 [Continuous Integration](docs/tools/ci.md)
- 📝 [Container builds and local production simulation](docs/tools/container-builds.md)
- 📝 [Release and desktop packaging model](docs/tools/release-model.md)
- 📝 [Tooling Guide](docs/tools/tooling.md)

## 📁 USR
- 🗂️ [Overview](docs/usr/usr.md)

<!-- AUTO-GENERATED:docs-index END -->
