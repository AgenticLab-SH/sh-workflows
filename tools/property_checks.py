#!/usr/bin/env python3
"""Optional bounded Hypothesis checks for the existing synthetic method trace.

No external inputs or answer generation. The optional dependency is imported
only when explicitly requested; stdlib-only entrypoints keep working without it.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path
import sys

EXPECTED_VERSIONS = {"hypothesis": "6.170.14", "sortedcontainers": "2.4.0"}


def install_runtime_guard():
    """Deny Python-audited network/subprocess attempts in this CLI process.

    This is a process-level regression guard, not an OS security sandbox.
    """
    def audit(event, args):
        if event.startswith("socket.") or event in ("subprocess.Popen", "os.system"):
            raise PermissionError("synthetic property runner denies network and subprocesses")
    sys.addaudithook(audit)


def verify_dependencies():
    found = {}
    for name, expected in EXPECTED_VERSIONS.items():
        try:
            found[name] = version(name)
        except PackageNotFoundError as exc:
            raise RuntimeError("optional property dependencies absent; use the documented local venv") from exc
        if found[name] != expected:
            raise RuntimeError(f"unsupported {name} version; expected the reviewed lock")
    return found


def run_property_checks(compare_case, enumerate_best, greedy_knapsack, knapsack_01):
    if any(key.startswith("HYPOTHESIS_EXPERIMENTAL_OBSERVABILITY") for key in os.environ):
        raise RuntimeError("observability-enabled environment is not supported by this synthetic runner")
    dependencies = verify_dependencies()
    # Process-only settings: no plugin autoload; constants cache stays in ignored local data.
    os.environ["HYPOTHESIS_NO_PLUGINS"] = "1"
    os.environ["HYPOTHESIS_STORAGE_DIRECTORY"] = str(
        Path(__file__).resolve().parents[1] / ".local" / "oss-integration" / "hypothesis-cache")
    from hypothesis import Phase, find, given, settings, strategies as st

    policy = dict(database=None, derandomize=True, deadline=None,
                  phases=(Phase.generate, Phase.shrink))
    # Every generated input stays inside the small independently enumerable model.
    small = st.tuples(st.lists(st.tuples(st.integers(0, 30), st.integers(0, 15)),
                              min_size=0, max_size=6), st.integers(0, 30))
    observed = {"dp_matches_subsets": 0, "budget_monotonic": 0,
                "permutation_preserves_objective": 0}

    @settings(max_examples=60, **policy)
    @given(small)
    def properties(case):
        rows, capacity = case
        values = [row[0] for row in rows]
        costs = [row[1] for row in rows]
        result = compare_case("generated_property", values, costs, capacity)
        assert result["passed"], result
        observed["dp_matches_subsets"] += 1
        best = result["dp"]["objective"]
        larger, _ = knapsack_01(values, costs, capacity + 1)
        assert larger >= best
        observed["budget_monotonic"] += 1
        reversed_value, _ = knapsack_01(values[::-1], costs[::-1], capacity)
        assert reversed_value == best
        observed["permutation_preserves_objective"] += 1

    properties()

    # Deliberately false claim: ratio-greedy is always optimal for indivisible items.
    # find() searches and shrinks; it does not claim a globally smallest counterexample.
    domain = st.tuples(st.lists(st.tuples(st.integers(1, 12), st.integers(1, 10)),
                               min_size=2, max_size=5), st.integers(1, 20))

    def greedy_is_worse(case):
        rows, capacity = case
        values = [row[0] for row in rows]
        costs = [row[1] for row in rows]
        baseline, _ = greedy_knapsack(values, costs, capacity)
        return baseline < enumerate_best(values, costs, capacity)

    rows, capacity = find(domain, greedy_is_worse,
                          settings=settings(max_examples=800, **policy))
    values, costs = [r[0] for r in rows], [r[1] for r in rows]
    witness = compare_case("shrunk_greedy_counterexample", values, costs, capacity)
    assert witness["passed"] and witness["gap_to_baseline"] > 0
    return {
        "dependencies": dependencies,
        "properties": observed,
        "settings": {"derandomize": True, "database": None, "deadline": None,
                     "property_max_examples": 60, "find_max_examples": 800,
                     "backend": "hypothesis", "input_max_items": 6},
        "counterexample": {"values": values, "costs": costs, **witness},
        "trace": {"question_ids": ["Q02", "Q03", "Q09", "Q10"],
                  "decision": "D02: ratio is a baseline, additive 0/1 objective uses DP",
                  "implementation": "tools/opt_kit.py: greedy_knapsack, knapsack_01",
                  "evidence": "counterexample plus independent subset optimum",
                  "learner_explanation": "NOT_RUN; no user answer generated",
                  "changed_assumption": "divisibility or item dependencies require a new model"},
        "passed": True,
    }
