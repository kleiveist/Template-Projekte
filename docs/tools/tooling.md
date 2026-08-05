<!-- AUTO-GENERATED:backlink START -->
[← Back](tools.md)
<!-- AUTO-GENERATED:backlink END -->
# Tooling Guide

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-05 |
| Audience | Contributors and release operators |
| Related ATP | N/A — template-level tooling reference |

## Purpose

This guide explains the central entry point for setup, development, testing, builds, Tauri, and documentation maintenance. It is designed for contributors returning after a long break as well as first-time users of the template.

## Scope

The guide covers `tools/control.py`, the interactive console, and all web, API, desktop, test-report, and PyGitIndex workflows exposed through that command. Run every example from the repository root.

## Safe return after a break

A command without arguments displays help and does not modify files:

```sh
python tools/control.py
```

Use this sequence to restore context and prepare the environment:

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
```

`doctor` checks runtimes, dependencies, project structure, and ports. `install` prepares the frontend and backend; it installs Playwright only when E2E tests are configured. `run` starts Vite and FastAPI together. In foreground mode, `Ctrl+C` stops both processes.

## Command map

| Command | Effect | Detailed help |
| --- | --- | --- |
| `doctor` | Inspect the development environment | `python tools/control.py doctor --help` |
| `install` | Install or repair project dependencies | `python tools/control.py install --help` |
| `console` | Open the guided interactive interface | `python tools/control.py console --help` |
| `run` | Start the frontend and backend | `python tools/control.py run --help` |
| `stop` | Stop tracked development services | `python tools/control.py stop --help` |
| `test` | Select test suites and reports | `python tools/control.py test` |
| `build` | Select a web or desktop build | `python tools/control.py build` |
| `docs` | Maintain navigation with PyGitIndex | `python tools/control.py docs` |
| `tauri` | Manage desktop diagnostics, development, and artifacts | `python tools/control.py tauri` |

Group commands display the next level of help when called without an action:

```sh
python tools/control.py build
python tools/control.py docs
python tools/control.py test
python tools/control.py tauri
```

An unknown command displays the relevant help map, explains the error, and provides the next `--help` command.

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
# Foreground; Ctrl+C stops both services
python tools/control.py run

# Background; PID and log files are stored under tools/.runtime
python tools/control.py run --detach

# Stop background services
python tools/control.py stop
```

Use `--frontend-port` and `--backend-port` for non-default ports. Run `python tools/control.py run --help` for every option.

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
| `frontend` | Vitest tests |
| `e2e` | Playwright tests when configured |
| `tools` | Project CLI and Tauri helper tests |
| `all` | Every configured suite |

Reports are written under `.report/`. `python tools/control.py test --report done` removes only that generated report directory.

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
```

Platform strategies and bundle options are documented by:

```sh
python tools/control.py build desktop --help
python tools/control.py tauri build --help
```

The Tauri map also provides prerequisite setup, development mode, local AppImage installation, validation, and artifact collection.

## Documentation indexing with PyGitIndex

Preview index and backlink changes before writing:

```sh
python tools/control.py docs index --dry-run
```

Apply the update after adding, moving, renaming, or deleting Markdown files:

```sh
python tools/control.py docs index
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

Do not manually edit blocks between `AUTO-GENERATED` markers.

## Troubleshooting

1. Repeat the failed command with `--help`.
2. Run `python tools/control.py doctor`.
3. Repair project dependencies with `python tools/control.py install`.
4. For desktop problems, also run `python tools/control.py tauri doctor`.
5. For indexing problems, run `python tools/control.py docs index --dry-run --script <path>`.
6. Rerun only the affected test suite, then run `--suite all` before hand-off.

Missing optional suites are reported as `WARN` during `test --suite all`. Missing optional accelerators such as `uv` do not reduce the Doctor status. A `FAIL` means the selected workflow did not complete successfully.

## Verification

After a tooling change, run at least:

```sh
python tools/control.py
python tools/control.py build
python tools/control.py docs
python tools/control.py test
python tools/control.py tauri
python tools/control.py docs index --dry-run
python tools/control.py test --suite tools
python tools/control.py build desktop --dry-run --no-clean
```

## Related documents

- [Documentation Standard](../README.md)
- [Framework Architecture](../def/architecture.md)
- [ATP Workflow](../atp/README.md)
