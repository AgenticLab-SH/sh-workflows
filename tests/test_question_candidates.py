"""Offline tests for tools/question_candidates.py on synthetic temp CSV files."""
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools' / 'question_candidates.py'
sys.path.insert(0, str(ROOT / 'tools'))
import question_candidates as qc  # noqa: E402
import question_ledger as ql  # noqa: E402
from kit_utils import InputError  # noqa: E402

ROOMS = ('room_id,name,seats,booking_limit\n'
         'R1,작은 방,4,2h\nR2,큰 방,0,90분\nR3,창가 방,6,120\nR4,회의실 넷,-2,1.5h\n')
BOOKINGS = ('booking_id,room,member,requested_at\n'
            'B1,R1,M01,2026-11-02T09:00:00+09:00\n'
            ' b2,R2,M02,2026-11-02T09:00:00+09:00\n'
            'B2,R9,M03,2026-11-02T09:05:00+09:00\n'
            'B3,,M04,2026-11-02T09:07:00+09:00\n')


def run(*args):
    p = subprocess.run([sys.executable, '-B', str(TOOL), *args], text=True, capture_output=True,
                       timeout=20, encoding='utf-8')
    return p.returncode, p.stdout


class QuestionCandidatesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.rooms = self.dir / 'rooms.csv'
        self.bookings = self.dir / 'bookings.csv'
        self.rooms.write_text(ROOMS, encoding='utf-8')
        self.bookings.write_text(BOOKINGS, encoding='utf-8')

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, **kw):
        return qc.build([str(self.rooms), str(self.bookings)], **kw)

    def cats(self, res):
        return [r['category'] for r in res['rows']]

    def test_finds_expected_decision_points(self):
        res = self.build(refs=['bookings.csv:room=rooms.csv:room_id'])
        cats = self.cats(res)
        for c in ('unit', 'boundary', 'outlier', 'duplicate', 'tie_priority', 'missing', 'doc_data_gap'):
            self.assertIn(c, cats, c)
        unit_q = [r['question'] for r in res['rows'] if r['category'] == 'unit']
        self.assertTrue(any('단위 없는 숫자' in q for q in unit_q))
        dup_q = [r['question'] for r in res['rows'] if r['category'] == 'duplicate']
        self.assertTrue(any('requested_at 값이 가장 늦은 행' in q for q in dup_q))
        self.assertTrue(any('대문자로 맞춘' in q for q in dup_q))

    def test_rows_are_ledger_ready_and_pass_lint(self):
        code, out = run(str(self.rooms), str(self.bookings), '--ref', 'bookings.csv:room=rooms.csv:room_id')
        self.assertEqual(code, 0, out)
        rows = list(csv.DictReader(io.StringIO(out)))
        self.assertEqual(list(rows[0].keys()), qc.LEDGER_COLUMNS)
        self.assertTrue(all(r['status'] == 'open' and r['ask_count'] == '0' for r in rows))
        ledger = self.dir / 'ledger.csv'
        ledger.write_text(out, encoding='utf-8')
        res = ql.lint(ql.load_ledger(ledger))
        self.assertTrue(res['passed'], res['issues'])

    def test_cli_emits_utf8_under_legacy_windows_pipe_encoding(self):
        # The parent decodes UTF-8; a CP949 child previously broke that contract.
        env = {**os.environ, 'PYTHONIOENCODING': 'cp949'}
        result = subprocess.run([sys.executable, '-B', str(TOOL), str(self.rooms)],
                                capture_output=True, timeout=20, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout.decode('utf-8')
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertTrue(rows)
        self.assertTrue(any('단위' in row['question'] for row in rows))

    def test_examples_zero_hides_values(self):
        res = self.build(refs=['bookings.csv:room=rooms.csv:room_id'], examples=0)
        text = json.dumps(res, ensure_ascii=False)
        for value in ('R9', ' b2', '1.5h', '-2'):
            self.assertNotIn(value, text)

    def test_category_unit_spelling_and_single_blank_column(self):
        items = self.dir / 'shelf.csv'
        rows = ''.join(f'T{i:02d},{"ab"[i % 2]},{i + 1}kg,{"500mL" if i == 3 else "2L"}\n' for i in range(9))
        items.write_text('tool_id,kind,weight,volume\n' + rows + 'T99,a,,1L\n', encoding='utf-8')
        res = qc.build([str(items)])
        qs = {r['category']: r['question'] for r in res['rows']}
        self.assertIn('함께 두면 안 되는 조합', qs['rule_conflict'])
        self.assertIn('mL 표기는 L 단위', qs['unit'])
        self.assertIn('weight이 빈 행은', qs['missing'])
        self.assertNotIn('각각', json.dumps(res, ensure_ascii=False))

    def test_identifier_like_columns_are_not_categories(self):
        ref = self.dir / 'picks.csv'
        ref.write_text('pick_id,first,second\n' + ''.join(f'K{i},S0{i % 3},S0{(i + 1) % 3}\n' for i in range(10)),
                       encoding='utf-8')
        self.assertNotIn('rule_conflict', self.cats(qc.build([str(ref)])))

    def test_clean_file_gives_no_questions(self):
        clean = self.dir / 'clean.csv'
        clean.write_text('item_id,size\nA,3\nB,5\n', encoding='utf-8')
        self.assertEqual(qc.build([str(clean)])['count'], 0)

    def test_sparse_column_asked_as_optional(self):
        sparse = self.dir / 'sparse.csv'
        sparse.write_text('item_id,note\nA,x\nB,\nC,\nD,\n', encoding='utf-8')
        rows = qc.build([str(sparse)])['rows']
        self.assertEqual(len(rows), 1)
        self.assertIn('선택 항목', rows[0]['question'])

    def test_explicit_key_and_missing_column(self):
        res = qc.build([str(self.bookings)], keys=['bookings.csv:member'])
        self.assertNotIn('duplicate', self.cats(res))
        with self.assertRaises(InputError):
            qc.build([str(self.bookings)], keys=['bookings.csv:nope'])

    def test_input_errors_exit_2(self):
        code, out = run(str(self.dir / 'missing.csv'))
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))
        code, out = run(str(self.rooms), '--ref', 'rooms.csv:seats')
        self.assertEqual(code, 2)
        code, out = run(str(self.rooms), '--examples', '9')
        self.assertEqual(code, 2)

    def test_no_file_written(self):
        before = sorted(p.name for p in self.dir.iterdir())
        run(str(self.rooms), str(self.bookings), '--format', 'json')
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), before)


if __name__ == '__main__':
    unittest.main()
