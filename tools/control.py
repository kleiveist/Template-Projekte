#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import logger
from tools.inst import build, console, doctor, install, run, run_test, stop
from tools.tauri import build as tauri_build
from tools.tauri import control as tauri_control

Handler = Callable[[argparse.Namespace], int]


class HelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=30, width=100)


class ControlParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_help(sys.stderr)
        print(file=sys.stderr)
        logger.fail(f"{self.prog}: {message}", stream=sys.stderr)
        logger.info(f"Next step: {self.prog} --help", stream=sys.stderr)
        self.exit(2)


COMMAND_ALIASES: dict[str, str] = {
    "--doctor": "doctor",
    "--install": "install",
    "--run": "run",
    "--stop": "stop",
    "--test": "test",
}

TAURI_COMMAND_ALIASES: dict[str, str] = {
    "--doctor": "doctor",
    "--install": "install",
    "--run": "run",
    "--build": "build",
    "--install-appimage": "install-appimage",
    "--test": "test",
    "--copy": "copy",
}

ROOT_HELP = """
One entry point for the complete project lifecycle.

Recommended workflow after returning to the project:
  1. doctor   Check tools, dependencies and occupied ports.
  2. install  Install or repair frontend, backend and optional test dependencies.
  3. run      Start the web frontend and API.
  4. test     Select and run the relevant quality checks.
  5. build    Choose a web or desktop release.

Prefer a menu? Start the optional interactive console:
  python tools/control.py console

Groups with their own command maps:
  python tools/control.py build
  python tools/control.py tauri
"""

ROOT_EXAMPLES = """
examples:
  python tools/control.py doctor
  python tools/control.py install
  python tools/control.py run --detach
  python tools/control.py stop
  python tools/control.py test --suite all --report
  python tools/control.py build web
  python tools/control.py tauri

Compatibility:
  The former aliases --doctor, --install, --run, --stop, --test and --build remain available.
"""


def _normalize_argv(argv: list[str] | None) -> list[str]:
    normalized = list(sys.argv[1:] if argv is None else argv)
    if not normalized:
        return normalized

    first = normalized[0].lower()
    if first == "--build":
        if len(normalized) >= 2 and normalized[1].lower() == "--desktop":
            return ["build", "desktop", *normalized[2:]]
        return ["build", "web", *normalized[1:]]

    if len(normalized) >= 2 and first == "tauri":
        tauri_alias = TAURI_COMMAND_ALIASES.get(normalized[1].lower())
        if tauri_alias:
            normalized[1] = tauri_alias
            return normalized

    alias = COMMAND_ALIASES.get(first)
    if alias:
        show_test_guide = first == "--test" and len(normalized) == 1
        normalized[0] = alias
        if show_test_guide:
            normalized.append("--suite-help")
    return normalized


def _add_examples(parser: argparse.ArgumentParser, examples: str) -> None:
    parser.epilog = examples.strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = ControlParser(
        prog="python tools/control.py",
        description=ROOT_HELP.strip(),
        epilog=ROOT_EXAMPLES.strip(),
        formatter_class=HelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="command map",
        metavar="<command>",
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="inspect the development environment",
        description="Inspect runtimes, dependencies, project files and local ports without changing them.",
        formatter_class=HelpFormatter,
    )
    doctor_parser.add_argument("--watch", action="store_true", help="repeat checks until interrupted")
    doctor_parser.add_argument("--interval", type=int, default=5, help="seconds between watch checks (default: 5)")
    _add_examples(
        doctor_parser,
        """examples:
  python tools/control.py doctor
  python tools/control.py doctor --watch --interval 10""",
    )

    install_parser = subparsers.add_parser(
        "install",
        help="install or repair project dependencies",
        description="Prepare the local frontend, backend and optional E2E environment.",
        formatter_class=HelpFormatter,
    )
    install_parser.add_argument("--skip-frontend", action="store_true", help="do not run npm install")
    install_parser.add_argument("--skip-backend", action="store_true", help="do not prepare the Python venv")
    install_parser.add_argument("--skip-playwright", action="store_true", help="do not install Playwright Chromium")
    _add_examples(
        install_parser,
        """examples:
  python tools/control.py install
  python tools/control.py install --skip-playwright
  python tools/control.py install --skip-frontend""",
    )

    console_parser = subparsers.add_parser(
        "console",
        help="open an interactive menu for common tasks",
        description="Open a numbered menu that guides you through common project actions.",
        formatter_class=HelpFormatter,
    )
    _add_examples(console_parser, "example:\n  python tools/control.py console")

    build_parser = subparsers.add_parser(
        "build",
        help="choose a web or desktop release",
        description="Build map. Choose one target; a bare 'build' only shows this guide.",
        formatter_class=HelpFormatter,
    )
    build_parser.set_defaults(build_parser=build_parser)
    build_subparsers = build_parser.add_subparsers(
        dest="build_command",
        title="build targets",
        metavar="<target>",
    )
    web_parser = build_subparsers.add_parser(
        "web",
        help="compile and package the Vite web app",
        description="Build frontend/dist and create .dist/web/template-project-web.zip.",
        formatter_class=HelpFormatter,
    )
    _add_examples(web_parser, "examples:\n  python tools/control.py build web")
    desktop_parser = build_subparsers.add_parser(
        "desktop",
        help="build Tauri desktop artifacts",
        description="Build native desktop artifacts through the restored Tauri tooling.",
        formatter_class=HelpFormatter,
    )
    tauri_control.configure_build_parser(desktop_parser)
    _add_examples(
        desktop_parser,
        """examples:
  python tools/control.py build desktop --dry-run
  python tools/control.py build desktop --target linux --bundles deb,rpm
  python tools/control.py build desktop --target windows-portable""",
    )
    _add_examples(
        build_parser,
        """examples:
  python tools/control.py build web
  python tools/control.py build desktop --dry-run

More desktop commands:
  python tools/control.py tauri""",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="start frontend and backend services",
        description="Start Vite and FastAPI together. Foreground is the default; Ctrl+C stops both.",
        formatter_class=HelpFormatter,
    )
    run_parser.add_argument("--frontend-port", type=int, default=5173, help="Vite port (default: 5173)")
    run_parser.add_argument("--backend-port", type=int, default=8000, help="FastAPI port (default: 8000)")
    run_parser.add_argument("--detach", action="store_true", help="run in background and write logs to tools/.runtime")
    _add_examples(
        run_parser,
        """examples:
  python tools/control.py run
  python tools/control.py run --detach
  python tools/control.py stop""",
    )

    stop_parser = subparsers.add_parser(
        "stop",
        help="stop tracked development services",
        description="Stop services recorded by detached runs and optionally clean stale project ports.",
        formatter_class=HelpFormatter,
    )
    stop_parser.add_argument("--frontend-port", type=int, default=5173, help="frontend cleanup port (default: 5173)")
    stop_parser.add_argument("--backend-port", type=int, default=8000, help="backend cleanup port (default: 8000)")
    stop_parser.add_argument("--tracked-only", action="store_true", help="do not inspect stale listeners")
    _add_examples(stop_parser, "examples:\n  python tools/control.py stop\n  python tools/control.py stop --tracked-only")

    test_parser = subparsers.add_parser(
        "test",
        help="select test suites and optional reports",
        description="Test map. A bare 'test' shows this guide and does not run every suite unexpectedly.",
        formatter_class=HelpFormatter,
    )
    test_parser.set_defaults(test_parser=test_parser)
    test_parser.add_argument(
        "--suite",
        choices=["api", "schema", "frontend", "e2e", "tools", "all"],
        default=None,
        help="suite to run; use all for the complete configured set",
    )
    test_parser.add_argument("--no-start", action="store_true", help="do not start services for E2E tests")
    test_parser.add_argument(
        "--report",
        nargs="?",
        const="md",
        choices=["md", "markdown", "json", "all", "done"],
        help="write a report, or use '--report done' to remove .report",
    )
    test_parser.add_argument("--suite-help", action="store_true", help=argparse.SUPPRESS)
    _add_examples(
        test_parser,
        """suites:
  api       FastAPI tests
  schema    shared JSON Schema examples (skipped until configured)
  frontend  Vitest tests
  e2e       Playwright tests (skipped until configured)
  tools     restored Python tooling tests
  all       every configured suite

examples:
  python tools/control.py test --suite tools
  python tools/control.py test --suite all --report
  python tools/control.py test --report done""",
    )

    tauri_parser = subparsers.add_parser(
        "tauri",
        help="open the Tauri desktop command map",
        description="Tauri-specific diagnostics, setup, development, builds and artifact handling.",
        formatter_class=HelpFormatter,
    )
    tauri_control.configure_parser(tauri_parser)

    return parser


def _handle_build(args: argparse.Namespace) -> int:
    if getattr(args, "build_command", None) is None:
        args.build_parser.print_help()
        return 0
    if args.build_command == "web":
        return build.main(args)
    if args.build_command == "desktop":
        return tauri_build.main(args)
    logger.fail(f"Unknown build target: {args.build_command}")
    return 2


def _handle_test(args: argparse.Namespace) -> int:
    if args.report == "done":
        return run_test.main(args)
    if args.suite is None and not args.suite_help:
        args.test_parser.print_help()
        return 0
    if args.suite is None:
        args.suite = "all"
    return run_test.main(args)


def _handle_console(_args: argparse.Namespace) -> int:
    return console.main()


def _handlers() -> dict[str, Handler]:
    return {
        "doctor": doctor.main,
        "install": install.main,
        "console": _handle_console,
        "build": _handle_build,
        "run": run.run_command,
        "stop": stop.main,
        "test": _handle_test,
        "tauri": tauri_control.main,
    }


def main(argv: list[str] | None = None) -> int:
    normalized_argv = _normalize_argv(argv)
    parser = _build_parser()
    args = parser.parse_args(normalized_argv)
    if args.command is None:
        parser.print_help()
        return 0

    args.display_argv = list(sys.argv[1:] if argv is None else argv)
    handler = _handlers().get(args.command)
    if handler is None:
        logger.fail(f"Unknown command: {args.command}")
        logger.info(f"Next step: {parser.prog} --help")
        return 2

    try:
        code = handler(args)
        return 0 if code is None else int(code)
    except KeyboardInterrupt:
        logger.warn("Interrupted by user")
        return 130
    except Exception as exc:  # pragma: no cover
        logger.fail(f"Unhandled error: {exc}")
        for line in traceback.format_exc().strip().splitlines():
            logger.info(line)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
