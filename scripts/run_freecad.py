#!/usr/bin/env python3
"""Run a FreeCAD Python script through FreeCADCmd with consistent discovery."""

from __future__ import annotations

import argparse
import json
import os
import reprlib
import shutil
import subprocess
import sys
from pathlib import Path


WINDOWS_CANDIDATES = (
    r"E:\FreeCAD\bin\freecadcmd.exe",
    r"C:\Program Files\FreeCAD\bin\FreeCADCmd.exe",
    r"C:\Program Files\FreeCAD 1.0\bin\FreeCADCmd.exe",
    r"C:\Program Files\FreeCAD 0.21\bin\FreeCADCmd.exe",
)


def _is_executable(path: Path) -> bool:
    return path.is_file()


def _glob_program_files() -> list[Path]:
    candidates: list[Path] = []
    roots = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
    ]
    for root in roots:
        if not root:
            continue
        root_path = Path(root)
        for pattern in ("FreeCAD*", "FreeCAD */"):
            for install_dir in root_path.glob(pattern):
                candidates.append(install_dir / "bin" / "FreeCADCmd.exe")
                candidates.append(install_dir / "bin" / "freecadcmd.exe")
    return candidates


def find_freecadcmd(explicit: str | None = None) -> Path | None:
    candidates: list[Path] = []

    if explicit:
        candidates.append(Path(explicit).expanduser())

    for env_name in ("FREECADCMD", "FREECAD_CMD", "FREECADCMD_PATH"):
        env_value = os.environ.get(env_name)
        if env_value:
            candidates.append(Path(env_value).expanduser())

    for binary_name in ("FreeCADCmd", "freecadcmd", "FreeCADCmd.exe", "freecadcmd.exe"):
        resolved = shutil.which(binary_name)
        if resolved:
            candidates.append(Path(resolved))

    candidates.extend(Path(raw) for raw in WINDOWS_CANDIDATES)
    candidates.extend(_glob_program_files())

    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.resolve() if candidate.exists() else candidate
        key = str(resolved).casefold()
        if key in seen:
            continue
        seen.add(key)
        if _is_executable(resolved):
            return resolved
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", help="FreeCAD Python script to execute.")
    parser.add_argument("--freecadcmd", help="Path to FreeCADCmd executable.")
    parser.add_argument(
        "--cwd",
        help="Working directory for FreeCADCmd. Defaults to the current directory.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Execution timeout in seconds. Defaults to 300.",
    )
    parser.add_argument("--json", action="store_true", help="Print structured JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, script_args = parser.parse_known_args(argv)
    if script_args and script_args[0] == "--":
        script_args = script_args[1:]

    script_path = Path(args.script).expanduser()
    if not script_path.is_file():
        message = f"FreeCAD script not found: {script_path}"
        if args.json:
            print(json.dumps({"ok": False, "error": message}, indent=2))
        else:
            print(message, file=sys.stderr)
        return 2

    freecadcmd = find_freecadcmd(args.freecadcmd)
    if freecadcmd is None:
        message = (
            "FreeCADCmd was not found. Set FREECADCMD or pass --freecadcmd "
            "with the path to FreeCADCmd."
        )
        if args.json:
            print(json.dumps({"ok": False, "error": message}, indent=2))
        else:
            print(message, file=sys.stderr)
        return 2

    cwd = Path(args.cwd).expanduser() if args.cwd else Path.cwd()
    script_abspath = script_path.resolve()
    script_argv = [str(script_abspath), *script_args]
    bootstrap_body = (
        "import runpy, sys, traceback\n"
        f"sys.argv = {script_argv!r}\n"
        "try:\n"
        f"    runpy.run_path({str(script_abspath)!r}, run_name='__main__')\n"
        "except SystemExit:\n"
        "    raise\n"
        "except BaseException:\n"
        "    traceback.print_exc()\n"
        "    raise SystemExit(1)\n"
        "raise SystemExit(0)\n"
    )
    bootstrap = f"exec({bootstrap_body!r})\n"
    command = [str(freecadcmd), "-c"]
    display_command = [*command, f"<runpy {reprlib.repr(str(script_abspath))}>"]

    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            input=bootstrap,
            capture_output=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        payload = {
            "ok": False,
            "returncode": None,
            "timeout": args.timeout,
            "command": display_command,
            "script": str(script_abspath),
            "script_args": script_args,
            "cwd": str(cwd),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "error": "FreeCADCmd timed out.",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(payload["error"], file=sys.stderr)
            if payload["stdout"]:
                print(payload["stdout"])
            if payload["stderr"]:
                print(payload["stderr"], file=sys.stderr)
        return 124

    payload = {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command": display_command,
        "script": str(script_abspath),
        "script_args": script_args,
        "cwd": str(cwd),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
