"""Optional integration tests; skipped by the stdlib suite without the reviewed OSS."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
try:
    AVAILABLE = importlib.metadata.version("hypothesis") == "6.170.14"
except importlib.metadata.PackageNotFoundError:
    AVAILABLE = False


@unittest.skipUnless(AVAILABLE, "optional reviewed Hypothesis venv not active")
class PropertyIntegrationTest(unittest.TestCase):
    def test_existing_entrypoint_end_to_end_and_repeat(self):
        results = []
        for _ in range(2):
            child = subprocess.run([sys.executable, "-B", "examples/method_trace.py", "--property-checks"],
                                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(child.returncode, 0, child.stderr or child.stdout)
            output = json.loads(child.stdout)
            self.assertTrue(output["passed"])
            result = output["property_checks"]
            self.assertTrue(all(count == 60 for count in result["properties"].values()))
            witness = result["counterexample"]
            self.assertGreater(witness["gap_to_baseline"], 0)
            self.assertEqual(witness["dp"]["objective"], witness["enumerated_optimum"])
            self.assertEqual(result["trace"]["learner_explanation"], "NOT_RUN; no user answer generated")
            results.append((witness["values"], witness["costs"], witness["budget"]))
        self.assertEqual(results[0], results[1])

    def test_observability_environment_is_rejected(self):
        env = {**os.environ, "HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY": "1"}
        child = subprocess.run([sys.executable, "-B", "examples/method_trace.py", "--property-checks"],
                               cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual(child.returncode, 2)
        self.assertFalse(json.loads(child.stdout)["passed"])

    def test_unreviewed_dependency_version_is_rejected(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from property_checks import verify_dependencies
        with patch("property_checks.version", return_value="0.0.0"):
            with self.assertRaisesRegex(RuntimeError, "reviewed lock"):
                verify_dependencies()
    def test_network_and_subprocess_attempts_are_rejected(self):
        code = """
import sys, socket, subprocess
sys.path.insert(0, 'tools')
from property_checks import install_runtime_guard
install_runtime_guard()
rejections = 0
for operation in (lambda: socket.socket(), lambda: subprocess.run([sys.executable, '-V'])):
    try:
        operation()
    except PermissionError:
        rejections += 1
assert rejections == 2
"""
        child = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT,
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(child.returncode, 0, child.stderr)


if __name__ == "__main__":
    unittest.main()
