"""Offline tests for bounded environment self-check. No real GitHub calls."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from quick_preflight import (generate, main, public_git_readiness, root_dir,
                             safe_project_markers, saved_fingerprint, tool_presence)


class FakeProc:
    returncode = 0
    stdout = "a" * 40 + "\tHEAD\n"
    stderr = ""


class ReadinessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "safe"
        self.root.mkdir()
        (self.root / "README.md").write_text("safe synthetic text", encoding="utf-8")
        (self.root / ".env").write_text("SECRET=something", encoding="utf-8")

    def test_root_and_marker_only(self):
        self.assertEqual(root_dir(str(self.root)), self.root)
        p = safe_project_markers(self.root)
        self.assertEqual(p["marker_files"], ["README.md"])
        self.assertNotIn("SECRET", json.dumps(p))

    def test_default_has_no_public_network(self):
        with patch("quick_preflight.public_git_readiness", side_effect=AssertionError("network!")):
            out = generate(self.root)
        self.assertEqual(out["public_github"]["status"], "NOT_RUN")
        self.assertEqual(out["file_write"], "DISABLED")
        self.assertEqual(out["screen_capture"], "DISABLED")
        self.assertEqual(out["external_upload"], "DISABLED")
        self.assertEqual(len(out["requires_human_ui"]), 4)
        self.assertNotIn("SECRET", json.dumps(out))

    def test_no_credentials_or_command_injection_in_network_check(self):
        calls = []
        def run(args, **kwargs):
            calls.append((args, kwargs))
            return FakeProc()
        result = public_git_readiness(run=run, which=lambda _: "/usr/bin/git")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0][1], "ls-remote")
        self.assertIn("ai-hackathon-prep-kit", calls[0][0][2])
        self.assertEqual(calls[0][1]["timeout"], 5)
        self.assertEqual(calls[0][1]["env"]["GIT_TERMINAL_PROMPT"], "0")
        self.assertNotIn("SECRET", json.dumps(result))

    def test_timeout_does_not_retry(self):
        attempts = []
        def delayed(*args, **kwargs):
            attempts.append(1)
            raise subprocess.TimeoutExpired("git", 5)
        r = public_git_readiness(run=delayed, which=lambda _: "/usr/bin/git")
        self.assertEqual(r["status"], "TIMEOUT")
        self.assertEqual(len(attempts), 1)

    def test_missing_git_never_calls_network(self):
        r = public_git_readiness(run=lambda *a, **kw: self.fail("network"), which=lambda _: None)
        self.assertEqual(r["status"], "NOT_FOUND")

    def test_saved_file_invalid_without_workspace_probe(self):
        with patch.dict(sys.modules, {"workspace_probe": None}):
            out = saved_fingerprint(self.root, "README.md")
        self.assertEqual(out["status"], "NOT_AVAILABLE")

    def test_python_binary_and_cli(self):
        with patch("quick_preflight.tool_presence", return_value={k:{"status":"NOT_FOUND"} for k in ("git","codex","node","npm")}):
            report = generate(self.root)
        self.assertEqual(report["binaries"]["codex"]["status"], "NOT_FOUND")
        self.assertEqual(main(["--root", str(self.root), "--format", "json"]), 0)


if __name__ == "__main__":
    unittest.main()
