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

## 📁 DEV
- 🗂️ [Overview](docs/dev/dev.md)

## 📁 Tools
- 🗂️ [Overview](docs/tools/tools.md)
- 📝 [Tooling Guide](docs/tools/tooling.md)

## 📁 USR
- 🗂️ [Overview](docs/usr/usr.md)

<!-- AUTO-GENERATED:docs-index END -->
# Full-Stack Project Template

This repository is a lean starting point for applications built with Vite and TypeScript, FastAPI, and Tauri 2.

## Included stack

| Area | Technology | Responsibility |
| --- | --- | --- |
| Web frontend | Vite 6, TypeScript 5, Vitest | Browser user interface and frontend tests |
| Backend | FastAPI, Uvicorn, Pytest | HTTP API and API tests |
| Desktop | Tauri 2, Rust | Native desktop shell for the web frontend |
| Tooling | Python | Shared setup, development, testing, build, and documentation workflows |

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer with npm
- Rust Stable and the [platform-specific Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) for desktop builds
- The system `PyGitIndex.py` script for documentation navigation; the project tooling locates it automatically or through `PYGITINDEX_PATH`

## Safe return after a break

Start without arguments when returning to the project. The command only displays the complete help map and does not modify files:

```sh
python tools/control.py
```

Then use the recommended sequence:

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
```

The default local endpoints are:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- API health check: `http://127.0.0.1:8000/api/health`

The combined development command runs in the foreground. Press `Ctrl+C` to stop both processes.

## Central commands

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
python tools/control.py stop
python tools/control.py test
python tools/control.py build
python tools/control.py docs
python tools/control.py tauri
python tools/control.py console
```

`build`, `docs`, `test`, and `tauri` display their own command map when called without a subcommand. Every command also supports `--help`.

Examples:

```sh
python tools/control.py test --suite api
python tools/control.py test --suite frontend
python tools/control.py test --suite tools
python tools/control.py test --suite all --report
python tools/control.py build web
python tools/control.py build desktop --dry-run
python tools/control.py docs index --dry-run
python tools/control.py tauri doctor
```

## Interactive console

The guided console is useful when command details are no longer familiar:

```sh
python tools/control.py console
```

It provides dedicated menus for environment setup, development services, tests and reports, web and desktop builds, Tauri workflows, and documentation indexing. Potentially disruptive actions require confirmation; diagnostic and dry-run actions are clearly marked.

See the [Tooling Guide](docs/tools/tooling.md) for the complete command and console reference.

## Project structure

```text
backend/             FastAPI application and API tests
docs/                Documentation rules, templates, architecture, and ATPs
frontend/            Vite and TypeScript application with frontend tests
shared/              Framework-neutral contracts, examples, and shared assets
src-tauri/           Tauri configuration, Rust entry point, and application icons
tools/control.py     Shared project CLI entry point
```

## Create a project from this template

1. Copy the repository or use it as a Git template, then start a new history.
2. Search for `template-project`, `project-template`, `Template Project`, and `com.example.templateproject`; replace them with project-specific values.
3. Replace `src-tauri/app-icon.svg` and generate platform icons with `npm --prefix frontend run tauri -- icon ../src-tauri/app-icon.svg`.
4. Document the product objective, ownership, and quality criteria.
5. Create the first ATP from `docs/atp/ATP-TEMPLATE.md`.
6. Refresh documentation navigation with `python tools/control.py docs index`.
7. Run `python tools/control.py test --suite all` and commit the first completed ATP with the implementation.

## Required documentation

English is the only documentation language for this repository and all projects derived from it.

- [Documentation Standard](docs/README.md)
- [Documentation Template](docs/DOCUMENT-TEMPLATE.md)
- [Framework Architecture](docs/def/architecture.md)
- [ATP Workflow](docs/atp/README.md)
- [ATP Template](docs/atp/ATP-TEMPLATE.md)
- [Tooling Guide](docs/tools/tooling.md)

A new or changed feature is complete only when its code, tests, acceptance evidence, and affected documentation are updated together.
