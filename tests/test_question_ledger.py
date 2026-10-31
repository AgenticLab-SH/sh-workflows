"""Offline tests for tools/question_ledger.py on synthetic ledgers."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import question_ledger as ql  # noqa: E402

HEADER = 'id,category,priority,context,question,status,answer,decision,test_case\n'


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = ql.main(argv)
    return code, buf.getvalue()


class LedgerTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def ledger(self, body, header=HEADER, name='ledger.csv'):
        p = self.dir / name
        p.write_text(header + body, encoding='utf-8')
        return str(p)

    def lint_codes(self, body, *extra):
        code, out = run(['lint', self.ledger(body), *extra])
        res = json.loads(out)
        return code, {i['id']: i['codes'] for i in res['issues']}, res


class LintTest(LedgerTestBase):
    def test_clean_row_passes(self):
        code, codes, res = self.lint_codes(
            'Q1,boundary,P0,1인 대출 한도는 5권입니다.,정확히 5번째 대출은 허용인가요?,open,,,\n')
        self.assertEqual(code, 0)
        self.assertTrue(res['passed'])
        self.assertEqual(codes, {})

    def test_compound_question_ascii_and_fullwidth(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,반납일은 포함인가요? 연체료는요?,open,,,\n'
            'Q2,c,P1,맥락,대여 수량은 1개인가요？ 2개인가요？,open,,,\n')
        self.assertIn('compound_question', codes['Q1'])
        self.assertIn('compound_question', codes['Q2'])

    def test_too_long_default_and_custom(self):
        long_q = '가' * 161 + '?'
        code, codes, _ = self.lint_codes(f'Q1,c,P1,맥락,{long_q},open,,,\n')
        self.assertEqual(code, 1)
        self.assertIn('too_long', codes['Q1'])
        _, codes, _ = self.lint_codes('Q1,c,P1,맥락,재고 0개는 품절인가요?,open,,,\n',
                                      '--max-length', '5')
        self.assertIn('too_long', codes['Q1'])

    def test_missing_context(self):
        _, codes, _ = self.lint_codes('Q1,c,P1,,재고 0개는 품절인가요?,open,,,\n')
        self.assertIn('missing_context', codes['Q1'])

    def test_open_phrases(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,빈값은 어떻게 할까요?,open,,,\n'
            'Q2,c,P1,맥락,중복은 알아서 처리하면 되나요?,open,,,\n'
            'Q3,c,P1,맥락,"도서, 잡지 등은 제외인가요?",open,,,\n')
        for qid in ('Q1', 'Q2', 'Q3'):
            self.assertIn('open_phrase', codes[qid])

    def test_deung_inside_word_is_not_open_phrase(self):
        _, codes, _ = self.lint_codes('Q1,c,P1,맥락,등록 전 문의도 등급 계산에 넣나요?,open,,,\n')
        self.assertNotIn('Q1', codes)

    def test_exact_duplicate_after_normalization(self):
        _, codes, res = self.lint_codes(
            'Q1,c,P1,맥락,반납 당일은 연체인가요?,open,,,\n'
            'Q2,c,P1,맥락,"반납  당일은, 연체인가요 ?",open,,,\n')
        self.assertIn('duplicate_question', codes['Q2'])
        self.assertEqual(res['issues'][0]['similar_to'], 'Q1')

    def test_near_duplicate(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,회의실 예약은 최대 4시간까지 가능한가요?,open,,,\n'
            'Q2,c,P1,맥락,회의실 예약은 최대 4시간까지만 가능한가요?,open,,,\n')
        self.assertIn('near_duplicate', codes['Q2'])
        self.assertNotIn('Q1', codes)

    def test_dropped_rows_skip_duplicate_check(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,반납 당일은 연체인가요?,answered,,,\n'
            'Q2,c,P1,맥락,반납 당일은 연체인가요?,dropped,,,\n')
        self.assertEqual(codes, {})

    def test_invalid_priority_and_status(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,high,맥락,재고 0개는 품절인가요?,open,,,\n'
            'Q2,c,P4,맥락,입고 당일 판매가 가능한가요?,done,,,\n')
        self.assertIn('invalid_priority', codes['Q1'])
        self.assertIn('invalid_priority', codes['Q2'])
        self.assertIn('invalid_status', codes['Q2'])

    def test_duplicate_and_missing_id(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,재고 0개는 품절인가요?,open,,,\n'
            'Q1,c,P1,맥락,입고 당일 판매가 가능한가요?,open,,,\n'
            ',c,P1,맥락,반품 재고는 판매 가능 수량에 넣나요?,open,,,\n')
        self.assertIn('duplicate_id', codes['Q1'])
        self.assertIn('missing_id', codes['row3'])

    def test_output_has_only_ids_and_codes(self):
        _, _, res = self.lint_codes('Q1,c,P1,,비밀답변 포함 질문은 어떻게 할까요?,open,SECRET_ANSWER,,\n')
        text = json.dumps(res, ensure_ascii=False)
        self.assertNotIn('SECRET_ANSWER', text)
        self.assertNotIn('비밀답변', text)

    def test_english_open_phrases_use_word_boundaries(self):
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,맥락,Should fetch run before the sketch export?,open,,,\n'
            'Q2,c,P1,맥락,"Include books, magazines, etc. in the count?",open,,,\n'
            'Q3,c,P1,맥락,Round the fee AS NEEDED for the receipt?,open,,,\n')
        self.assertNotIn('Q1', codes)
        self.assertIn('open_phrase', codes['Q2'])
        self.assertIn('open_phrase', codes['Q3'])

    def test_short_questions_compare_with_context(self):
        # Same short re-ask wording but different facts in context: not duplicates.
        _, codes, _ = self.lint_codes(
            'Q1,c,P1,반납 예정일이 휴관일이면 다음 개관일로 미루는 안입니다.,이 안으로 진행해도 되나요?,open,,,\n'
            'Q2,c,P1,분실 신고된 책은 대출 가능 목록에서 빼는 안입니다.,이 안으로 진행해도 되나요?,open,,,\n')
        self.assertEqual(codes, {})
        _, codes, res = self.lint_codes(
            'Q1,c,P1,분실 신고된 책은 대출 가능 목록에서 빼는 안입니다.,이 안으로 진행해도 되나요?,open,,,\n'
            'Q2,c,P1,분실 신고된 책은 대출 가능 목록에서 빼는 안입니다.,이 안으로 진행해도 될까요?,open,,,\n')
        self.assertIn('near_duplicate', codes['Q2'])
        self.assertEqual(res['issues'][0]['similar_to'], 'Q1')

    def test_long_questions_ignore_context_for_duplicates(self):
        q = '회의실 예약 마감 당일 23시 59분에 들어온 예약은 마감 전 예약으로 보나요?'
        self.assertGreaterEqual(len(q), ql.SHORT_QUESTION)
        _, codes, _ = self.lint_codes(f'Q1,c,P1,맥락 하나,{q},open,,,\nQ2,c,P1,전혀 다른 맥락,{q},open,,,\n')
        self.assertIn('duplicate_question', codes['Q2'])

    def test_ask_count_optional_retry_limit_and_invalid(self):
        header = HEADER.strip() + ',ask_count\n'
        _, codes, _ = self.lint_codes('Q1,c,P1,맥락,재고 0개는 품절인가요?,open,,,\n')
        self.assertEqual(codes, {})  # ledger without ask_count still passes
        p = self.ledger('Q1,c,P1,맥락,재고 0개는 품절인가요?,unclear,,,,3\n'
                        'Q2,c,P1,맥락,입고 당일 판매가 가능한가요?,answered,,,,3\n'
                        'Q3,c,P1,맥락,반품 재고는 판매 가능 수량에 넣나요?,sent,,,,2\n'
                        'Q4,c,P1,맥락,할인 상품도 재고 합계에 넣나요?,open,,,,-1\n'
                        'Q5,c,P1,맥락,묶음 상품은 낱개 수량으로 세나요?,open,,,,\n', header=header)
        code, out = run(['lint', p])
        codes = {i['id']: i['codes'] for i in json.loads(out)['issues']}
        self.assertEqual(code, 1)
        self.assertEqual(codes, {'Q1': ['retry_limit'], 'Q4': ['invalid_ask_count']})
        _, out = run(['summary', p])
        self.assertEqual(json.loads(out)['retry_limit'], ['Q1'])

    def test_retry_limit_only_for_partial_and_unclear(self):
        header = HEADER.strip() + ',ask_count\n'
        p = self.ledger('Q1,c,P1,맥락,재고 0개는 품절인가요?,sent,,,,3\n'
                        'Q2,c,P1,맥락,입고 당일 판매가 가능한가요?,open,,,,3\n'
                        'Q3,c,P1,맥락,반품 재고는 판매 가능 수량에 넣나요?,unclear,,,,3\n'
                        'Q4,c,P1,맥락,묶음 상품은 낱개 수량으로 세나요?,partial,,,,4\n', header=header)
        code, out = run(['lint', p])
        codes = {i['id']: i['codes'] for i in json.loads(out)['issues']}
        self.assertEqual(code, 1)
        self.assertEqual(codes, {'Q3': ['retry_limit'], 'Q4': ['retry_limit']})
        _, out = run(['summary', p])
        self.assertEqual(json.loads(out)['retry_limit'], ['Q3', 'Q4'])
        _, out = run(['next', p])
        res = json.loads(out)
        self.assertEqual([m['id'] for m in res['messages']], ['Q2'])
        self.assertEqual(res['retry_limit'], ['Q3', 'Q4'])
        # A third send still waiting for an answer passes lint on its own.
        code, out = run(['lint', self.ledger('Q1,c,P1,맥락,재고 0개는 품절인가요?,sent,,,,3\n',
                                             header=header)])
        self.assertEqual(code, 0, out)

    def test_lint_2000_rows_is_fast(self):
        body = ''.join(f'Q{i},c,P1,맥락 {i},도서 {i}번의 {i % 7}차 연장 기한은 {i * 3}일인가요?,open,,,\n'
                       for i in range(2000))
        start = time.perf_counter()
        code, out = run(['lint', self.ledger(body)])
        self.assertLess(time.perf_counter() - start, 10)
        res = json.loads(out)
        self.assertEqual(res['rows'], 2000)
        self.assertIn('near-duplicate check skipped above 500 rows per category', res['note'])
        self.assertIn(code, (0, 1))

    def test_pair_budget_bounds_four_categories_of_500(self):
        cats = 'abcd'
        body = ''.join(f'Q{i},{cats[i % 4]},P1,맥락 {i},도서 {i}번의 {i % 7}차 연장 기한은 {i * 3}일인가요?,open,,,\n'
                       for i in range(2000))
        start = time.perf_counter()
        code, out = run(['lint', self.ledger(body)])
        self.assertLess(time.perf_counter() - start, 10)
        res = json.loads(out)
        self.assertIn(f'{ql.NEAR_DUP_MAX_PAIRS} comparison pairs in total', res['note'])
        self.assertIn(code, (0, 1))

    def test_near_duplicate_only_within_category(self):
        _, codes, res = self.lint_codes(
            'Q1,a,P1,맥락,회의실 예약은 최대 4시간까지 가능한가요?,open,,,\n'
            'Q2,b,P1,맥락,회의실 예약은 최대 4시간까지만 가능한가요?,open,,,\n')
        self.assertEqual(codes, {})
        self.assertNotIn('skipped', res['note'])

    def test_large_category_keeps_exact_duplicate_check(self):
        body = ''.join(f'Q{i},c,P1,맥락,도서 {i}번의 연장 기한은 {i * 3}일인가요?,open,,,\n'
                       for i in range(501))
        body += 'Q9999,c,P1,맥락,도서 7번의 연장 기한은 21일인가요?,open,,,\n'
        _, codes, res = self.lint_codes(body)
        self.assertIn('duplicate_question', codes['Q9999'])
        self.assertNotIn('near_duplicate', sum(codes.values(), []))
        self.assertIn('near-duplicate check skipped', res['note'])

    def test_help_states_length_policy(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            ql.main(['lint', '--help'])
        text = ' '.join(buf.getvalue().split())
        self.assertIn('hard upper limit', text)
        self.assertIn('about 120 characters', text)


class NextTest(LedgerTestBase):
    BODY = ('A,c,P2,맥락A,질문A?,open,,,\n'
            'B,c,P0,맥락B,질문B?,answered,,,\n'
            'C,c,P1,맥락C,질문C?,unclear,,,\n'
            'D,c,P0,맥락D,질문D?,open,,,\n'
            'E,c,P0,맥락E,질문E?,sent,,,\n'
            'F,c,P0,맥락F,질문F?,unclear,,,\n'
            'G,c,P3,맥락G,질문G?,open,,,\n'
            'H,c,P1,맥락H,질문H?,partial,,,\n')

    def test_order_and_status_filter(self):
        code, out = run(['next', self.ledger(self.BODY), '--limit', '10'])
        self.assertEqual(code, 0)
        res = json.loads(out)
        self.assertEqual([m['id'] for m in res['messages']], ['D', 'F', 'C', 'H', 'A', 'G'])
        self.assertEqual([m['no'] for m in res['messages']], [1, 2, 3, 4, 5, 6])
        self.assertEqual(res['messages'][0]['message'], '맥락D 질문D?')
        self.assertFalse(res['messages'][0]['needs_rewrite'])

    def test_partial_and_unclear_need_rewrite(self):
        _, out = run(['next', self.ledger(self.BODY), '--limit', '10'])
        msgs = {m['id']: m for m in json.loads(out)['messages']}
        for qid in ('F', 'C', 'H'):
            self.assertTrue(msgs[qid]['needs_rewrite'], qid)
            self.assertIsNone(msgs[qid]['message'], qid)
            self.assertEqual(msgs[qid]['rewrite_hint'], '쪼개기/선택지/샘플 행')
        self.assertEqual(msgs['H']['reference_original'], '맥락H 질문H?')

    def test_limit(self):
        _, out = run(['next', self.ledger(self.BODY), '--limit', '2'])
        res = json.loads(out)
        self.assertEqual(res['count'], 2)
        self.assertEqual(res['pending_total'], 6)
        self.assertEqual([m['id'] for m in res['messages']], ['D', 'F'])

    def test_text_format(self):
        _, out = run(['next', self.ledger(self.BODY), '--limit', '4', '--format', 'text'])
        self.assertIn('[1] D · P0\n', out)
        self.assertIn('[2] F · P0 재질문 [다시 쓰기 필요: 쪼개기/선택지/샘플 행]', out)
        self.assertIn('[4] H · P1 보완 질문 [다시 쓰기 필요: 쪼개기/선택지/샘플 행]', out)
        self.assertIn('(참고 원문, 그대로 보내지 않음) 맥락H 질문H?', out)
        self.assertNotIn('\n질문H?', out)  # never printed as a bare copy line
        self.assertLess(out.index('맥락D'), out.index('질문D?'))
        self.assertIn('전송 단위 시험', out.splitlines()[0])

    def test_retry_limit_rows_leave_next(self):
        body = ('A,c,P0,맥락A,질문A?,unclear,,,,3\n'
                'B,c,P0,맥락B,질문B?,unclear,,,,2\n')
        header = HEADER.strip() + ',ask_count\n'
        _, out = run(['next', self.ledger(body, header=header)])
        res = json.loads(out)
        self.assertEqual([m['id'] for m in res['messages']], ['B'])
        self.assertEqual(res['messages'][0]['ask_count'], 2)
        self.assertEqual(res['retry_limit'], ['A'])
        _, out = run(['next', self.ledger(body, header=header), '--format', 'text'])
        self.assertIn('재질문 한도 도달(assumed로 기록하고 진행): A', out)

    def test_rewritten_row_set_to_open_is_copy_ready(self):
        header = HEADER.strip() + ',ask_count\n'
        body = 'A,c,P0,휴관일 반납은 다음 개관일로 미루는 안입니다.,이 안으로 진행해도 되나요?,open,,,,2\n'
        _, out = run(['next', self.ledger(body, header=header)])
        res = json.loads(out)
        m = res['messages'][0]
        self.assertEqual((m['id'], m['ask_count'], m['needs_rewrite']), ('A', 2, False))
        self.assertEqual(m['message'], '휴관일 반납은 다음 개관일로 미루는 안입니다. 이 안으로 진행해도 되나요?')
        self.assertEqual(res['retry_limit'], [])
        self.assertIn('keep ask_count', res['note'])
        _, out = run(['next', self.ledger(body, header=header), '--format', 'text'])
        self.assertIn('\n이 안으로 진행해도 되나요?', out)
        self.assertNotIn('참고 원문', out)

    def test_text_format_states_rewrite_rule(self):
        _, out = run(['next', self.ledger(self.BODY), '--format', 'text'])
        self.assertIn('status를 open으로 바꾸고 ask_count는 그대로', out)

    def test_invalid_limit_is_error(self):
        code, out = run(['next', self.ledger(self.BODY), '--limit', '0'])
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))


class SummaryTest(LedgerTestBase):
    def test_counts_and_ids_without_answers(self):
        body = ('Q1,boundary,P0,맥락,질문1?,answered,ANSWER_ONE,,\n'
                'Q2,boundary,P0,맥락,질문2?,partial,ANSWER_TWO,,\n'
                'Q3,data_field,P1,맥락,질문3?,assumed,,가정함,\n'
                'Q4,data_field,P1,맥락,질문4?,sent,,,\n'
                'Q5,output_format,P2,맥락,질문5?,open,,,\n'
                'Q6,output_format,P1,맥락,질문6?,dropped,,,\n')
        code, out = run(['summary', self.ledger(body)])
        self.assertEqual(code, 0)
        res = json.loads(out)
        self.assertEqual(res['rows'], 6)
        self.assertEqual(res['by_status'], {'answered': 1, 'partial': 1, 'assumed': 1,
                                            'sent': 1, 'open': 1, 'dropped': 1})
        self.assertEqual(res['by_category'], {'boundary': 2, 'data_field': 2, 'output_format': 2})
        self.assertEqual(res['by_priority'], {'P0': 2, 'P1': 3, 'P2': 1})
        self.assertEqual(res['unresolved_p0_p1'], ['Q2', 'Q4'])
        self.assertEqual(res['needs_rewrite'], ['Q2'])
        self.assertEqual(res['retry_limit'], [])
        self.assertEqual(res['assumed'], ['Q3'])
        self.assertFalse(res['stop_condition_met'])
        self.assertNotIn('ANSWER_ONE', out)
        self.assertNotIn('ANSWER_TWO', out)


class TemplateAndErrorTest(LedgerTestBase):
    def test_template_ledger_passes_lint(self):
        code, out = run(['lint', str(ROOT / 'templates' / 'QUESTION_LEDGER.csv')])
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)['rows'], 5)

    def test_template_header_and_statuses(self):
        path = ROOT / 'templates' / 'QUESTION_LEDGER.csv'
        first = path.read_text(encoding='utf-8').splitlines()[0]
        self.assertEqual(first, ','.join(ql.COLUMNS + ql.OPTIONAL_COLUMNS))
        rows = ql.load_ledger(path)
        self.assertTrue(all(r['status'] in ql.STATUSES for r in rows))
        self.assertTrue(all(not r['_ask_count_invalid'] for r in rows))

    def test_template_next_marks_partial_and_unclear(self):
        _, out = run(['next', str(ROOT / 'templates' / 'QUESTION_LEDGER.csv')])
        msgs = {m['id']: m for m in json.loads(out)['messages']}
        self.assertTrue(msgs['Q2']['needs_rewrite'])
        self.assertTrue(msgs['Q3']['needs_rewrite'])
        self.assertFalse(msgs['Q4']['needs_rewrite'])
        self.assertNotIn('Q1', msgs)

    def test_doc_example_questions_pass_lint(self):
        """Concrete example questions in the Skill and docs follow the kit's own message rules."""
        sources = {
            '.agents/skills/stakeholder-agent-questioning/SKILL.md': 'table',
            'docs/STAKEHOLDER_QUESTIONS.md': 'table',
            'templates/QUESTION_MESSAGES.md': 'bullet',
        }
        for rel, kind in sources.items():
            lines = (ROOT / rel).read_text(encoding='utf-8').splitlines()
            examples = []
            for no, line in enumerate(lines, start=1):
                if kind == 'bullet' and line.startswith('- 예: '):
                    examples.append((no, line[len('- 예: '):]))
                elif kind == 'table' and line.startswith('| ') and line.count('|') == 3:
                    cell = line.split('|')[2].strip()
                    if cell.endswith('?') and not cell.startswith('구체 질문'):
                        examples.append((no, cell))
            self.assertGreaterEqual(len(examples), 5, rel)
            body = ''.join(f'E{no},example,P1,{rel}:{no},"{q}",open,,,\n' for no, q in examples)
            code, out = run(['lint', self.ledger(body, name='examples.csv')])
            self.assertEqual(code, 0, f'{rel}: {out}')

    def test_wrong_header_exit_2(self):
        p = self.ledger('Q1,c,P0,맥락,질문?\n', header='id,category,priority,context,question\n')
        code, out = run(['lint', p])
        self.assertEqual(code, 2)
        self.assertIn('missing required columns', json.loads(out)['error'])

    def test_duplicate_header_exit_2(self):
        p = self.ledger('', header=HEADER.strip() + ',id\n')
        code, out = run(['summary', p])
        self.assertEqual(code, 2)

    def test_missing_file_and_wrong_suffix_exit_2(self):
        code, _ = run(['summary', str(self.dir / 'none.csv')])
        self.assertEqual(code, 2)
        txt = self.dir / 'ledger.txt'
        txt.write_text(HEADER, encoding='utf-8')
        code, out = run(['summary', str(txt)])
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))

    def test_cli_subprocess_exit_codes(self):
        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        bad = self.ledger('Q1,c,P9,,빈값은 어떻게 할까요? 중복은요?,open,,,\n')
        script = str(ROOT / 'tools' / 'question_ledger.py')
        p = subprocess.run([sys.executable, script, 'lint', bad], capture_output=True,
                           timeout=20, env=env)
        self.assertEqual(p.returncode, 1, p.stderr)
        codes = json.loads(p.stdout.decode('utf-8'))['issues'][0]['codes']
        for c in ('compound_question', 'missing_context', 'open_phrase', 'invalid_priority'):
            self.assertIn(c, codes)
        p = subprocess.run([sys.executable, script, 'next', str(self.dir / 'none.csv')],
                           capture_output=True, timeout=20, env=env)
        self.assertEqual(p.returncode, 2)
        self.assertIn('error', json.loads(p.stdout.decode('utf-8')))


if __name__ == '__main__':
    unittest.main()
