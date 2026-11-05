"""Offline synthetic checks of method choice and its independent evidence."""
import importlib.util
from pathlib import Path
import random
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("method_trace", ROOT / "examples" / "method_trace.py")
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class MethodTraceTest(unittest.TestCase):
    def test_counterexample_witness_and_boundary_cases(self):
        report = trace.run()
        self.assertTrue(report["passed"])
        main = report["cases"][0]
        self.assertEqual(main["baseline"]["ids"], ["A", "B"])
        self.assertEqual(main["baseline"]["objective"], 160)
        self.assertEqual(main["dp"]["ids"], ["B", "C"])
        self.assertEqual((main["dp"]["used"], main["dp"]["objective"]), (50, 220))
        self.assertEqual(main["gap_to_baseline"], 60)
        by_name = {case["case"]: case for case in report["cases"]}
        self.assertEqual(by_name["changed_budget"]["dp"]["objective"], 160)
        self.assertEqual(by_name["zero_cost"]["dp"]["objective"], 5)
        self.assertIn("learner_explanation", report["not_run"])

    def test_dp_matches_independent_subsets_on_small_changed_inputs(self):
        rng = random.Random(93)
        for _ in range(40):
            n = rng.randrange(0, 9)
            values = [rng.randrange(-3, 25) for _ in range(n)]
            costs = [rng.randrange(0, 12) for _ in range(n)]
            capacity = rng.randrange(0, 25)
            case = trace.compare_case("generated", values, costs, capacity)
            self.assertTrue(case["passed"], case)

    def test_invalid_units_and_resource_limit_are_rejections(self):
        report = trace.run()
        self.assertEqual(len(report["rejections"]), 3)
        self.assertTrue(all(row["rejected"] for row in report["rejections"]))
        with self.assertRaises(ValueError):
            trace.enumerate_best([1] * 13, [1] * 13, 5)


if __name__ == "__main__":
    unittest.main()
