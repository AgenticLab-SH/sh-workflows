"""Synthetic subprocess checks: stdout-only, no default network or writes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PreflightSafetyTest(unittest.TestCase):
    def test_cli_fingerprint_no_writes_and_no_private_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("synthetic", encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "tools/quick_preflight.py"),
                 "--root", str(root), "--fingerprint", "README.md", "--format", "json"],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["saved_fingerprint"]["status"], "PASS")
            self.assertEqual(report["public_github"]["status"], "NOT_RUN")
            self.assertNotIn(str(root), result.stdout + result.stderr)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_invalid_root_redacts_path(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools/quick_preflight.py"),
             "--root", str(ROOT / "missing-private-path")],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("BLOCKED", result.stderr)
        self.assertNotIn("missing-private-path", result.stderr)

    def test_auth_and_hidden_file_blocked(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from workspace_probe import file_fingerprint, WorkspaceError
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("auth.json", ".private"):
                (root / name).write_text("synthetic-secret", encoding="utf-8")
                with self.assertRaises(WorkspaceError):
                    file_fingerprint(root, name)
