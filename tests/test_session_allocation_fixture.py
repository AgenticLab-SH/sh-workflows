"""합성 연습 자료 검사: exercises/session-allocation (실제 대회 문제·업무 데이터 아님).

정제 수치만 독립 계산해 FACILITATOR.md 표와 비교한다. 배정 알고리즘은 포함하지 않는다.
표준 라이브러리만 사용하며 오프라인에서 실행된다.
"""
import csv
import hashlib
import io
import re
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'exercises' / 'session-allocation'
FILES = ['BRIEF.md', 'FACILITATOR.md', 'participants.csv', 'sessions.csv']
SYNTH = '합성 연습 자료, 실제 대회 문제·업무 데이터 아님'

# 공개 저장소에서 피할 영역 단어 목록을 평문으로 다시 노출하지 않도록
# (글자 수, sha256 앞 16자리)로만 보관한다. 영문은 소문자 기준.
BLOCKED = {
    (2, '5eb36550b4cd74af'), (2, 'f47bcbbc672a0ede'), (2, 'fb84fa7f86eac62e'),
    (2, 'c5d62126c655bab0'), (2, 'f56a93ccff08be8e'), (2, '560d1e948136e687'),
    (3, '888da7692e098e28'), (2, 'd5266138a565f6aa'), (2, '02cb09e20c94f203'),
    (2, '976934e54b1b9841'), (2, '82c5fe62d75b8c38'), (2, '5babf0a60dbf4607'),
    (2, 'edebf005949ad339'), (3, '04e027e4990a203f'), (5, '8a84e406c08ac959'),
    (7, '48f42260a8448caa'), (9, 'bf816809a4d8aa98'), (7, 'b404ed3c370c8c26'),
    (7, '068b7e6c97f2284a'), (8, 'db8d1b6d64e4ec90'), (7, 'fde2b189f66a29e2'),
    (6, 'b67edcdb95503aae'), (8, '7ff87f6b41ccc0c3'), (9, '7dd0c85c947c5e8f'),
    (2, '9fcf20767362a62b'), (2, '680ce6b5107e3b64'), (2, '57bcfb6e119961a2'),
    (6, 'e8ef1d2b609adbba'),
}


def read_text(name):
    return (EX / name).read_text(encoding='utf-8')


def read_rows(name):
    lines = [ln for ln in read_text(name).splitlines() if not ln.startswith('#')]
    return list(csv.DictReader(io.StringIO('\n'.join(lines))))


def norm_id(raw):
    return raw.strip().upper()


def to_minutes(raw):
    v = raw.strip().lower()
    if v.endswith('분'):
        return float(v[:-1])
    if v.endswith('h'):
        return float(v[:-1]) * 60
    return float(v)  # 단위 없는 숫자는 분


def cleaned():
    """FACILITATOR.md 정제 규칙의 최소 구현(배정 없음)."""
    sessions = {r['session_id']: r for r in read_rows('sessions.csv')}
    open_ids = {k for k, r in sessions.items() if int(r['capacity']) > 0}
    raw = read_rows('participants.csv')
    latest = {}
    for r in raw:
        pid = norm_id(r['participant_id'])
        ts = datetime.fromisoformat(r['submitted_at'])
        if pid not in latest or ts > latest[pid][0]:
            latest[pid] = (ts, r)
    eff = [r for _, r in latest.values()]
    choices = [r[f'choice{i}'].strip() for r in eff for i in (1, 2, 3)]
    filled = [c for c in choices if c]
    stats = {
        'raw_rows': len(raw),
        'unique_participants': len(latest),
        'dropped_duplicate_rows': len(raw) - len(latest),
        'duplicated_ids': sum(1 for pid in latest
                              if sum(norm_id(r['participant_id']) == pid for r in raw) > 1),
        'id_needs_normalizing_rows': sum(1 for r in raw
                                         if r['participant_id'] != norm_id(r['participant_id'])),
        'sessions_total': len(sessions),
        'sessions_open': len(open_ids),
        'sessions_closed': len(sessions) - len(open_ids),
        'open_capacity_total': sum(int(sessions[k]['capacity']) for k in open_ids),
        'slots_with_multiple_sessions': sum(
            1 for s in {r['slot'] for r in sessions.values()}
            if sum(r['slot'] == s for r in sessions.values()) > 1),
        'duration_needs_conversion': sum(1 for r in sessions.values()
                                         if not r['duration'].strip().endswith('분')),
        'duration_hour_unit': sum(1 for r in sessions.values()
                                  if r['duration'].strip().lower().endswith('h')),
        'duration_unitless': sum(1 for r in sessions.values()
                                 if re.fullmatch(r'\d+', r['duration'].strip())),
        'fixed_assignments': sum(1 for r in eff if r['fixed'].strip()),
        'blank_choice_cells': len(choices) - len(filled),
        'participants_without_choices': sum(
            1 for r in eff if not any(r[f'choice{i}'].strip() for i in (1, 2, 3))),
        'choices_unknown_session': sum(1 for c in filled if c not in sessions),
        'choices_closed_session': sum(1 for c in filled if c in sessions and c not in open_ids),
        'valid_choice_cells': sum(1 for c in filled if c in open_ids),
    }
    minutes = {k: to_minutes(r['duration']) for k, r in sessions.items()}
    return stats, minutes, eff, raw, sessions


def facilitator_table():
    m = re.search(r'<!-- expected-start -->(.*?)<!-- expected-end -->',
                  read_text('FACILITATOR.md'), re.S)
    assert m, 'FACILITATOR.md 기대 수치 표 표식이 없습니다'
    out = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[1].startswith('`'):
            out[cells[1].strip('`')] = int(cells[2])
    return out


class SessionAllocationFixtureTest(unittest.TestCase):
    def test_files_exist_and_marked_synthetic(self):
        for name in FILES:
            text = read_text(name)
            if name.endswith('.md'):
                self.assertIn(SYNTH, '\n'.join(text.splitlines()[:3]), name)
            else:  # CSV는 일반 CSV 도구와 호환되도록 주석 없이 첫 줄이 헤더다.
                self.assertFalse(text.startswith('#'), name)

    def test_headers(self):
        self.assertEqual(list(read_rows('participants.csv')[0].keys()),
                         ['participant_id', 'name', 'group', 'choice1', 'choice2',
                          'choice3', 'submitted_at', 'fixed'])
        self.assertEqual(list(read_rows('sessions.csv')[0].keys()),
                         ['session_id', 'title', 'slot', 'capacity', 'duration'])

    def test_expected_numbers_match_facilitator(self):
        stats, _, _, _, _ = cleaned()
        table = facilitator_table()
        self.assertEqual(set(table), set(stats))
        for k, v in stats.items():
            self.assertEqual(table[k], v, k)

    def test_duration_minutes(self):
        _, minutes, _, _, _ = cleaned()
        self.assertEqual(minutes, {'S01': 90, 'S02': 60, 'S03': 90, 'S04': 120,
                                   'S05': 60, 'S06': 120, 'S07': 45, 'S08': 90})

    def test_intended_edge_cases_present(self):
        stats, _, eff, raw, sessions = cleaned()
        self.assertTrue(30 <= stats['raw_rows'] <= 40)
        self.assertTrue(7 <= stats['sessions_total'] <= 9)
        self.assertGreaterEqual(stats['duplicated_ids'], 3)
        self.assertGreaterEqual(stats['id_needs_normalizing_rows'], 2)
        self.assertGreater(stats['blank_choice_cells'], 0)
        self.assertEqual(stats['choices_unknown_session'], 1)
        self.assertGreater(stats['choices_closed_session'], 0)
        self.assertTrue(2 <= stats['fixed_assignments'] <= 3)
        self.assertEqual(stats['sessions_closed'], 1)
        self.assertGreaterEqual(stats['slots_with_multiple_sessions'], 1)
        self.assertGreater(stats['duration_hour_unit'], 0)
        self.assertGreater(stats['duration_unitless'], 0)
        for r in raw:  # ISO 8601 일관
            self.assertRegex(r['submitted_at'],
                             r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$')
        # 파일 순서가 아니라 신청시각이 늦은 행이 유효해야 하는 사례가 있다.
        p003 = [r for r in raw if norm_id(r['participant_id']) == 'P003']
        self.assertLess(p003[1]['submitted_at'], p003[0]['submitted_at'])
        # 고정 배정 세션은 모두 존재하고 개설된 세션이다.
        for r in eff:
            if r['fixed'].strip():
                self.assertGreater(int(sessions[r['fixed'].strip()]['capacity']), 0)

    def test_names_are_placeholder(self):
        for r in read_rows('participants.csv'):
            self.assertRegex(r['name'], r'^수강생\d{2}$')
            self.assertRegex(r['group'], r'^가상모임[A-Z]$')

    def test_brief_baseline_and_facilitator_rules(self):
        self.assertIn('신청시각이 빠른 수강생부터 한 명씩, 그 사람의 희망 순서대로 가능한 만큼 배정',
                      read_text('BRIEF.md'))
        fac = read_text('FACILITATOR.md')
        for phrase in ['그 안으로 진행해도 됩니다', '질문이 지목한 사실만',
                       '정원 우선 규칙과 점수 합이 다른 배정을 낼 때', '결과 CSV 열·정렬']:
            self.assertIn(phrase, fac)
        # 답하는 구체 질문 예는 물음표 하나, 열린 표현 없음.
        m = re.search(r'\*\*답하는 구체 질문 예\*\*.*?\n\n(.*?)\n\n', fac, re.S)
        self.assertIsNotNone(m)
        for line in m.group(1).splitlines():
            self.assertEqual(line.count('?'), 1, line)
            self.assertNotIn('어떻게', line)

    def test_no_blocked_domain_words(self):
        lengths = {n for n, _ in BLOCKED}
        for name in FILES:
            text = read_text(name).lower()
            for n in lengths:
                for i in range(len(text) - n + 1):
                    h = hashlib.sha256(text[i:i + n].encode('utf-8')).hexdigest()[:16]
                    self.assertNotIn((n, h), BLOCKED, f'{name}: 위치 {i}')


if __name__ == '__main__':
    unittest.main()
