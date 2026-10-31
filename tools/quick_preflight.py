#!/usr/bin/env python3
"""Read-only, bounded diagnostic for an authorized project worktree.

By default: no network, no disk writes, no environment-variable dumps, no
screenshots, no browser automation, no platform-control inspection. Optional
public GitHub reachability uses a single git ls-remote, not push.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode = True

PUBLIC_REPO = "https://github.com/AgenticLab-SH/sh-workflows.git"
TOOLS = ("git", "codex", "node", "npm")
MANUAL = (
    "Codex /status, /model, and optional Skill availability",
    "Browser editor saved/unsaved indicator and file reconciliation",
    "Built-in Browser preview and expected vs observed behavior",
    "Proctor connection, webcam, screen share, and submission preview",
)


def root_dir(value: str) -> Path:
    p = Path(value).resolve(strict=True)
    if not p.is_dir():
        raise ValueError("root must be an existing directory")
    return p


def tool_presence(which=shutil.which) -> dict[str, dict[str, str]]:
    return {name: {"status": "PASS" if which(name) else "FAIL"}
            for name in TOOLS}


def public_git_readiness(run=subprocess.run, which=shutil.which) -> dict[str, str]:
    """One explicit public-only network read; no fallback or credential output."""
    git = which("git")
    if not git:
        return {"status": "FAIL", "note": "Git binary absent"}
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        p = run([git, "ls-remote", PUBLIC_REPO, "HEAD"],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, timeout=5, env=env,
                check=False)
    except subprocess.TimeoutExpired:
        return {"status": "BLOCKED", "note": "Public read timed out"}
    except (OSError, ValueError):
        return {"status": "BLOCKED", "note": "Git read could not start"}
    if p.returncode == 0 and re.fullmatch(r"[0-9a-f]{40,64}\s+HEAD\s*",
                                           p.stdout.strip()):
        return {"status": "PASS", "note": "Public repository reachable via Git"}
    return {"status": "BLOCKED", "note": "Public read did not succeed; no retry or bypass"}


def safe_project_markers(root: Path) -> dict[str, object]:
    """Check only approved filename markers at the given root; never read data."""
    known = ("README.md", "package.json", "pyproject.toml", "requirements.txt",
             "Cargo.toml", "go.mod")
    present = [name for name in known if (root / name).is_file()
               and not (root / name).is_symlink()]
    skill = root / ".hackathon-kit" / ".agents" / "skills" / "hackathon-task-driver" / "SKILL.md"
    return {"marker_files": present,
            "reference_kit": "PASS" if skill.is_file() and not skill.is_symlink()
            else "NOT_RUN"}


def saved_fingerprint(root: Path, relative: str) -> dict[str, str]:
    """Hash only an explicitly requested non-sensitive saved file in root."""
    # Import the existing safe path validator rather than implement a weaker one.
    try:
        from workspace_probe import file_fingerprint, WorkspaceError
    except ImportError:
        return {"status": "NOT_RUN", "note": "workspace_probe.py absent"}
    try:
        info = file_fingerprint(root, relative)
    except (WorkspaceError, FileNotFoundError, OSError, ValueError):
        return {"status": "BLOCKED", "note": "File not within allowed saved tree"}
    return {"status": "PASS", "relative_path": info["path"],
            "size_bytes": str(info["size_bytes"]),
            "sha256_prefix": info["sha256"][:12]}


def generate(root: Path, check_public_github: bool = False,
             file_path: str | None = None) -> dict[str, object]:
    report: dict[str, object] = {
        "tool": "quick_preflight", "scope": "authorized saved worktree only",
        "python": {"status": "PASS", "version": ".".join(map(str, sys.version_info[:3]))},
        "project": safe_project_markers(root),
        "binaries": tool_presence(),
        "binary_versions": {"status": "NOT_RUN", "note": "No executable launched by default"},
        "local_tests": {"status": "NOT_RUN", "note": "Use only task README test commands"},
        "public_github": ({"status": "NOT_RUN", "note": "Opt in only if current rules permit"}
                          if not check_public_github else public_git_readiness()),
        "saved_fingerprint": ({"status": "NOT_RUN"} if not file_path
                              else saved_fingerprint(root, file_path)),
        "requires_human_ui": [{"task": x, "status": "MANUAL_REQUIRED"} for x in MANUAL],
        "external_upload": "DISABLED", "screen_capture": "DISABLED",
        "file_write": "DISABLED", "codex_update": "DISABLED",
    }
    return report


def render(report: dict[str, object]) -> str:
    project = report["project"]
    binaries = report["binaries"]
    lines = ["=== Authorized Workspace Quick Check ===",
             "Python: PASS " + report["python"]["version"],
             "Project markers: " + (", ".join(project["marker_files"]) or "none at this root"),
             "Public reference kit: " + project["reference_kit"]]
    for name in TOOLS:
        lines.append(f"{name}: {binaries[name]['status']}")
    lines.extend(["Binary versions / project tests: NOT_RUN (not executed)", "Public GitHub read: " + report["public_github"]["status"],
                  "Saved file hash: " + report["saved_fingerprint"]["status"]])
    if report["saved_fingerprint"]["status"] == "PASS":
        lines.append("Saved file SHA256 prefix: " + report["saved_fingerprint"]["sha256_prefix"])
    lines.extend(["Human UI checks: MANUAL_REQUIRED (Codex menus / editor / Browser / Proctor / submission)",
                  "Network upload: DISABLED; screenshot: DISABLED; disk write: DISABLED",
                  "This is not a security, monitoring, permission, or full test audit."])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bounded read-only check for an allowed workspace")
    p.add_argument("--root", default=".", help="Authorized project root (default: current directory)")
    p.add_argument("--check-public-github", action="store_true",
                   help="One optional GitHub ls-remote read; only if the rules allow it")
    p.add_argument("--fingerprint", metavar="RELATIVE_FILE",
                   help="Metadata/hash of one explicitly named saved non-sensitive file")
    p.add_argument("--format", choices=("text", "json"), default="text")
    args = p.parse_args(argv)
    try:
        report = generate(root_dir(args.root), args.check_public_github, args.fingerprint)
    except (OSError, ValueError) as e:
        print("BLOCKED: requested project root is unavailable", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=True) if args.format == "json"
          else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
