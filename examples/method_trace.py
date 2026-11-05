#!/usr/bin/env python3
"""Synthetic method-to-evidence rehearsal; no network or input files.

Default mode writes no files. Optional property checks use an ignored local cache.

Reuses the existing opt_kit budget demo. Business rules below are authored
practice assumptions, not stakeholder answers or rules for a real assessment.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from opt_kit import InputError, greedy_knapsack, knapsack_01

ITEM_IDS = ["A", "B", "C"]
VALUES = [60, 100, 120]
COSTS = [10, 20, 30]
BUDGET = 50


def enumerate_best(values, costs, budget):
    """Independent small oracle: inspect every subset, not the DP recurrence."""
    if len(values) > 12:
        raise ValueError("practice oracle supports at most 12 items")
    best = 0
    for bits in itertools.product((0, 1), repeat=len(values)):
        used = sum(c * b for c, b in zip(costs, bits))
        if used <= budget:
            best = max(best, sum(v * b for v, b in zip(values, bits)))
    return best


def compare_case(name, values, costs, budget):
    """Same input for baseline, existing DP and independent enumeration."""
    result = {"case": name, "budget": budget, "items": len(values)}
    for label, method in (("baseline", greedy_knapsack), ("dp", knapsack_01)):
        start = perf_counter()
        objective, chosen = method(values, costs, budget)
        elapsed_ms = (perf_counter() - start) * 1000
        cost = sum(costs[i] for i in chosen)
        violations = int(cost > budget) + int(len(chosen) != len(set(chosen)))
        violations += int(objective != sum(values[i] for i in chosen))
        result[label] = {"objective": objective, "indices": chosen,
                         "used": cost, "violations": violations,
                         "elapsed_ms": round(elapsed_ms, 6)}
    result["enumerated_optimum"] = enumerate_best(values, costs, budget)
    result["gap_to_baseline"] = result["dp"]["objective"] - result["baseline"]["objective"]
    result["passed"] = (
        result["dp"]["objective"] == result["enumerated_optimum"]
        and result["baseline"]["objective"] <= result["enumerated_optimum"]
        and result["baseline"]["violations"] == result["dp"]["violations"] == 0
    )
    return result


def run():
    cases = [
        ("ratio_counterexample", VALUES, COSTS, BUDGET),
        ("changed_budget", VALUES, COSTS, 30),
        ("zero_budget", VALUES, COSTS, 0),
        ("no_items", [], [], 50),
        ("nothing_fits", [8], [51], 50),
        ("tied_optimum", [5, 5], [1, 1], 1),
        ("zero_cost", [5, 6], [0, 1], 0),
        ("negative_value", [-5, 6], [0, 1], 1),
    ]
    compared = [compare_case(*case) for case in cases]
    rejected = []
    for name, values, costs, budget in [
        ("fractional_cost", [1], [1.5], 2),
        ("negative_cost", [1], [-1], 2),
        ("table_limit", [1], [1], 5_000_001),
    ]:
        try:
            knapsack_01(values, costs, budget)
        except InputError as exc:
            rejected.append({"case": name, "rejected": True, "reason": str(exc)})
        else:
            rejected.append({"case": name, "rejected": False})
    main = compared[0]
    for method in ("baseline", "dp"):
        main[method]["ids"] = [ITEM_IDS[i] for i in main[method]["indices"]]
    return {
        "scope": "synthetic; authored assumptions; no user Q&A performed",
        "policy": {"indivisible": True, "one_each": True, "additive_value": True,
                   "budget_inclusive": True, "mandatory_items": [],
                   "equal_objective": "any optimal subset"},
        "cases": compared,
        "rejections": rejected,
        "passed": all(c["passed"] for c in compared) and all(r["rejected"] for r in rejected),
        "not_run": ["large_input_benchmark", "OR-Tools", "browser", "assessment_runtime",
                    "learner_explanation", "live_stakeholder_Q&A"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--property-checks", action="store_true",
                        help="optional reviewed Hypothesis checks on synthetic inputs only")
    args = parser.parse_args(argv)
    if args.property_checks:
        from property_checks import install_runtime_guard, run_property_checks
        install_runtime_guard()
    report = run()
    if args.property_checks:
        try:
            report["property_checks"] = run_property_checks(
                compare_case, enumerate_best, greedy_knapsack, knapsack_01)
        except Exception as exc:
            print(json.dumps({"passed": False, "stage": "property_checks",
                              "error": type(exc).__name__, "reason": str(exc)},
                             ensure_ascii=False))
            return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
