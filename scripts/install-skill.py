#!/usr/bin/env python3
"""Install the FreeCAD Modeling skill into common agent skill directories."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_NAME = "freecad-modeling"

AGENT_CHOICES = (
    "codex",
    "claude",
    "gemini",
    "openclaw",
    "cursor",
    "vscode",
    "goose",
    "project",
    "all",
)

ALL_AGENT_TARGETS = (
    "codex",
    "claude",
    "gemini",
    "openclaw",
    "cursor",
    "vscode",
    "goose",
    "project",
)

EXCLUDED_NAMES = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "coverage",
    "dist",
    "dist-verify",
    "htmlcov",
    "node_modules",
    ".claude",
    ".cursor",
    ".gemini",
    ".skills",
}

EXCLUDED_SUFFIXES = (".pyc", ".pyo")


@dataclass(frozen=True)
class AgentTarget:
    name: str
    label: str
    destination: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_user_path(raw_path: str | Path) -> Path:
    return Path(raw_path).expanduser().resolve()


def path_from_env(env_name: str, default: str) -> Path:
    value = os.environ.get(env_name) or default
    return resolve_user_path(value)


def codex_destination() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return resolve_user_path(Path(codex_home) / "skills")
    return resolve_user_path(Path.home() / ".codex" / "skills")


def agent_target(agent: str) -> AgentTarget:
    destinations = {
        "codex": AgentTarget("codex", "OpenAI Codex", codex_destination()),
        "claude": AgentTarget(
            "claude",
            "Claude Code",
            path_from_env("CLAUDE_SKILLS_DIR", "~/.claude/skills"),
        ),
        "gemini": AgentTarget(
            "gemini",
            "Gemini CLI",
            path_from_env("GEMINI_SKILLS_DIR", ".gemini/skills"),
        ),
        "openclaw": AgentTarget(
            "openclaw",
            "OpenClaw",
            path_from_env("OPENCLAW_SKILLS_DIR", "~/.openclaw/skills"),
        ),
        "cursor": AgentTarget(
            "cursor",
            "Cursor",
            path_from_env("CURSOR_SKILLS_DIR", ".cursor/skills"),
        ),
        "vscode": AgentTarget(
            "vscode",
            "VS Code / Copilot",
            path_from_env("VSCODE_SKILLS_DIR", ".github/skills"),
        ),
        "goose": AgentTarget(
            "goose",
            "Goose",
            path_from_env("GOOSE_SKILLS_DIR", "~/.config/goose/skills"),
        ),
        "project": AgentTarget(
            "project",
            "Generic project",
            path_from_env("PROJECT_SKILLS_DIR", ".skills"),
        ),
    }
    return destinations[agent]


def ignored_copy_names(_directory: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        if name in EXCLUDED_NAMES or name.endswith(EXCLUDED_SUFFIXES):
            ignored.add(name)
    return ignored


def remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def install_skill(target: AgentTarget, *, dry_run: bool, force: bool, link: bool) -> str:
    source = repo_root()
    destination = target.destination / SKILL_NAME
    action = "link" if link else "copy"

    if destination.exists() or destination.is_symlink():
        try:
            same_path = destination.resolve() == source.resolve()
        except OSError:
            same_path = False
        if same_path:
            return f"skip {SKILL_NAME}: already points at {source}"
        if not force:
            return f"skip {SKILL_NAME}: {destination} already exists"
        if dry_run:
            return f"would replace {destination} and {action} {source}"
        remove_existing(destination)

    if dry_run:
        return f"would {action} {source} -> {destination}"

    destination.parent.mkdir(parents=True, exist_ok=True)
    if link:
        destination.symlink_to(source.resolve(), target_is_directory=True)
    else:
        shutil.copytree(
            source,
            destination,
            ignore=ignored_copy_names,
            symlinks=True,
        )
    completed_action = "linked" if link else "copied"
    return f"{completed_action} {SKILL_NAME} -> {destination}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the FreeCAD Modeling skill into a supported agent.",
    )
    parser.add_argument(
        "--agent",
        choices=AGENT_CHOICES,
        help="Target agent or 'all' for every supported target.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files.")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill folder.")
    parser.add_argument("--link", action="store_true", help="Symlink the skill instead of copying it.")
    args = parser.parse_args(argv)
    if not args.agent:
        parser.error("--agent is required")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    agent_names = ALL_AGENT_TARGETS if args.agent == "all" else (args.agent,)
    targets = [agent_target(agent) for agent in agent_names]

    for target in targets:
        print(f"{target.label}: {target.destination}")
        print(
            f"  {install_skill(target, dry_run=args.dry_run, force=args.force, link=args.link)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
