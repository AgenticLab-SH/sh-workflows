"""합성 연습 자료 검사: exercises/donation-packing (실제 대회 문제·업무 데이터 아님).

진행자 표의 정제 수치·기준선·정확해를 데이터에서 독립 계산해 대조한다.
정확해는 작은 입력 전수 탐색(가지치기)으로 구한다. 표준 라이브러리만, 오프라인.
"""
import csv
import hashlib
import io
import math
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'exercises' / 'donation-packing'
FILES = ['BRIEF.md', 'FACILITATOR.md', 'items.csv']
SYNTH = '합성 연습 자료, 실제 대회 문제·업무 데이터 아님'
CAP_W, CAP_V = 10_000, 40_000  # g, mL
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_session_allocation_fixture import BLOCKED  # noqa: E402


def text(name):
    return (EX / name).read_text(encoding='utf-8')


def grams(v):
    v = v.strip().lower()
    if not v:
        return None
    if v.endswith('kg'):
        return round(float(v[:-2]) * 1000)
    if v.endswith('g'):
        return round(float(v[:-1]))
    return round(float(v) * 1000)  # 단위 없는 숫자는 kg


def millilitres(v):
    v = v.strip().lower()
    if v.endswith('ml'):
        return round(float(v[:-2]))
    if v.endswith('l'):
        return round(float(v[:-1]) * 1000)
    return round(float(v) * 1000)  # 단위 없는 숫자는 L


def clean():
    raw = list(csv.DictReader(io.StringIO(text('items.csv'))))
    latest = {}
    for r in raw:
        k = r['item_id'].strip().upper()
        t = datetime.fromisoformat(r['logged_at'])
        if k not in latest or t > latest[k][0]:
            latest[k] = (t, r)
    eff = {k: r for k, (_, r) in sorted(latest.items())}
    items, missing, oversize = [], [], []
    for k, r in eff.items():
        w, v = grams(r['weight']), millilitres(r['volume'])
        if w is None:
            missing.append(k)
        elif w > CAP_W or v > CAP_V:
            oversize.append(k)
        else:
            items.append((k, w, v, r['category'].strip(), r['set_id'].strip()))
    return raw, eff, items, missing, oversize


def conflict(cats, c):
    return (c == '액체' and '종이' in cats) or (c == '종이' and '액체' in cats)


def fits(box, it):
    return box['w'] + it[1] <= CAP_W and box['v'] + it[2] <= CAP_V and not conflict(box['c'], it[3])


def splits(boxes):
    where = {}
    for i, b in enumerate(boxes):
        for it in b['items']:
            if it[4]:
                where.setdefault(it[4], set()).add(i)
    return sum(1 for s in where.values() if len(s) > 1)


def first_fit(order):
    boxes = []
    for it in order:
        for b in boxes:
            if fits(b, it):
                b['items'].append(it); b['w'] += it[1]; b['v'] += it[2]; b['c'].add(it[3])
                break
        else:
            boxes.append({'items': [it], 'w': it[1], 'v': it[2], 'c': {it[3]}})
    return boxes


def exact(items):
    """Lexicographic optimum (box count, then set splits) by exhaustive search."""
    order = sorted(items, key=lambda x: (-x[2], x[0]))
    best = [math.inf, math.inf]

    def dfs(i, boxes):
        if len(boxes) > best[0]:
            return
        if i == len(order):
            key = (len(boxes), splits(boxes))
            if key < tuple(best):
                best[0], best[1] = key
            return
        it = order[i]
        for b in boxes:
            if fits(b, it):
                added = it[3] not in b['c']
                b['items'].append(it); b['w'] += it[1]; b['v'] += it[2]; b['c'].add(it[3])
                dfs(i + 1, boxes)
                b['items'].pop(); b['w'] -= it[1]; b['v'] -= it[2]
                if added:
                    b['c'].discard(it[3])
        if len(boxes) + 1 <= best[0]:
            boxes.append({'items': [it], 'w': it[1], 'v': it[2], 'c': {it[3]}})
            dfs(i + 1, boxes)
            boxes.pop()

    dfs(0, [])
    return best[0], best[1]


def expected_table():
    m = re.search(r'<!-- expected-start -->(.*?)<!-- expected-end -->', text('FACILITATOR.md'), re.S)
    assert m, 'expected table markers missing'
    out = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[1].startswith('`'):
            out[cells[1].strip('`')] = int(cells[2])
    return out


def stats():
    raw, eff, items, missing, oversize = clean()
    filled_w = [r['weight'].strip().lower() for r in eff.values() if r['weight'].strip()]
    vols = [r['volume'].strip().lower() for r in eff.values()]
    tw, tv = sum(i[1] for i in items), sum(i[2] for i in items)
    base = first_fit(sorted(items, key=lambda x: (-x[2], x[0])))
    best_boxes, best_splits = exact(items)
    return {
        'raw_rows': len(raw),
        'unique_items': len(eff),
        'dropped_duplicate_rows': len(raw) - len(eff),
        'id_needs_normalizing_rows': sum(1 for r in raw if r['item_id'] != r['item_id'].strip().upper()),
        'missing_weight_items': len(missing),
        'oversize_items': len(oversize),
        'packable_items': len(items),
        'weight_not_kg_text': sum(1 for w in filled_w if not w.endswith('kg')),
        'volume_not_l_text': sum(1 for v in vols if not (v.endswith('l') and not v.endswith('ml'))),
        'total_weight_g': tw,
        'total_volume_ml': tv,
        'box_lower_bound': max(math.ceil(tw / CAP_W), math.ceil(tv / CAP_V)),
        'baseline_boxes': len(base),
        'optimal_boxes': best_boxes,
        'optimal_set_splits': best_splits,
    }, base


class DonationPackingFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats, cls.baseline = stats()

    def test_expected_numbers_match_facilitator(self):
        table = expected_table()
        self.assertEqual(set(table), set(self.stats))
        for k, v in self.stats.items():
            self.assertEqual(table[k], v, k)

    def test_baseline_respects_hard_constraints(self):
        for b in self.baseline:
            self.assertLessEqual(b['w'], CAP_W)
            self.assertLessEqual(b['v'], CAP_V)
            self.assertFalse({'액체', '종이'} <= b['c'])

    def test_teaching_gaps_exist(self):
        s = self.stats
        self.assertGreater(s['baseline_boxes'], s['optimal_boxes'])
        self.assertEqual(s['optimal_boxes'], s['box_lower_bound'])
        self.assertGreater(s['optimal_set_splits'], 0)

    def test_intended_edge_cases_present(self):
        raw = list(csv.DictReader(io.StringIO(text('items.csv'))))
        i05 = [r for r in raw if r['item_id'].strip().upper() == 'I05']
        self.assertEqual(len(i05), 2)
        self.assertGreater(i05[0]['logged_at'], i05[1]['logged_at'])  # later file row is older
        self.assertTrue(any(re.fullmatch(r'\d+(\.\d+)?', r['weight'].strip()) for r in raw))
        self.assertTrue(any(r['weight'].strip().lower().endswith('g') and
                            not r['weight'].strip().lower().endswith('kg') for r in raw))
        self.assertTrue(any(r['volume'].strip().lower().endswith('ml') for r in raw))

    def test_marked_synthetic_and_no_blocked_words(self):
        for name in FILES:
            body = text(name)
            if name.endswith('.md'):
                self.assertIn(SYNTH, '\n'.join(body.splitlines()[:3]), name)
            else:
                self.assertFalse(body.startswith('#'), name)
            low = body.lower()
            for n in {n for n, _ in BLOCKED}:
                for i in range(len(low) - n + 1):
                    h = hashlib.sha256(low[i:i + n].encode('utf-8')).hexdigest()[:16]
                    self.assertNotIn((n, h), BLOCKED, f'{name}: 위치 {i}')

    def test_brief_does_not_reveal_hidden_rules(self):
        brief = text('BRIEF.md')
        for hidden in ('10kg', '40L', '액체', '단위 없는 숫자는'):
            self.assertNotIn(hidden, brief)


if __name__ == '__main__':
    unittest.main()
