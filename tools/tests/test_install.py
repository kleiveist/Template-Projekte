from __future__ import annotations

import subprocess
from pathlib import Path

from tools.inst import install


def test_frontend_install_uses_npm_ci_when_lockfile_exists(monkeypatch, tmp_path: Path) -> None:
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text("{}\n", encoding="utf-8")
    (frontend / "package-lock.json").write_text("{}\n", encoding="utf-8")
    calls: list[tuple[list[str], Path | None]] = []

    monkeypatch.setattr(install, "ROOT", tmp_path)
    monkeypatch.setattr(install.shutil, "which", lambda name: "/usr/bin/npm" if name == "npm" else None)
    monkeypatch.setattr(
        install,
        "_run",
        lambda command, cwd=None: calls.append((command, cwd))
        or subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    result = install._install_frontend()

    assert result.status == "OK"
    assert calls == [(["/usr/bin/npm", "ci", "--no-audit", "--no-fund"], frontend)]


def test_frontend_install_falls_back_without_lockfile(monkeypatch, tmp_path: Path) -> None:
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text("{}\n", encoding="utf-8")
    calls: list[list[str]] = []

    monkeypatch.setattr(install, "ROOT", tmp_path)
    monkeypatch.setattr(install.shutil, "which", lambda name: "/usr/bin/npm" if name == "npm" else None)
    monkeypatch.setattr(
        install,
        "_run",
        lambda command, cwd=None: calls.append(command)
        or subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    assert install._install_frontend().status == "OK"
    assert calls[0][1] == "install"
