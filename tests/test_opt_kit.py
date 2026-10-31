"""Deterministic, offline tests for tools/opt_kit.py on synthetic data."""
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from kit_utils import InputError
import opt_kit as ok


def rand_matrix(rng, rows, cols, lo=0, hi=20):
    return [[float(rng.randint(lo, hi)) for _ in range(cols)] for _ in range(rows)]


class AssignmentTest(unittest.TestCase):
    def test_hungarian_matches_brute_force_square(self):
        rng = random.Random(42)
        for _ in range(8):
            m = rand_matrix(rng, 6, 6)
            assignment, total = ok.hungarian(m)
            self.assertEqual(sorted(assignment), list(range(6)))
            _, best = ok.brute_force_assignment(m)
            self.assertAlmostEqual(total, best)
            self.assertAlmostEqual(total, ok.assignment_cost(assignment, m))

    def test_hungarian_rectangular_both_directions(self):
        rng = random.Random(7)
        for _ in range(5):
            wide = rand_matrix(rng, 4, 6)
            a, total = ok.hungarian(wide)
            self.assertEqual(len(set(a)), 4)
            self.assertAlmostEqual(total, ok.brute_force_assignment(wide)[1])
            tall = [list(col) for col in zip(*wide)]  # 6 x 4
            b, total_t = ok.hungarian(tall)
            self.assertEqual(sum(x is None for x in b), 2)
            self.assertEqual(len({x for x in b if x is not None}), 4)
            self.assertAlmostEqual(total_t, total)

    def test_capacity_greedy_swap_feasible_and_not_better_than_exact(self):
        rng = random.Random(3)
        for _ in range(10):
            caps = [3, 2, 2]
            m = rand_matrix(rng, 7, 3, 1, 9)
            greedy = ok.greedy_assign_with_capacity(m, caps)
            improved = ok.improve_assignment_by_swap(greedy, m, caps, max_rounds=50)
            self.assertEqual(ok.constraint_report(greedy, caps), [])
            self.assertEqual(ok.constraint_report(improved, caps), [])
            _, exact = ok.brute_force_assignment(m, caps)
            g, i = ok.assignment_cost(greedy, m), ok.assignment_cost(improved, m)
            self.assertLessEqual(i, g + 1e-9)
            self.assertGreaterEqual(i, exact - 1e-9)
            h, h_total = ok.hungarian_with_capacity(m, caps)
            self.assertEqual(ok.constraint_report(h, caps), [])
            self.assertAlmostEqual(h_total, exact)

    def test_constraint_report_lists_excess(self):
        r = ok.constraint_report([0, 0, 0, 1], [2, 2])
        self.assertEqual(r, [{'column': 0, 'assigned': 3, 'capacity': 2, 'excess': 1}])

    def test_swap_does_not_mutate_input(self):
        m = [[1.0, 5.0], [5.0, 1.0]]
        start = [1, 0]
        self.assertEqual(ok.improve_assignment_by_swap(start, m, [1, 1]), [0, 1])
        self.assertEqual(start, [1, 0])


def brute_single(costs, caps, allow_unassigned=False, unassigned_cost=0.0, banned=()):
    """Exact one-column-per-row assignment by enumeration (test reference)."""
    n, m = len(costs), len(costs[0])
    best = math.inf
    for choice in itertools.product(*[[j for j in range(m) if (i, j) not in banned]
                                      + ([None] if allow_unassigned else []) for i in range(n)]):
        load = [0] * m
        for c in choice:
            if c is not None:
                load[c] += 1
        if any(load[j] > caps[j] for j in range(m)):
            continue
        best = min(best, sum(costs[i][c] if c is not None else unassigned_cost for i, c in enumerate(choice)))
    return best


def brute_multi(a, k, caps, groups, banned=(), maximize=False, unassigned_cost=0.0, fixed=()):
    """Exact several-columns-per-row assignment by depth-first enumeration (test reference).

    fixed pairs must appear in the row's choice (they still count toward k, groups, capacity).
    """
    n, m = len(a), len(a[0])
    grp = list(range(m)) if groups is None else groups
    must = [{j for r, j in fixed if r == i} for i in range(n)]
    options = []
    for i in range(n):
        opts = []
        for size in range(k + 1):
            for cols in itertools.combinations(range(m), size):
                if len({grp[j] for j in cols}) == size and all((i, j) not in banned for j in cols) \
                        and must[i] <= set(cols):
                    opts.append((cols, sum(a[i][j] for j in cols) + unassigned_cost * (k - size)))
        options.append(opts)
    sign = -1 if maximize else 1
    best = [math.inf]
    load = [0] * m

    def dfs(i, acc):
        if i == n:
            best[0] = min(best[0], sign * acc)
            return
        for cols, val in options[i]:
            if all(load[j] < caps[j] for j in cols):
                for j in cols:
                    load[j] += 1
                dfs(i + 1, acc + val)
                for j in cols:
                    load[j] -= 1

    dfs(0, 0.0)
    return sign * best[0]


class LimitedAssignmentTest(unittest.TestCase):
    def test_hungarian_allow_unassigned_and_forbidden_match_enumeration(self):
        rng = random.Random(101)
        for _ in range(12):
            n, m = 6, 3
            scores = rand_matrix(rng, n, m, 0, 9)
            costs = [[-s for s in r] for r in scores]
            caps = [rng.randint(0, 2) for _ in range(m)]
            banned = {(rng.randrange(n), rng.randrange(m)) for _ in range(4)}
            assignment, total = ok.hungarian_with_capacity(costs, caps, allow_unassigned=True,
                                                           unassigned_cost=0.0, forbidden=banned)
            self.assertTrue(all((i, c) not in banned for i, c in enumerate(assignment) if c is not None))
            self.assertEqual(ok.constraint_report(assignment, caps), [])
            self.assertAlmostEqual(total, brute_single(costs, caps, True, 0.0, banned))
            g = ok.greedy_assign_with_capacity(costs, caps, allow_unassigned=True, unassigned_cost=0.0,
                                               forbidden=banned)
            self.assertTrue(all((i, c) not in banned for i, c in enumerate(g) if c is not None))
            self.assertEqual(ok.constraint_report(g, caps), [])
            self.assertGreaterEqual(ok.assignment_cost(g, costs), total - 1e-9)

    def test_unassigned_cost_is_counted(self):
        a, total = ok.hungarian_with_capacity([[1.0, 2.0], [1.0, 9.0], [4.0, 9.0]], [1, 1],
                                              allow_unassigned=True, unassigned_cost=5.0)
        self.assertEqual(a, [1, 0, None])
        self.assertAlmostEqual(total, 1 + 2 + 5)

    def test_forbidden_never_used(self):
        a, total = ok.hungarian_with_capacity([[0.0, 10.0], [10.0, 0.0]], [1, 1], forbidden={(0, 0)})
        self.assertEqual(a, [1, 0])
        self.assertAlmostEqual(total, 20)
        with self.assertRaises(InputError):
            ok.hungarian_with_capacity([[1.0, 2.0], [3.0, 4.0]], [1, 1], forbidden={(0, 0), (0, 1)})
        a2, _ = ok.hungarian_with_capacity([[1.0, 2.0], [3.0, 4.0]], [1, 1], allow_unassigned=True,
                                           unassigned_cost=100.0, forbidden={(0, 0), (0, 1)})
        self.assertIsNone(a2[0])
        with self.assertRaises(InputError):
            ok.greedy_assign_with_capacity([[1.0, 2.0], [3.0, 4.0]], [1, 1], forbidden={(0, 0), (0, 1)})

    def test_min_cost_flow_known_graph(self):
        edges = [(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)]
        r = ok.min_cost_flow(4, edges, 0, 3)
        self.assertEqual((r['flow'], r['cost'], r['edge_flows']), (3, 10, [2, 1, 1, 1, 2]))
        r2 = ok.min_cost_flow(4, edges, 0, 3, max_flow=2)
        self.assertEqual((r2['flow'], r2['cost']), (2, 6))
        self.assertEqual(ok.min_cost_flow(3, [(0, 1, 5, 1)], 0, 2)['flow'], 0)
        neg = ok.min_cost_flow(3, [(0, 1, 1, -4), (1, 2, 1, 1), (0, 2, 1, 0)], 0, 2)
        self.assertEqual((neg['flow'], neg['cost']), (2, -3))
        with self.assertRaises(InputError):
            ok.min_cost_flow(4, [(0, 1, 1, 0), (1, 2, 1, -2), (2, 1, 1, 1), (2, 3, 1, 0)], 0, 3)

    def test_assignment_flow_matches_brute_force(self):
        rng = random.Random(202)
        for case in range(10):
            n, m = 4, 4
            groups = ['am', 'am', 'pm', 'pm']
            scores = rand_matrix(rng, n, m, 0, 9)
            caps = [rng.randint(0, 2) for _ in range(m)]
            banned = {(rng.randrange(n), rng.randrange(m)) for _ in range(3)}
            r = ok.assignment_flow(scores, 2, caps, groups=groups, maximize=True, forbidden=banned)
            self.assertEqual(ok.constraint_report(r['assignment'], caps, row_limits=2, groups=groups), [])
            self.assertTrue(all((i, j) not in banned for i, cols in enumerate(r['assignment']) for j in cols))
            self.assertAlmostEqual(r['objective'], brute_multi(scores, 2, caps, groups, banned, maximize=True))
            costs = rand_matrix(rng, n, 3, 1, 9)
            caps3 = [rng.randint(1, 3) for _ in range(3)]
            r2 = ok.assignment_flow(costs, 2, caps3, unassigned_cost=6.0)
            self.assertEqual(ok.constraint_report(r2['assignment'], caps3, row_limits=2), [])
            self.assertAlmostEqual(r2['objective'], brute_multi(costs, 2, caps3, None, unassigned_cost=6.0))

    def test_assignment_flow_single_pick_equals_hungarian(self):
        rng = random.Random(303)
        for _ in range(6):
            scores = rand_matrix(rng, 7, 3, 0, 9)
            caps = [rng.randint(0, 3) for _ in range(3)]
            r = ok.assignment_flow(scores, 1, caps, maximize=True)
            _, h = ok.hungarian_with_capacity([[-s for s in row] for row in scores], caps,
                                              allow_unassigned=True, unassigned_cost=0.0)
            self.assertAlmostEqual(r['objective'], -h)

    def test_unassigned_cost_required_when_allowed(self):
        costs = [[1.0, 2.0], [3.0, 4.0], [2.0, 1.0]]
        for fn in (ok.hungarian_with_capacity, ok.greedy_assign_with_capacity):
            with self.assertRaises(InputError) as cm:
                fn(costs, [1, 1], allow_unassigned=True)
            self.assertIn('unassigned_cost is required', str(cm.exception))
            self.assertIn('leaves everyone unassigned', str(cm.exception))
        # the pitfall the error prevents: nonnegative costs with u=0 assign nobody
        a, total = ok.hungarian_with_capacity(costs, [1, 1], allow_unassigned=True, unassigned_cost=0.0)
        self.assertEqual((a, total), ([None, None, None], 0.0))
        # existing calls without allow_unassigned keep working
        self.assertEqual(ok.hungarian_with_capacity(costs, [2, 1])[1], 1.0 + 3.0 + 1.0)
        self.assertEqual(len(ok.greedy_assign_with_capacity(costs, [2, 1])), 3)

    def test_swap_rejects_unassigned_rows_with_matching_hint(self):
        costs = [[1.0, 2.0], [3.0, 4.0], [2.0, 1.0]]
        g = ok.greedy_assign_with_capacity(costs, [1, 1], allow_unassigned=True, unassigned_cost=5.0)
        self.assertIn(None, g)
        with self.assertRaises(InputError) as cm:
            ok.improve_assignment_by_swap(g, costs, [1, 1])
        msg = str(cm.exception)
        self.assertNotIn('allow_unassigned', msg)
        self.assertIn('drop the unassigned', msg)
        self.assertIn('assignment_flow', msg)
        keep = [i for i, c in enumerate(g) if c is not None]
        sub = ok.improve_assignment_by_swap([g[i] for i in keep], [costs[i] for i in keep], [1, 1])
        self.assertEqual(ok.constraint_report(sub, [1, 1]), [])

    def test_assignment_flow_fixed_matches_brute_force(self):
        rng = random.Random(404)
        groups = ['am', 'am', 'pm', 'pm']
        checked = 0
        for _ in range(40):
            n, m = 4, 4
            scores = rand_matrix(rng, n, m, 0, 9)
            caps = [rng.randint(1, 2) for _ in range(m)]
            banned = {(rng.randrange(n), rng.randrange(m)) for _ in range(2)}
            fixed = []
            for _ in range(rng.randint(1, 2)):
                i, j = rng.randrange(n), rng.randrange(m)
                if (i, j) not in banned and all(r != i or groups[c] != groups[j] for r, c in fixed) \
                        and sum(c == j for _, c in fixed) < caps[j]:
                    fixed.append((i, j))
            if not fixed:
                continue
            for maximize, u in ((True, 0.0), (False, 6.0)):
                r = ok.assignment_flow(scores, 2, caps, groups=groups, maximize=maximize, unassigned_cost=u,
                                       forbidden=banned, fixed=fixed)
                self.assertEqual(r['conflicts'], [])
                for i, j in fixed:
                    self.assertIn(j, r['assignment'][i])
                self.assertEqual(ok.constraint_report(r['assignment'], caps, row_limits=2, groups=groups), [])
                self.assertTrue(all((i, j) not in banned for i, cols in enumerate(r['assignment']) for j in cols))
                self.assertAlmostEqual(r['fixed_total'], sum(scores[i][j] for i, j in fixed))
                self.assertAlmostEqual(r['objective'], brute_multi(scores, 2, caps, groups, banned, maximize=maximize,
                                                                    unassigned_cost=u, fixed=fixed))
            checked += 1
        self.assertGreaterEqual(checked, 20)

    def test_assignment_flow_fixed_conflicts_are_listed(self):
        scores = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        r = ok.assignment_flow(scores, 1, [1, 1, 1], groups=['am', 'am', 'pm'], maximize=True,
                               forbidden={(1, 2)}, fixed=[(0, 0), (1, 0), (0, 1), (1, 2)])
        self.assertIsNone(r['assignment'])
        self.assertIsNone(r['objective'])
        kinds = sorted(c['kind'] for c in r['conflicts'])
        self.assertEqual(kinds, ['column_capacity', 'forbidden', 'group', 'row_limit', 'row_limit'])
        self.assertIn({'kind': 'column_capacity', 'column': 0, 'fixed': 2, 'capacity': 1}, r['conflicts'])
        self.assertIn({'kind': 'group', 'row': 0, 'group': 'am', 'columns': [0, 1], 'limit': 1}, r['conflicts'])
        dup = ok.assignment_flow(scores, 2, [2, 2, 2], fixed=[(0, 0), (0, 0)])
        self.assertEqual([c['kind'] for c in dup['conflicts']], ['duplicate'])
        with self.assertRaises(InputError):
            ok.assignment_flow(scores, 1, [1, 1, 1], fixed=[(0, 9)])
        ok_r = ok.assignment_flow(scores, 1, [1, 1, 1], maximize=True, fixed=[(0, 0)])
        self.assertEqual(ok_r['assignment'][0], [0])
        self.assertEqual(ok_r['conflicts'], [])

    def test_constraint_report_row_limits_and_groups(self):
        r = ok.constraint_report([[0, 1], [0, 0], None, 2], [1, 1, 1], row_limits=1, groups=['a', 'a', 'b'])
        self.assertEqual(r, [
            {'column': 0, 'assigned': 3, 'capacity': 1, 'excess': 2},
            {'row': 0, 'assigned': 2, 'limit': 1, 'excess': 1},
            {'row': 0, 'group': 'a', 'assigned': 2, 'limit': 1, 'excess': 1},
            {'row': 1, 'column': 0, 'assigned': 2, 'limit': 1, 'excess': 1},
            {'row': 1, 'assigned': 2, 'limit': 1, 'excess': 1},
            {'row': 1, 'group': 'a', 'assigned': 2, 'limit': 1, 'excess': 1},
        ])
        self.assertEqual(ok.constraint_report([[0], [1, 2]], [1, 1, 1], row_limits=[1, 2], groups=['a', 'a', 'b']), [])
        with self.assertRaises(InputError):
            ok.constraint_report([0, 1], [1, 1], row_limits=[1])


class SelectionPackingTest(unittest.TestCase):
    def test_knapsack_known_answer(self):
        self.assertEqual(ok.knapsack_01([60, 100, 120], [10, 20, 30], 50), (220, [1, 2]))
        self.assertEqual(ok.greedy_knapsack([60, 100, 120], [10, 20, 30], 50)[0], 160)
        self.assertEqual(ok.knapsack_01([5, 4], [7, 8], 3), (0, []))

    def test_knapsack_matches_enumeration(self):
        rng = random.Random(9)
        for _ in range(5):
            v = [rng.randint(1, 30) for _ in range(8)]
            w = [rng.randint(1, 15) for _ in range(8)]
            best = 0
            for mask in range(1 << 8):
                idx = [i for i in range(8) if mask >> i & 1]
                if sum(w[i] for i in idx) <= 30:
                    best = max(best, sum(v[i] for i in idx))
            val, chosen = ok.knapsack_01(v, w, 30)
            self.assertEqual(val, best)
            self.assertLessEqual(sum(w[i] for i in chosen), 30)

    def test_ffd_bounds(self):
        rng = random.Random(5)
        for _ in range(5):
            sizes = [rng.randint(1, 10) for _ in range(20)]
            bins = ok.first_fit_decreasing(sizes, 10)
            self.assertGreaterEqual(len(bins), math.ceil(sum(sizes) / 10))
            self.assertTrue(all(sum(sizes[i] for i in b) <= 10 for b in bins))
            self.assertEqual(sorted(i for b in bins for i in b), list(range(20)))

    def test_interval_schedule_and_pareto(self):
        self.assertEqual(ok.interval_schedule([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]), [0, 3, 4])
        self.assertEqual(ok.pareto_front([(1, 5), (2, 2), (3, 3), (5, 1)]), [0, 1, 3])


class MultiPackingTest(unittest.TestCase):
    """Synthetic shelf items: (weight, volume) with label conflicts. Not any exercise's data."""

    def test_first_fit_multi_respects_all_dimensions_and_conflicts(self):
        rng = random.Random(7)
        for _ in range(30):
            n = rng.randint(3, 12)
            sizes = [(rng.randint(1, 6), rng.randint(1, 9)) for _ in range(n)]
            labels = [rng.choice('xyz') for _ in range(n)]
            bad = [('x', 'y')]
            order = sorted(range(n), key=lambda i: -sizes[i][1])
            bins = ok.first_fit_multi(sizes, (8, 10), labels, bad, order)
            rep = ok.pack_report(bins, sizes, (8, 10), labels, bad)
            self.assertEqual(rep['violations'], [])
            self.assertGreaterEqual(len(bins), ok.bins_lower_bound(sizes, (8, 10)))
            self.assertEqual(sorted(i for b in bins for i in b), list(range(n)))

    def test_same_label_pair_forbids_two_of_a_kind(self):
        bins = ok.first_fit_multi([(1,), (1,), (1,)], (10,), ['a', 'a', 'b'], [('a', 'a')])
        self.assertEqual(bins, [[0, 2], [1]])

    def test_lower_bound_uses_largest_dimension(self):
        self.assertEqual(ok.bins_lower_bound([(5, 1), (5, 1), (5, 1)], (10, 10)), 2)
        self.assertEqual(ok.bins_lower_bound([(1, 9), (1, 9)], (10, 10)), 2)
        self.assertEqual(ok.bins_lower_bound([], (10,)), 0)

    def test_pack_report_finds_problems_and_splits(self):
        sizes = [(6,), (6,), (1,), (1,)]
        rep = ok.pack_report([[0, 1], [2], [2]], sizes, (10,), ['p', 'q', 'p', 'q'], [('p', 'q')],
                             groups=['g', '', 'g', None])
        kinds = sorted(v['kind'] for v in rep['violations'])
        self.assertEqual(kinds, ['capacity', 'conflict', 'missing', 'repeated'])
        self.assertEqual(rep['split_groups'], 1)

    def test_multi_input_errors(self):
        for call in (
            lambda: ok.first_fit_multi([(11, 1)], (10, 10)),
            lambda: ok.first_fit_multi([(1,)], (10, 10)),
            lambda: ok.first_fit_multi([(1,), (2,)], (10,), order=[0, 0]),
            lambda: ok.first_fit_multi([(1,)], (10,), incompatible=[('a', 'b')]),
            lambda: ok.bins_lower_bound([(1,)], (0,)),
        ):
            with self.assertRaises(InputError):
                call()


class OrderAndPathTest(unittest.TestCase):
    def setUp(self):
        rng = random.Random(11)
        self.cases = []
        for _ in range(4):
            pts = [(rng.randint(0, 30), rng.randint(0, 30)) for _ in range(8)]
            self.cases.append([[math.dist(p, q) for q in pts] for p in pts])

    def test_two_opt_not_worse_and_close_to_exact(self):
        for dist in self.cases:
            for closed in (False, True):
                nn = ok.nearest_neighbor_order(dist, 0)
                opt = ok.two_opt(nn, dist, closed=closed)
                self.assertEqual(opt[0], 0)
                self.assertEqual(sorted(opt), list(range(8)))
                nn_len = ok.order_length(nn, dist, closed)
                opt_len = ok.order_length(opt, dist, closed)
                _, exact = ok.brute_force_order(dist, 0, closed)
                self.assertLessEqual(opt_len, nn_len + 1e-9)
                self.assertGreaterEqual(opt_len, exact - 1e-9)

    def test_two_opt_asymmetric(self):
        d = [[0, 1, 9, 9], [9, 0, 1, 9], [9, 9, 0, 1], [1, 9, 9, 0]]
        opt = ok.two_opt([0, 2, 1, 3], d, closed=True)
        self.assertLessEqual(ok.order_length(opt, d, True), ok.order_length([0, 2, 1, 3], d, True))

    def test_dijkstra_known_graph(self):
        g = {'A': [('B', 4), ('C', 1)], 'C': [('B', 2), ('D', 5)], 'B': [('D', 1)], 'D': [], 'E': [('A', 1)]}
        dist, prev = ok.dijkstra(g, 'A')
        self.assertEqual(dist, {'A': 0, 'B': 3, 'C': 1, 'D': 4})
        self.assertEqual(ok.shortest_path(prev, 'D'), ['A', 'C', 'B', 'D'])
        self.assertEqual(ok.shortest_path(prev, 'E'), [])


class AnnealingTest(unittest.TestCase):
    def test_seed_determinism(self):
        dist = [[abs(i - j) * (1 + (i * j) % 3) for j in range(7)] for i in range(7)]

        def neighbor(order, rng):
            i, j = sorted(rng.sample(range(1, 7), 2))
            return order[:i] + order[i:j + 1][::-1] + order[j + 1:]

        def cost(order):
            return ok.order_length(order, dist)

        start = [0, 3, 6, 1, 5, 2, 4]
        r1 = ok.simulated_annealing(start, neighbor, cost, seed=1, iterations=500, start_temp=5)
        r2 = ok.simulated_annealing(start, neighbor, cost, seed=1, iterations=500, start_temp=5)
        self.assertEqual(r1, r2)
        self.assertLessEqual(r1[1], cost(start))


class InvalidInputTest(unittest.TestCase):
    def test_invalid_inputs_raise(self):
        cases = [
            lambda: ok.hungarian([]),
            lambda: ok.hungarian([[1, 2], [3]]),
            lambda: ok.hungarian([[1, float('nan')]]),
            lambda: ok.greedy_assign_with_capacity([[1, 2]], [-1, 2]),
            lambda: ok.greedy_assign_with_capacity([[1, 2], [3, 4], [5, 6]], [1, 1]),
            lambda: ok.brute_force_assignment([[1.0] * 3 for _ in range(13)], [5, 5, 5]),
            lambda: ok.knapsack_01([1, 2], [1], 3),
            lambda: ok.knapsack_01([1], [1.5], 3),
            lambda: ok.first_fit_decreasing([11], 10),
            lambda: ok.nearest_neighbor_order([[0, 1, 2], [1, 0, 3]], 0),
            lambda: ok.brute_force_order([[0] * 10 for _ in range(10)]),
            lambda: ok.dijkstra({'A': [('B', -1)], 'B': []}, 'A'),
            lambda: ok.simulated_annealing(0, lambda s, r: s, float, seed=0, cooling=1.5),
            lambda: ok.improve_assignment_by_swap([0, 0], [[1, 2], [3, 4]], [1, 1]),
            lambda: ok.hungarian_with_capacity([[1, 2]], [1, 1], forbidden={(0, 5)}),
            lambda: ok.min_cost_flow(3, [(0, 1, -1, 0)], 0, 2),
            lambda: ok.min_cost_flow(3, [(0, 3, 1, 0)], 0, 2),
            lambda: ok.assignment_flow([[1, 2]], 1, [1, 1], groups=['a']),
            lambda: ok.assignment_flow([[1, 2]], [1, 1], [1, 1]),
        ]
        for fn in cases:
            with self.assertRaises(InputError):
                fn()


class CLITest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'tools' / 'opt_kit.py'), *args],
                              text=True, capture_output=True, timeout=20)

    def test_demo_json(self):
        p = self.run_cli('demo')
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout)
        s = r['class_assignment']
        self.assertEqual(s['capacity_violations'], 0)
        self.assertLessEqual(s['after_swap_total'], s['baseline_greedy_total'])
        self.assertAlmostEqual(s['exact_brute_force_total'], s['exact_hungarian_total'])
        lim = r['class_assignment_with_limits']
        self.assertEqual(lim['violations'], 0)
        self.assertAlmostEqual(lim['single_pick_hungarian_score'], lim['single_pick_flow_score'])
        self.assertGreaterEqual(lim['two_picks_flow_score'], lim['single_pick_flow_score'])
        self.assertEqual(p.stdout, self.run_cli('demo').stdout)  # deterministic output
        self.assertEqual(r['budget_selection']['dp_value'], 220)
        self.assertGreaterEqual(r['work_order']['gap_vs_exact'], 0)

    def test_assign_json_with_header_and_capacity(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'costs.csv'
            p.write_text('staff,s1,s2\nkim,1,5\nlee,2,4\npark,3,1\n', encoding='utf8')
            r1 = self.run_cli('assign', '--costs', str(p))
            self.assertEqual(r1.returncode, 0, r1.stderr)
            j1 = json.loads(r1.stdout)
            self.assertEqual(j1['method'], 'hungarian')
            self.assertEqual(j1['unassigned_rows'], 1)
            r2 = self.run_cli('assign', '--costs', str(p), '--capacities', '2,1')
            self.assertEqual(r2.returncode, 0, r2.stderr)
            j2 = json.loads(r2.stdout)
            self.assertEqual(j2['capacity_violations'], [])
            self.assertEqual(j2['exact_total'], 4.0)
            self.assertEqual(set(j2['assignment']), {'kim', 'lee', 'park'})

    def test_assign_bad_input_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.csv'
            p.write_text('1,2\n3,x\n', encoding='utf8')
            r = self.run_cli('assign', '--costs', str(p))
            self.assertEqual(r.returncode, 2)
            self.assertIn('error', json.loads(r.stdout))


if __name__ == '__main__':
    unittest.main()
