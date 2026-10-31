#!/usr/bin/env python3
"""Small, deterministic optimization building blocks (stdlib only, no network, no file writes).

These are general components for baselines and small-scale exact checks, not a finished
answer for any particular task. Problem definition, objectives and constraints belong to
the participant and the official task instructions.

CLI:
  python tools/opt_kit.py assign --costs matrix.csv [--capacities 2,2,1]
  python tools/opt_kit.py demo
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import sys
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence, TypeVar

try:
    from kit_utils import InputError, ensure_file
except ImportError:  # imported as tools.opt_kit
    from tools.kit_utils import InputError, ensure_file  # type: ignore[no-redef]

T = TypeVar("T")
Matrix = Sequence[Sequence[float]]

MAX_BRUTE_ROWS = 12
MAX_BRUTE_COMBINATIONS = 2_000_000
MAX_BRUTE_ORDER_NODES = 9
MAX_KNAPSACK_CELLS = 5_000_000
MAX_CLI_DIM = 300
EPS = 1e-12

__all__ = [
    "InputError", "hungarian", "hungarian_with_capacity", "greedy_assign_with_capacity",
    "improve_assignment_by_swap", "brute_force_assignment", "assignment_cost", "constraint_report",
    "min_cost_flow", "assignment_flow",
    "knapsack_01", "greedy_knapsack", "first_fit_decreasing", "first_fit_multi", "bins_lower_bound",
    "pack_report", "interval_schedule",
    "nearest_neighbor_order", "two_opt", "order_length", "brute_force_order",
    "dijkstra", "shortest_path", "simulated_annealing", "pareto_front",
]


# ---------------------------------------------------------------- validation helpers

def _number(x: Any, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise InputError(f"{what} must be a number")
    if not math.isfinite(x):
        raise InputError(f"{what} must be finite")
    return x


def _matrix(m: Matrix, what: str = "cost matrix") -> list[list[float]]:
    if not isinstance(m, Sequence) or len(m) == 0:
        raise InputError(f"{what} must be a non-empty list of rows")
    rows = []
    width = None
    for i, row in enumerate(m):
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)) or len(row) == 0:
            raise InputError(f"{what} row {i} must be a non-empty list")
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise InputError(f"{what} must be rectangular")
        rows.append([_number(v, f"{what}[{i}]") for v in row])
    return rows


def _square_nonneg(dist: Matrix) -> list[list[float]]:
    d = _matrix(dist, "distance matrix")
    n = len(d)
    if any(len(r) != n for r in d):
        raise InputError("distance matrix must be square")
    if any(v < 0 for r in d for v in r):
        raise InputError("distance matrix must be non-negative")
    return d


def _capacities(capacities: Sequence[int], cols: int, rows: int, require_full: bool = True,
                hint: str = "use allow_unassigned=True or assignment_flow") -> list[int]:
    if not isinstance(capacities, Sequence) or len(capacities) != cols:
        raise InputError("capacities length must equal the number of columns")
    caps = []
    for c in capacities:
        if isinstance(c, bool) or not isinstance(c, int):
            raise InputError("capacities must be integers")
        if c < 0:
            raise InputError("capacities must be non-negative")
        caps.append(c)
    if require_full and sum(caps) < rows:
        raise InputError(f"total capacity is smaller than the number of rows ({hint})")
    return caps


UNASSIGNED_COST_REQUIRED = ("unassigned_cost is required when allow_unassigned=True; "
                            "with nonnegative costs 0 leaves everyone unassigned")


def _unassigned_cost(allow_unassigned: bool, unassigned_cost: float | None) -> float:
    """Explicit cost of an empty row when allow_unassigned=True; unused (0) otherwise."""
    if allow_unassigned and unassigned_cost is None:
        raise InputError(UNASSIGNED_COST_REQUIRED)
    return 0.0 if unassigned_cost is None else _number(unassigned_cost, "unassigned_cost")


def _forbidden(forbidden: Iterable[tuple[int, int]] | None, rows: int, cols: int) -> set[tuple[int, int]]:
    if forbidden is None:
        return set()
    out = set()
    for item in forbidden:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise InputError("forbidden must contain (row, col) pairs")
        i, j = item
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (i, j)) \
                or not (0 <= i < rows and 0 <= j < cols):
            raise InputError("forbidden contains an invalid (row, col) pair")
        out.add((i, j))
    return out


def _row_limits(row_limits: int | Sequence[int], rows: int) -> list[int]:
    if isinstance(row_limits, int) and not isinstance(row_limits, bool):
        return [_int_nonneg(row_limits, "row limit")] * rows
    if not isinstance(row_limits, Sequence) or len(row_limits) != rows:
        raise InputError("row_limits must be an integer or one integer per row")
    return [_int_nonneg(k, "row limit") for k in row_limits]


def _groups(groups: Sequence[Hashable], cols: int) -> list[Hashable]:
    if not isinstance(groups, Sequence) or isinstance(groups, (str, bytes)) or len(groups) != cols:
        raise InputError("groups must give one group label per column")
    out = list(groups)
    for g in out:
        try:
            hash(g)
        except TypeError as exc:
            raise InputError("group labels must be hashable") from exc
    return out


def _int_nonneg(x: Any, what: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise InputError(f"{what} must be a non-negative integer")
    return x


def _check_assignment(assignment: Sequence[int], rows: int, cols: int) -> list[int]:
    if len(assignment) != rows:
        raise InputError("assignment length must equal the number of rows")
    out = []
    for a in assignment:
        if isinstance(a, bool) or not isinstance(a, int) or not 0 <= a < cols:
            raise InputError("assignment contains an invalid column index")
        out.append(a)
    return out


# ---------------------------------------------------------------- assignment

def hungarian(cost_matrix: Matrix) -> tuple[list[int | None], float]:
    """Minimum-cost one-to-one assignment (Hungarian / Kuhn-Munkres, O(n^2 m)).

    Rectangular input is supported. If rows <= cols every row gets a distinct column.
    If rows > cols the problem is solved on the transpose, so only `cols` rows are
    assigned and the rest are None. Returns (assignment[row] -> column or None, total).
    To maximize, pass negated scores.
    """
    a = _matrix(cost_matrix)
    n, m = len(a), len(a[0])
    if n > m:
        t = [[a[i][j] for i in range(n)] for j in range(m)]
        col_to_row, total = hungarian(t)
        res: list[int | None] = [None] * n
        for j, i in enumerate(col_to_row):
            if i is not None:
                res[i] = j
        return res, total
    inf = math.inf
    u = [0.0] * (n + 1)
    v = [0.0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [inf] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = inf
            j1 = 0
            row = a[i0 - 1]
            for j in range(1, m + 1):
                if not used[j]:
                    cur = row[j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    result: list[int | None] = [None] * n
    for j in range(1, m + 1):
        if p[j]:
            result[p[j] - 1] = j - 1
    total = sum(a[i][c] for i, c in enumerate(result) if c is not None)
    return result, total


def hungarian_with_capacity(costs: Matrix, capacities: Sequence[int], allow_unassigned: bool = False,
                            unassigned_cost: float | None = None,
                            forbidden: Iterable[tuple[int, int]] | None = None) -> tuple[list[int | None], float]:
    """Exact capacitated assignment: copy each column `capacity` times, then run Hungarian.

    Each column is expanded to min(capacity, rows) slots. Cost grows with rows * slots,
    so use it for small or medium inputs and compare with greedy + swap on larger ones.

    allow_unassigned=True adds `rows` dummy slots of cost `unassigned_cost`, so the total
    capacity may be smaller than the number of rows; unassigned rows get None.
    unassigned_cost is then required (InputError if omitted). Pitfall: when minimizing
    nonnegative costs, unassigned_cost=0 makes "leave empty" the cheapest choice for every
    row, so nobody is assigned; set it above the largest cost you would still accept.
    forbidden is a set of (row, col) pairs that are never used in the result. If every
    row must be assigned and that is impossible without a forbidden cell, InputError.
    Returned total = assigned costs + unassigned_cost * (number of None rows).
    To maximize scores, pass negated scores (then unassigned_cost=0 means "empty is 0 points").
    """
    a = _matrix(costs)
    n, m = len(a), len(a[0])
    caps = _capacities(capacities, m, n, require_full=not allow_unassigned)
    u = _unassigned_cost(allow_unassigned, unassigned_cost)
    banned = _forbidden(forbidden, n, m)
    slot_col: list[int | None] = [j for j in range(m) for _ in range(min(caps[j], n))]
    if allow_unassigned:
        slot_col += [None] * n
    values = [v for r in a for v in r] + ([u] if allow_unassigned else [])
    # Any solution with one more forbidden cell costs more than any spread of normal costs.
    big = (max(values) - min(values) + 1.0) * (n + 1) + max(abs(v) for v in values)
    expanded = [[u if c is None else (big if (i, c) in banned else a[i][c]) for c in slot_col]
                for i in range(n)]
    slots, _ = hungarian(expanded)
    assignment: list[int | None] = []
    for i, s in enumerate(slots):
        c = slot_col[s]  # rows <= slots, so every row gets a slot
        if c is not None and (i, c) in banned:
            if not allow_unassigned:
                raise InputError("no assignment of every row avoids the forbidden cells")
            c = None  # safety net; the big cost already makes the dummy slot cheaper
        assignment.append(c)
    total = assignment_cost(assignment, a) + u * sum(c is None for c in assignment)
    return assignment, total


def assignment_cost(assignment: Sequence[int | None], costs: Matrix) -> float:
    """Sum of costs[row][col] over assigned rows (None rows are skipped)."""
    a = _matrix(costs)
    return sum(a[i][c] for i, c in enumerate(assignment) if c is not None)


def greedy_assign_with_capacity(costs: Matrix, capacities: Sequence[int], allow_unassigned: bool = False,
                                unassigned_cost: float | None = None,
                                forbidden: Iterable[tuple[int, int]] | None = None) -> list[int | None]:
    """Baseline: take (cost, row, col) pairs in ascending order while capacity remains.

    Deterministic (ties by row, then column). Forbidden (row, col) pairs are skipped.
    Without allow_unassigned every row must be placed, otherwise InputError.
    With allow_unassigned a row is placed only when the pair costs strictly less than
    `unassigned_cost`, which is then required (InputError if omitted); the rest stay None.
    Pitfall: with nonnegative costs, unassigned_cost=0 places nobody.
    Returns assignment[row] -> column or None.
    """
    a = _matrix(costs)
    n, m = len(a), len(a[0])
    left = _capacities(capacities, m, n, require_full=not allow_unassigned)
    u = _unassigned_cost(allow_unassigned, unassigned_cost)
    banned = _forbidden(forbidden, n, m)
    pairs = sorted((a[i][j], i, j) for i in range(n) for j in range(m) if (i, j) not in banned)
    result: list[int | None] = [None] * n
    done = 0
    for c, i, j in pairs:
        if allow_unassigned and c >= u:
            break
        if result[i] is None and left[j] > 0:
            result[i] = j
            left[j] -= 1
            done += 1
            if done == n:
                break
    if not allow_unassigned and done < n:
        raise InputError("greedy could not place every row (capacity or forbidden cells); "
                         "try hungarian_with_capacity or allow_unassigned=True")
    return result


def improve_assignment_by_swap(assignment: Sequence[int], costs: Matrix, capacities: Sequence[int],
                               max_rounds: int = 100) -> list[int]:
    """Local search: move a row to a column with spare capacity, or swap two rows' columns.

    Applies the first strictly improving move in a fixed order, repeats until no move
    improves or `max_rounds` passes are done. Never breaks capacities. Returns a new list.
    Every row must already have a column. If a baseline left rows unassigned (None), drop
    those rows from both `assignment` and `costs` before calling, or solve the whole
    problem with assignment_flow, which handles empty rows exactly.
    """
    a = _matrix(costs)
    n, m = len(a), len(a[0])
    if not isinstance(assignment, Sequence) or any(c is None for c in assignment):
        raise InputError("improve_assignment_by_swap needs every row assigned; drop the unassigned "
                         "(None) rows and their cost rows before calling, or use assignment_flow")
    caps = _capacities(capacities, m, n, require_full=False)
    cur = _check_assignment(assignment, n, m)
    if isinstance(max_rounds, bool) or not isinstance(max_rounds, int) or max_rounds < 0:
        raise InputError("max_rounds must be a non-negative integer")
    load = [0] * m
    for c in cur:
        load[c] += 1
    if any(load[j] > caps[j] for j in range(m)):
        raise InputError("initial assignment violates capacities")
    for _ in range(max_rounds):
        improved = False
        for i in range(n):
            for j in range(m):
                if j != cur[i] and load[j] < caps[j] and a[i][j] < a[i][cur[i]] - EPS:
                    load[cur[i]] -= 1
                    load[j] += 1
                    cur[i] = j
                    improved = True
        for i in range(n):
            for k in range(i + 1, n):
                ci, ck = cur[i], cur[k]
                if ci != ck and a[i][ck] + a[k][ci] < a[i][ci] + a[k][ck] - EPS:
                    cur[i], cur[k] = ck, ci
                    improved = True
        if not improved:
            break
    return cur


def brute_force_assignment(costs: Matrix, capacities: Sequence[int] | None = None) -> tuple[list[int], float]:
    """Exact capacitated assignment by depth-first search with a simple lower bound.

    For verifying heuristics on small inputs only. capacities=None means 1 per column.
    Raises InputError when rows > MAX_BRUTE_ROWS or cols**rows > MAX_BRUTE_COMBINATIONS.
    """
    a = _matrix(costs)
    n, m = len(a), len(a[0])
    caps = _capacities([1] * m if capacities is None else capacities, m, n,
                       hint="brute force assigns every row; check unassigned cases with assignment_flow")
    if n > MAX_BRUTE_ROWS or m ** n > MAX_BRUTE_COMBINATIONS:
        raise InputError("input too large for brute force; use it only on small checks")
    row_min = [min(r) for r in a]
    rest = [0.0] * (n + 1)
    for i in range(n - 1, -1, -1):
        rest[i] = rest[i + 1] + row_min[i]
    best: list[Any] = [math.inf, None]
    cur = [0] * n
    left = caps[:]

    def dfs(i: int, acc: float) -> None:
        if acc + rest[i] >= best[0] - EPS:
            return
        if i == n:
            best[0], best[1] = acc, cur[:]
            return
        for j in range(m):
            if left[j]:
                left[j] -= 1
                cur[i] = j
                dfs(i + 1, acc + a[i][j])
                left[j] += 1

    dfs(0, 0.0)
    assignment = best[1]
    return assignment, assignment_cost(assignment, a)


def constraint_report(assignment: Sequence[int | Sequence[int] | None], capacities: Sequence[int],
                      row_limits: int | Sequence[int] | None = None,
                      groups: Sequence[Hashable] | None = None) -> list[dict[str, Any]]:
    """List constraint violations. Empty list means no violation.

    assignment[row] may be a column, None (unassigned) or a list of columns (several per row).
    Always checks column capacity: {"column", "assigned", "capacity", "excess"}.
    A column repeated inside one row: {"row", "column", "assigned", "limit": 1, "excess"}.
    row_limits (int or one per row): {"row", "assigned", "limit", "excess"}.
    groups (one label per column, e.g. a time slot): at most one column per (row, group),
    reported as {"row", "group", "assigned", "limit": 1, "excess"}.
    """
    caps = list(capacities)
    if any(isinstance(c, bool) or not isinstance(c, int) or c < 0 for c in caps):
        raise InputError("capacities must be non-negative integers")
    limits = None if row_limits is None else _row_limits(row_limits, len(assignment))
    grp = None if groups is None else _groups(groups, len(caps))
    load = [0] * len(caps)
    per_row: list[list[int]] = []
    for c in assignment:
        cols = [] if c is None else list(c) if isinstance(c, (list, tuple)) else [c]
        for j in cols:
            if isinstance(j, bool) or not isinstance(j, int) or not 0 <= j < len(caps):
                raise InputError("assignment contains an invalid column index")
            load[j] += 1
        per_row.append(cols)
    report: list[dict[str, Any]] = [
        {"column": j, "assigned": load[j], "capacity": caps[j], "excess": load[j] - caps[j]}
        for j in range(len(caps)) if load[j] > caps[j]]
    for i, cols in enumerate(per_row):
        for j in sorted(set(cols)):
            if cols.count(j) > 1:
                report.append({"row": i, "column": j, "assigned": cols.count(j), "limit": 1,
                               "excess": cols.count(j) - 1})
        if limits is not None and len(cols) > limits[i]:
            report.append({"row": i, "assigned": len(cols), "limit": limits[i],
                           "excess": len(cols) - limits[i]})
        if grp is not None:
            counts: dict[Hashable, int] = {}
            for j in cols:
                counts[grp[j]] = counts.get(grp[j], 0) + 1
            for g, k in counts.items():
                if k > 1:
                    report.append({"row": i, "group": g, "assigned": k, "limit": 1, "excess": k - 1})
    return report


# ---------------------------------------------------------------- min-cost flow

def min_cost_flow(num_nodes: int, edges: Sequence[tuple[int, int, int, float]], source: int, sink: int,
                  max_flow: int | None = None) -> dict[str, Any]:
    """Minimum-cost flow by successive shortest paths (Bellman-Ford queue / SPFA).

    Nodes are 0..num_nodes-1. edges: (u, v, capacity, cost) with integer capacity >= 0.
    Negative costs are allowed if the graph has no negative-cost cycle (else InputError).
    Sends as much flow as possible (up to max_flow) and, for that amount, the least cost.
    Returns {"flow": int, "cost": float, "edge_flows": [flow on edges[k]]}.
    Small and medium graphs only: each augmentation is O(V * E).
    """
    from collections import deque

    n = _int_nonneg(num_nodes, "num_nodes")
    if n < 2:
        raise InputError("num_nodes must be at least 2")

    def node(x: Any, what: str) -> int:
        if isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < n:
            raise InputError(f"{what} must be a node index in 0..num_nodes-1")
        return x

    s, t = node(source, "source"), node(sink, "sink")
    if s == t:
        raise InputError("source and sink must differ")
    limit: float = math.inf if max_flow is None else _int_nonneg(max_flow, "max_flow")
    to: list[int] = []
    cap: list[int] = []
    cst: list[float] = []
    adj: list[list[int]] = [[] for _ in range(n)]
    for e in edges:
        if not isinstance(e, (tuple, list)) or len(e) != 4:
            raise InputError("each edge must be (u, v, capacity, cost)")
        u, v = node(e[0], "edge start"), node(e[1], "edge end")
        c, w = _int_nonneg(e[2], "edge capacity"), _number(e[3], "edge cost")
        adj[u].append(len(to)); to.append(v); cap.append(c); cst.append(w)
        adj[v].append(len(to)); to.append(u); cap.append(0); cst.append(-w)
    flow = 0
    while flow < limit:
        dist = [math.inf] * n
        prev = [-1] * n
        inq = [False] * n
        hops = [0] * n
        dist[s] = 0.0
        queue = deque([s])
        inq[s] = True
        while queue:
            x = queue.popleft()
            inq[x] = False
            for e in adj[x]:
                y = to[e]
                if cap[e] > 0 and dist[x] + cst[e] < dist[y] - EPS:
                    dist[y] = dist[x] + cst[e]
                    prev[y] = e
                    hops[y] = hops[x] + 1
                    if hops[y] >= n:  # a shortest path never needs n edges
                        raise InputError("graph has a negative-cost cycle; min_cost_flow needs none")
                    if not inq[y]:
                        queue.append(y)
                        inq[y] = True
        if dist[t] == math.inf:
            break
        push = limit - flow
        y = t
        while y != s:
            e = prev[y]
            push = min(push, cap[e])
            y = to[e ^ 1]
        push = int(push)
        y = t
        while y != s:
            e = prev[y]
            cap[e] -= push
            cap[e ^ 1] += push
            y = to[e ^ 1]
        flow += push
    edge_flows = [cap[2 * k + 1] for k in range(len(edges))]
    total = sum(f * float(edges[k][3]) for k, f in enumerate(edge_flows))
    return {"flow": flow, "cost": total, "edge_flows": edge_flows}


def assignment_flow(scores_or_costs: Matrix, row_limits: int | Sequence[int], col_capacities: Sequence[int],
                    groups: Sequence[Hashable] | None = None, maximize: bool = False,
                    unassigned_cost: float = 0.0,
                    forbidden: Iterable[tuple[int, int]] | None = None,
                    fixed: Iterable[tuple[int, int]] | None = None) -> dict[str, Any]:
    """Exact assignment with several picks per row, via min-cost flow.

    Each row takes at most row_limits[i] columns (int = same for all rows), each column at
    most col_capacities[j] rows, a row takes a column at most once, and at most one column
    per (row, group) when groups gives a label per column (e.g. a time slot). Forbidden
    (row, col) pairs are never used. With maximize=True, block cells that must not be
    used with forbidden instead of giving them score 0: a 0-score cell ties with
    unassigned_cost=0 and may be filled. Rows may stay partly or fully unassigned: every
    unfilled row slot is worth `unassigned_cost` (a score when maximize=True, a cost
    otherwise). For minimization with positive costs, set unassigned_cost above the costs
    you would accept, or nothing gets assigned.
    fixed: (row, col) pairs that are decided in advance. Pre-processing per pair: column
    capacity - 1, row limit - 1, every column of the same group is forbidden for that row
    (so the row cannot take another class in that slot or the same column twice), and its
    value is added separately. If pre-processing makes any capacity or limit negative, or
    a fixed pair is forbidden, repeated, or shares a group with another fixed pair of the
    same row, nothing is solved: the result has assignment=None, objective=None and a
    non-empty "conflicts" list (all conflicts at once, so they can be reported together).
    Network: source -> row (cap k) -> (row, group) (cap 1) -> column (cap 1) -> sink (cap
    capacity), plus row -> sink (cap k, unassigned value) for empty slots.
    Returns {"assignment": [sorted column list per row, fixed included], "objective": pair
    total + unassigned_cost * unfilled, "pairs_total" (fixed included), "fixed_total",
    "fixed", "unfilled", "conflicts": [], "maximize"}.
    """
    a = _matrix(scores_or_costs)
    n, m = len(a), len(a[0])
    limits = _row_limits(row_limits, n)
    caps = _capacities(col_capacities, m, n, require_full=False)
    grp: list[Hashable] = list(range(m)) if groups is None else _groups(groups, m)
    banned = _forbidden(forbidden, n, m)
    u = _number(unassigned_cost, "unassigned_cost")
    sign = -1.0 if maximize else 1.0
    total_limit = sum(limits)
    fixed_list: list[tuple[int, int]] = []
    if fixed is not None:
        for item in fixed:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise InputError("fixed must contain (row, col) pairs")
            i, j = item
            if any(isinstance(x, bool) or not isinstance(x, int) for x in (i, j)) \
                    or not (0 <= i < n and 0 <= j < m):
                raise InputError("fixed contains an invalid (row, col) pair")
            fixed_list.append((i, j))
    conflicts: list[dict[str, Any]] = []
    seen: dict[tuple[int, int], int] = {}
    group_cols: dict[tuple[int, Hashable], list[int]] = {}
    fixed_cols: list[list[int]] = [[] for _ in range(n)]
    for i, j in fixed_list:
        seen[(i, j)] = seen.get((i, j), 0) + 1
        cols_in_group = group_cols.setdefault((i, grp[j]), [])
        if j not in cols_in_group:
            cols_in_group.append(j)
        if (i, j) in banned:
            conflicts.append({"kind": "forbidden", "row": i, "column": j})
        caps[j] -= 1
        limits[i] -= 1
        fixed_cols[i].append(j)
    for (i, j), k in sorted(seen.items()):
        if k > 1:
            conflicts.append({"kind": "duplicate", "row": i, "column": j, "fixed": k})
    for (i, g), cols in group_cols.items():
        if len(cols) > 1:
            conflicts.append({"kind": "group", "row": i, "group": g, "columns": sorted(cols), "limit": 1})
    for j in range(m):
        if caps[j] < 0:
            conflicts.append({"kind": "column_capacity", "column": j,
                              "fixed": col_capacities[j] - caps[j], "capacity": col_capacities[j]})
    for i in range(n):
        if limits[i] < 0:
            conflicts.append({"kind": "row_limit", "row": i, "fixed": len(fixed_cols[i]),
                              "limit": len(fixed_cols[i]) + limits[i]})
    fixed_total = sum(a[i][j] for i, j in fixed_list)
    if conflicts:
        return {"assignment": None, "objective": None, "pairs_total": None, "fixed_total": fixed_total,
                "fixed": sorted(fixed_list), "unfilled": None, "conflicts": conflicts,
                "maximize": maximize}
    for i, j in fixed_list:
        for c in range(m):
            if grp[c] == grp[j]:
                banned.add((i, c))
    labels: list[Hashable] = []
    for g in grp:
        if g not in labels:
            labels.append(g)
    source, sink = 0, 1
    nodes = 2 + n + m
    edges: list[tuple[int, int, int, float]] = []
    pair_edge: dict[tuple[int, int], int] = {}
    for i in range(n):
        r = 2 + i
        edges.append((source, r, limits[i], 0.0))
        edges.append((r, sink, limits[i], sign * u))
        for g in labels:
            cols = [j for j in range(m) if grp[j] == g and caps[j] > 0 and (i, j) not in banned]
            if not cols:
                continue
            rg = nodes
            nodes += 1
            edges.append((r, rg, 1, 0.0))
            for j in cols:
                pair_edge[(i, j)] = len(edges)
                edges.append((rg, 2 + n + j, 1, sign * a[i][j]))
    for j in range(m):
        edges.append((2 + n + j, sink, caps[j], 0.0))
    res = min_cost_flow(nodes, edges, source, sink)
    assignment: list[list[int]] = [list(cols) for cols in fixed_cols]
    for (i, j), k in sorted(pair_edge.items()):
        if res["edge_flows"][k]:
            assignment[i].append(j)
    assignment = [sorted(cols) for cols in assignment]
    pairs_total = sum(a[i][j] for i, cols in enumerate(assignment) for j in cols)
    unfilled = total_limit - sum(len(cols) for cols in assignment)
    return {"assignment": assignment, "objective": pairs_total + u * unfilled,
            "pairs_total": pairs_total, "fixed_total": fixed_total, "fixed": sorted(fixed_list),
            "unfilled": unfilled, "conflicts": [], "maximize": maximize}


# ---------------------------------------------------------------- selection / packing / intervals

def knapsack_01(values: Sequence[float], weights: Sequence[int], capacity: int) -> tuple[float, list[int]]:
    """Exact 0/1 knapsack by dynamic programming, O(n * capacity).

    Weights and capacity must be non-negative integers (scale units first, e.g. 1,000 won).
    Returns (best_value, chosen indices ascending).
    """
    if len(values) != len(weights):
        raise InputError("values and weights must have the same length")
    vals = [_number(v, "value") for v in values]
    wts = [_int_nonneg(w, "weight") for w in weights]
    cap = _int_nonneg(capacity, "capacity")
    n = len(vals)
    if n * (cap + 1) > MAX_KNAPSACK_CELLS:
        raise InputError("knapsack table too large; scale weights or use greedy_knapsack")
    dp = [0.0] * (cap + 1)
    take = [bytearray(cap + 1) for _ in range(n)]
    for i in range(n):
        w, v = wts[i], vals[i]
        if v <= 0:
            continue
        for c in range(cap, w - 1, -1):
            cand = dp[c - w] + v
            if cand > dp[c] + EPS:
                dp[c] = cand
                take[i][c] = 1
    chosen = []
    c = cap
    for i in range(n - 1, -1, -1):
        if take[i][c]:
            chosen.append(i)
            c -= wts[i]
    chosen.sort()
    return sum(vals[i] for i in chosen), chosen


def greedy_knapsack(values: Sequence[float], weights: Sequence[float], capacity: float) -> tuple[float, list[int]]:
    """Baseline: pick items by value/weight ratio (desc) while they fit. Not always optimal."""
    if len(values) != len(weights):
        raise InputError("values and weights must have the same length")
    vals = [_number(v, "value") for v in values]
    wts = [_number(w, "weight") for w in weights]
    cap = _number(capacity, "capacity")
    if cap < 0 or any(w < 0 for w in wts):
        raise InputError("weights and capacity must be non-negative")
    order = sorted(range(len(vals)), key=lambda i: (-(vals[i] / wts[i]) if wts[i] else -math.inf, i))
    used, chosen = 0.0, []
    for i in order:
        if vals[i] > 0 and used + wts[i] <= cap + EPS:
            used += wts[i]
            chosen.append(i)
    chosen.sort()
    return sum(vals[i] for i in chosen), chosen


def first_fit_decreasing(sizes: Sequence[float], capacity: float) -> list[list[int]]:
    """Bin packing heuristic: sort items by size (desc) and put each in the first bin it fits.

    Returns bins as lists of item indices. Uses at most about 11/9 * optimal + 1 bins.
    """
    cap = _number(capacity, "capacity")
    if cap <= 0:
        raise InputError("capacity must be positive")
    sz = [_number(s, "size") for s in sizes]
    if any(s <= 0 or s > cap + EPS for s in sz):
        raise InputError("each size must be positive and not exceed capacity")
    bins: list[list[int]] = []
    room: list[float] = []
    for i in sorted(range(len(sz)), key=lambda k: (-sz[k], k)):
        for b in range(len(bins)):
            if sz[i] <= room[b] + EPS:
                bins[b].append(i)
                room[b] -= sz[i]
                break
        else:
            bins.append([i])
            room.append(cap - sz[i])
    return bins


def _multi_sizes(sizes: Sequence[Sequence[float]], capacities: Sequence[float]) -> tuple[list[list[float]], list[float]]:
    caps = [_number(c, "capacity") for c in capacities]
    if not caps or any(c <= 0 for c in caps):
        raise InputError("capacities must be a non-empty list of positive numbers")
    out = []
    for i, s in enumerate(sizes):
        if not isinstance(s, Sequence) or isinstance(s, (str, bytes)) or len(s) != len(caps):
            raise InputError(f"item {i} must have one size per capacity dimension")
        v = [_number(x, f"size[{i}]") for x in s]
        if any(x < 0 for x in v):
            raise InputError("sizes must be non-negative")
        if any(x > c + EPS for x, c in zip(v, caps)):
            raise InputError(f"item {i} exceeds a capacity; list it separately before packing")
        out.append(v)
    return out, caps


def _incompatible(labels: Sequence[Hashable] | None, incompatible: Iterable[tuple[Hashable, Hashable]] | None,
                  n: int) -> tuple[list[Hashable] | None, set[frozenset]]:
    if incompatible is None:
        return (list(labels) if labels is not None else None), set()
    if labels is None or len(labels) != n:
        raise InputError("labels must give one label per item when incompatible pairs are used")
    pairs = set()
    for p in incompatible:
        if not isinstance(p, (tuple, list)) or len(p) != 2:
            raise InputError("incompatible must contain (label, label) pairs")
        pairs.add(frozenset(p))
    return list(labels), pairs


def first_fit_multi(sizes: Sequence[Sequence[float]], capacities: Sequence[float],
                    labels: Sequence[Hashable] | None = None,
                    incompatible: Iterable[tuple[Hashable, Hashable]] | None = None,
                    order: Sequence[int] | None = None) -> list[list[int]]:
    """Baseline packing with several capacity dimensions and label conflicts.

    sizes[i] has one value per dimension (for example weight and volume) and every bin
    has the same `capacities`. Items whose labels form an `incompatible` pair never share
    a bin (a pair (a, a) forbids two items with label a together). Items go in `order`
    (default: as given) into the first bin where every dimension still fits; pass e.g.
    sorted(range(n), key=lambda i: -sizes[i][1]) for "largest volume first".
    This is a heuristic baseline, not an optimum: compare with bins_lower_bound and try
    other orders or a local search (simulated_annealing) before calling a plan minimal.
    Items larger than a capacity raise InputError; list them separately first.
    Returns bins as lists of item indices in insertion order.
    """
    sz, caps = _multi_sizes(sizes, capacities)
    lab, bad = _incompatible(labels, incompatible, len(sz))
    idx = list(range(len(sz))) if order is None else list(order)
    if sorted(idx) != list(range(len(sz))):
        raise InputError("order must be a permutation of item indices")
    bins: list[list[int]] = []
    load: list[list[float]] = []
    for i in idx:
        for b in range(len(bins)):
            if all(load[b][d] + sz[i][d] <= caps[d] + EPS for d in range(len(caps))) and \
                    not (bad and any(frozenset((lab[i], lab[j])) in bad for j in bins[b])):
                bins[b].append(i)
                load[b] = [load[b][d] + sz[i][d] for d in range(len(caps))]
                break
        else:
            bins.append([i])
            load.append(list(sz[i]))
    return bins


def bins_lower_bound(sizes: Sequence[Sequence[float]], capacities: Sequence[float]) -> int:
    """max over dimensions of ceil(total size / capacity). A plan with this many bins is minimal."""
    sz, caps = _multi_sizes(sizes, capacities)
    return max((math.ceil(sum(s[d] for s in sz) / caps[d] - EPS) for d in range(len(caps))), default=0)


def pack_report(bins: Sequence[Sequence[int]], sizes: Sequence[Sequence[float]], capacities: Sequence[float],
                labels: Sequence[Hashable] | None = None,
                incompatible: Iterable[tuple[Hashable, Hashable]] | None = None,
                groups: Sequence[Hashable | None] | None = None) -> dict[str, Any]:
    """Check a packing plan: capacity and conflict violations, missing/repeated items, split groups.

    groups[i] is a set label for item i (None or '' = no group); a group spread over more
    than one bin counts once in "split_groups". Returns {"bins", "violations", "split_groups"}.
    """
    sz, caps = _multi_sizes(sizes, capacities)
    lab, bad = _incompatible(labels, incompatible, len(sz))
    if groups is not None and len(groups) != len(sz):
        raise InputError("groups must give one value per item")
    violations: list[dict[str, Any]] = []
    seen: dict[int, int] = {}
    for b, items in enumerate(bins):
        for i in items:
            if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(sz):
                raise InputError("bins contain an invalid item index")
            seen[i] = seen.get(i, 0) + 1
        for d, c in enumerate(caps):
            total = sum(sz[i][d] for i in items)
            if total > c + EPS:
                violations.append({"kind": "capacity", "bin": b, "dimension": d, "load": total, "capacity": c})
        if bad:
            for x in range(len(items)):
                for y in range(x + 1, len(items)):
                    if frozenset((lab[items[x]], lab[items[y]])) in bad:
                        violations.append({"kind": "conflict", "bin": b, "items": [items[x], items[y]]})
    for i in range(len(sz)):
        if seen.get(i, 0) != 1:
            violations.append({"kind": "missing" if i not in seen else "repeated", "item": i,
                               "count": seen.get(i, 0)})
    split = 0
    if groups is not None:
        where: dict[Hashable, set[int]] = {}
        for b, items in enumerate(bins):
            for i in items:
                g = groups[i]
                if g not in (None, ''):
                    where.setdefault(g, set()).add(b)
        split = sum(1 for s in where.values() if len(s) > 1)
    return {"bins": len(bins), "violations": violations, "split_groups": split}


def interval_schedule(intervals: Sequence[tuple[float, float]]) -> list[int]:
    """Maximum number of non-overlapping [start, end) intervals (earliest end first)."""
    iv = []
    for k, pair in enumerate(intervals):
        if len(pair) != 2:
            raise InputError("each interval must be (start, end)")
        s, e = _number(pair[0], "start"), _number(pair[1], "end")
        if e < s:
            raise InputError("interval end must not be before start")
        iv.append((e, s, k))
    chosen, last = [], -math.inf
    for e, s, k in sorted(iv):
        if s >= last:
            chosen.append(k)
            last = e
    return sorted(chosen)


# ---------------------------------------------------------------- visiting / work order

def order_length(order: Sequence[int], dist: Matrix, closed: bool = False) -> float:
    """Total distance along `order`; closed=True adds the edge back to the first node."""
    d = _square_nonneg(dist)
    n = len(d)
    if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < n for x in order):
        raise InputError("order contains an invalid node index")
    return _length(order, d, closed)


def _length(order: Sequence[int], d: list[list[float]], closed: bool) -> float:
    total = sum(d[order[k]][order[k + 1]] for k in range(len(order) - 1))
    if closed and len(order) > 1:
        total += d[order[-1]][order[0]]
    return total


def nearest_neighbor_order(dist: Matrix, start: int = 0) -> list[int]:
    """Baseline order: from `start`, always go to the nearest unvisited node (ties: lower index)."""
    d = _square_nonneg(dist)
    n = len(d)
    if isinstance(start, bool) or not isinstance(start, int) or not 0 <= start < n:
        raise InputError("start must be a valid node index")
    order, seen = [start], {start}
    while len(order) < n:
        last = order[-1]
        nxt = min((j for j in range(n) if j not in seen), key=lambda j: (d[last][j], j))
        order.append(nxt)
        seen.add(nxt)
    return order


def two_opt(order: Sequence[int], dist: Matrix, closed: bool = False, max_rounds: int = 1000) -> list[int]:
    """Improve an order by reversing segments while the length strictly decreases.

    The first node stays fixed. Works for asymmetric matrices (full recompute) but is
    fastest for symmetric ones (O(1) delta). Result is never longer than the input.
    """
    d = _square_nonneg(dist)
    n = len(d)
    cur = list(order)
    if sorted(cur) != list(range(n)):
        raise InputError("order must be a permutation of all nodes")
    symmetric = all(d[i][j] == d[j][i] for i in range(n) for j in range(i + 1, n))
    best_len = order_length(cur, d, closed)
    for _ in range(max_rounds):
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if symmetric:
                    a, b, c = cur[i - 1], cur[i], cur[j]
                    if j + 1 < n:
                        e = cur[j + 1]
                        delta = d[a][c] + d[b][e] - d[a][b] - d[c][e]
                    elif closed:
                        e = cur[0]
                        delta = d[a][c] + d[b][e] - d[a][b] - d[c][e]
                    else:
                        delta = d[a][c] - d[a][b]
                    if delta < -EPS:
                        cur[i:j + 1] = reversed(cur[i:j + 1])
                        best_len += delta
                        improved = True
                else:
                    cand = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
                    length = _length(cand, d, closed)
                    if length < best_len - EPS:
                        cur, best_len, improved = cand, length, True
        if not improved:
            break
    return cur


def brute_force_order(dist: Matrix, start: int = 0, closed: bool = False) -> tuple[list[int], float]:
    """Exact best order starting at `start` by checking all permutations (n <= 9)."""
    d = _square_nonneg(dist)
    n = len(d)
    if n > MAX_BRUTE_ORDER_NODES:
        raise InputError(f"brute force order supports at most {MAX_BRUTE_ORDER_NODES} nodes")
    if isinstance(start, bool) or not isinstance(start, int) or not 0 <= start < n:
        raise InputError("start must be a valid node index")
    others = [k for k in range(n) if k != start]
    best_order, best_len = None, math.inf
    for perm in itertools.permutations(others):
        cand = [start, *perm]
        length = _length(cand, d, closed)
        if length < best_len - EPS:
            best_order, best_len = cand, length
    return best_order, best_len  # type: ignore[return-value]


# ---------------------------------------------------------------- shortest path

def dijkstra(graph: Mapping[Hashable, Iterable[tuple[Hashable, float]]],
             source: Hashable) -> tuple[dict[Hashable, float], dict[Hashable, Hashable | None]]:
    """Single-source shortest paths for non-negative weights.

    graph: {node: [(neighbor, weight), ...]}. Returns (dist, prev) for reachable nodes only.
    """
    import heapq

    if source not in graph:
        raise InputError("source is not in graph")
    edges: dict[Hashable, list[tuple[Hashable, float]]] = {}
    for u, nbrs in graph.items():
        lst = []
        for item in nbrs:
            if len(item) != 2:
                raise InputError("edges must be (neighbor, weight)")
            w = _number(item[1], "edge weight")
            if w < 0:
                raise InputError("dijkstra requires non-negative weights")
            lst.append((item[0], w))
        edges[u] = lst
    dist: dict[Hashable, float] = {source: 0.0}
    prev: dict[Hashable, Hashable | None] = {source: None}
    heap: list[tuple[float, int, Hashable]] = [(0.0, 0, source)]
    counter = 1
    done = set()
    while heap:
        du, _, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in edges.get(u, []):
            nd = du + w
            if v not in dist or nd < dist[v] - EPS:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, counter, v))
                counter += 1
    return dist, prev


def shortest_path(prev: Mapping[Hashable, Hashable | None], target: Hashable) -> list[Hashable]:
    """Rebuild the node list from the source to `target` using dijkstra's prev map."""
    if target not in prev:
        return []
    path = [target]
    while prev[path[-1]] is not None:
        path.append(prev[path[-1]])
    return path[::-1]


# ---------------------------------------------------------------- metaheuristic / multi-objective

def simulated_annealing(initial: T, neighbor_fn: Callable[[T, random.Random], T],
                        cost_fn: Callable[[T], float], seed: int, iterations: int = 1000,
                        start_temp: float = 1.0, cooling: float = 0.995) -> tuple[T, float]:
    """Generic simulated annealing (minimization). Same seed and inputs give the same result.

    neighbor_fn(state, rng) must return a NEW state and use only the given rng for randomness.
    Returns (best_state, best_cost). Keep hard constraints inside neighbor_fn, or add a
    large penalty in cost_fn and check violations separately.
    """
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 0:
        raise InputError("iterations must be a non-negative integer")
    if _number(start_temp, "start_temp") <= 0:
        raise InputError("start_temp must be positive")
    if not 0 < _number(cooling, "cooling") < 1:
        raise InputError("cooling must be between 0 and 1")
    rng = random.Random(seed)
    cur, cur_cost = initial, _number(cost_fn(initial), "cost")
    best, best_cost = cur, cur_cost
    temp = start_temp
    for _ in range(iterations):
        cand = neighbor_fn(cur, rng)
        cand_cost = _number(cost_fn(cand), "cost")
        delta = cand_cost - cur_cost
        if delta <= 0 or rng.random() < math.exp(-delta / max(temp, EPS)):
            cur, cur_cost = cand, cand_cost
            if cur_cost < best_cost - EPS:
                best, best_cost = cur, cur_cost
        temp *= cooling
    return best, best_cost


def pareto_front(points: Sequence[Sequence[float]]) -> list[int]:
    """Indices of non-dominated points when every objective is minimized."""
    pts = [[_number(v, "objective") for v in p] for p in points]
    if len({len(p) for p in pts}) > 1:
        raise InputError("all points need the same number of objectives")
    keep = []
    for i, p in enumerate(pts):
        dominated = any(all(q[k] <= p[k] for k in range(len(p))) and any(q[k] < p[k] for k in range(len(p)))
                        for j, q in enumerate(pts) if j != i)
        if not dominated:
            keep.append(i)
    return keep


# ---------------------------------------------------------------- CLI

def _read_matrix_csv(path: str) -> tuple[list[str], list[str], list[list[float]]]:
    """Numeric CSV, or CSV with a header row (corner + column names) and a name column."""
    p = ensure_file(path, ".csv")
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        try:
            rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
        except csv.Error as exc:
            raise InputError("malformed CSV structure") from exc
    if not rows:
        raise InputError("CSV is empty")

    def num(cell: str) -> float:
        try:
            v = float(cell)
        except ValueError as exc:
            raise InputError("matrix cell is not a number") from exc
        if not math.isfinite(v):
            raise InputError("matrix cell must be finite")
        return v

    try:
        [float(c) for c in rows[0]]
        header = False
    except ValueError:
        header = True
    if header:
        col_names = [c.strip() for c in rows[0][1:]]
        body = rows[1:]
        row_names = [r[0].strip() for r in body]
        data = [[num(c) for c in r[1:]] for r in body]
    else:
        data = [[num(c) for c in r] for r in rows]
        row_names = [f"r{i}" for i in range(len(data))]
        col_names = [f"c{j}" for j in range(len(data[0]))]
    if not data or len(data) > MAX_CLI_DIM or len(col_names) > MAX_CLI_DIM:
        raise InputError(f"matrix must have 1..{MAX_CLI_DIM} rows and columns")
    if any(len(r) != len(col_names) for r in data):
        raise InputError("matrix must be rectangular and match the header")
    return row_names, col_names, _matrix(data)


def _named(assignment: Sequence[int | None], rows: list[str], cols: list[str]) -> dict[str, str | None]:
    return {rows[i]: (cols[c] if c is not None else None) for i, c in enumerate(assignment)}


def cli_assign(costs_path: str, capacities_text: str | None) -> dict[str, Any]:
    rows, cols, a = _read_matrix_csv(costs_path)
    if not capacities_text:
        assignment, total = hungarian(a)
        return {"method": "hungarian", "rows": len(rows), "columns": len(cols),
                "total_cost": round(total, 9), "unassigned_rows": sum(c is None for c in assignment),
                "assignment": _named(assignment, rows, cols),
                "note": "One-to-one minimum cost. Negate scores to maximize."}
    try:
        caps = [int(x) for x in capacities_text.split(",") if x.strip()]
    except ValueError as exc:
        raise InputError("capacities must be comma-separated integers") from exc
    greedy = greedy_assign_with_capacity(a, caps)
    improved = improve_assignment_by_swap(greedy, a, caps)
    out: dict[str, Any] = {
        "method": "greedy_with_capacity+swap", "rows": len(rows), "columns": len(cols),
        "baseline_total": round(assignment_cost(greedy, a), 9),
        "improved_total": round(assignment_cost(improved, a), 9),
        "capacity_violations": constraint_report(improved, caps),
        "assignment": _named(improved, rows, cols)}
    slots = sum(min(c, len(rows)) for c in caps)
    if len(rows) * slots <= 40_000:
        exact, exact_total = hungarian_with_capacity(a, caps)
        out["exact_total"] = round(exact_total, 9)
        out["gap_vs_exact"] = round(out["improved_total"] - exact_total, 9)
        out["exact_assignment"] = _named(exact, rows, cols)
    else:
        out["exact_total"] = None
        out["note"] = "Input too large for the built-in exact check; compare on a small sample."
    return out


def cli_demo() -> dict[str, Any]:
    """Synthetic examples only: community-center class assignment, budget selection, work order."""
    rng = random.Random(5)
    learners, classes, caps = 8, 3, [3, 3, 2]
    # synthetic dissatisfaction cost 1..9 per (learner, community-center class)
    costs = [[float(rng.randint(1, 9)) for _ in range(classes)] for _ in range(learners)]
    greedy = greedy_assign_with_capacity(costs, caps)
    improved = improve_assignment_by_swap(greedy, costs, caps)
    exact, exact_total = brute_force_assignment(costs, caps)
    hung, hung_total = hungarian_with_capacity(costs, caps)

    # seats < learners, up to 2 classes per learner, at most one class per time slot
    rng = random.Random(21)
    lim_caps, slots = [3, 2, 2, 1], ["am", "am", "pm", "pm"]
    scores = [[float(rng.randint(0, 5)) for _ in range(4)] for _ in range(10)]
    single, single_cost = hungarian_with_capacity([[-s for s in r] for r in scores], lim_caps,
                                                  allow_unassigned=True, unassigned_cost=0.0)
    single_flow = assignment_flow(scores, 1, lim_caps, maximize=True)
    multi = assignment_flow(scores, 2, lim_caps, groups=slots, maximize=True)

    values = [60, 100, 120]
    weights = [10, 20, 30]
    budget = 50
    rng = random.Random(11)
    g_val, g_items = greedy_knapsack(values, weights, budget)
    k_val, k_items = knapsack_01(values, weights, budget)

    pts = [(rng.randint(0, 20), rng.randint(0, 20)) for _ in range(8)]
    dist = [[float(abs(x1 - x2) + abs(y1 - y2)) for x2, y2 in pts] for x1, y1 in pts]
    nn = nearest_neighbor_order(dist, 0)
    opt = two_opt(nn, dist, closed=False)
    bf, bf_len = brute_force_order(dist, 0, closed=False)

    return {
        "note": "Synthetic demo. Shows baseline -> improvement -> small exact comparison.",
        "class_assignment": {
            "rows": learners, "columns": classes, "capacities": caps,
            "baseline_greedy_total": round(assignment_cost(greedy, costs), 6),
            "after_swap_total": round(assignment_cost(improved, costs), 6),
            "exact_brute_force_total": round(exact_total, 6),
            "exact_hungarian_total": round(hung_total, 6),
            "gap_vs_exact": round(assignment_cost(improved, costs) - exact_total, 6),
            "capacity_violations": len(constraint_report(improved, caps))},
        "class_assignment_with_limits": {
            "rows": len(scores), "capacities": lim_caps, "time_slots": slots,
            "single_pick_hungarian_score": round(-single_cost, 6),
            "single_pick_flow_score": round(single_flow["objective"], 6),
            "single_pick_unassigned_rows": sum(c is None for c in single),
            "two_picks_flow_score": round(multi["objective"], 6),
            "two_picks_unfilled_slots": multi["unfilled"],
            "violations": len(constraint_report(multi["assignment"], lim_caps, row_limits=2, groups=slots))},
        "budget_selection": {
            "budget": budget, "greedy_value": g_val, "greedy_items": g_items,
            "dp_value": k_val, "dp_items": k_items, "gap": k_val - g_val},
        "work_order": {
            "nodes": len(pts), "nearest_neighbor_length": order_length(nn, dist),
            "two_opt_length": order_length(opt, dist), "brute_force_length": bf_len,
            "gap_vs_exact": order_length(opt, dist) - bf_len},
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic optimization building blocks.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("assign", help="minimum-cost assignment from a CSV cost matrix")
    pa.add_argument("--costs", required=True, help="CSV matrix (optional header row and name column)")
    pa.add_argument("--capacities", default=None, help="comma-separated column capacities, e.g. 2,2,1")
    sub.add_parser("demo", help="built-in synthetic comparison")
    args = parser.parse_args(argv)
    try:
        result = cli_assign(args.costs, args.capacities) if args.cmd == "assign" else cli_demo()
    except (InputError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
