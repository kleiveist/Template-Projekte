from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import process


def test_prepare_command_keeps_native_executable(monkeypatch) -> None:
    monkeypatch.setattr(process.sys, "platform", "win32")

    command = [r"C:\Python311\python.exe", "--version"]

    assert process.prepare_command(command) is command


def test_prepare_command_routes_windows_batch_launcher_through_comspec(monkeypatch) -> None:
    monkeypatch.setattr(process.sys, "platform", "win32")
    monkeypatch.setenv("COMSPEC", r"C:\Windows\System32\cmd.exe")

    prepared = process.prepare_command([r"C:\Program Files\nodejs\npm.cmd", "ci", "--no-audit"])

    assert prepared == [
        r"C:\Windows\System32\cmd.exe",
        "/d",
        "/s",
        "/c",
        "call",
        r"C:\Program Files\nodejs\npm.cmd",
        "ci",
        "--no-audit",
    ]


@pytest.mark.skipif(sys.platform != "win32", reason="requires the Windows command interpreter")
def test_prepare_command_executes_batch_launcher_with_spaced_path_and_arguments(tmp_path: Path) -> None:
    launcher_dir = tmp_path / "launcher path with spaces"
    launcher_dir.mkdir()
    launcher = launcher_dir / "argument probe.cmd"
    launcher.write_text('@echo off\r\n<nul set /p "=[%~1]|[%~2]"\r\n', encoding="utf-8")

    completed = subprocess.run(
        process.prepare_command([str(launcher), "first value", "second value"]),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == "[first value]|[second value]"
