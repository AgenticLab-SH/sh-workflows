#!/usr/bin/env python3
"""Read-only question ledger CLI: lint questions, print next messages, summarize status.

A question asks one fact with one question mark. A message is one send to the
stakeholder chat; it may carry one question or a numbered batch, depending on
the send-unit trial. No network calls and no file writes. Output goes to stdout.
Errors print JSON {"error": ...} and exit 2. `lint` exits 1 when issues exist.

Re-ask rule: after rewriting a partial/unclear row, set status back to open and keep
ask_count; when sending, set status to sent and add 1. If the row was split into new
rows, close the original row as answered (answered part in decision) or dropped.
The retry limit applies only to partial/unclear rows with ask_count >= 3.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_utils import InputError, ensure_file  # noqa: E402

COLUMNS = ['id', 'category', 'priority', 'context', 'question',
           'status', 'answer', 'decision', 'test_case']
OPTIONAL_COLUMNS = ['ask_count']  # times sent, first ask included; blank or absent = 0
STATUSES = ('open', 'sent', 'answered', 'partial', 'unclear', 'assumed', 'dropped')
PENDING = ('open', 'partial', 'unclear')
NEEDS_REWRITE = ('partial', 'unclear')
RESOLVED = ('answered', 'assumed', 'dropped')
PRIORITY_RE = re.compile(r'^P[0-3]$')
MAX_LEDGER_ROWS = 2000
DEFAULT_MAX_LENGTH = 160  # hard upper limit; docs recommend about 120 characters
DEFAULT_SIMILARITY = 0.9
SHORT_QUESTION = 25  # shorter questions are compared together with their context
NEAR_DUP_MAX_ROWS = 500  # per category; above this only exact duplicates are checked
NEAR_DUP_MAX_PAIRS = 200_000  # whole ledger; largest categories are skipped first beyond this
NEAR_DUP_SKIP_NOTE = (f'near-duplicate check skipped above {NEAR_DUP_MAX_ROWS} rows per category '
                      f'or {NEAR_DUP_MAX_PAIRS} comparison pairs in total')
RETRY_LIMIT = 3  # first ask + two re-asks (a choice-type re-ask also counts)
REWRITE_HINT = '쪼개기/선택지/샘플 행'
REWRITE_RULE = ('다시 쓴 행은 status를 open으로 바꾸고 ask_count는 그대로 둡니다'
                '(보낼 때 sent로 바꾸고 1 올림). 새 행으로 쪼갰다면 원래 행은 '
                'answered(답한 부분만 decision에) 또는 dropped로 닫습니다.')
STATUS_TAG = {'unclear': '재질문', 'partial': '보완 질문'}

# Korean open-ended phrases, matched as substrings.
OPEN_PHRASES = ['어떻게 할까요', '어떻게 하면 될까요', '어떻게 처리', '적절히', '적당히',
                '알아서', '대충', '가능하면', '필요하면', '기타 등등', '등등']
# English open-ended phrases, matched on ASCII-letter word boundaries (no 'fetch' hit for 'etc').
OPEN_PHRASES_EN = ['etc', 'as appropriate', 'as needed', 'whatever']
OPEN_EN_RE = re.compile(r'(?<![A-Za-z])(' + '|'.join(re.escape(p) for p in OPEN_PHRASES_EN)
                        + r')(?![A-Za-z])', re.IGNORECASE)
# Standalone '등' (not part of 등록·등급 etc.), optionally followed by a particle.
STANDALONE_DEUNG = re.compile(r'(?:^|[\s,])등(?:$|[\s,.?？!]|[은는을이의도과와]|으로)')


def _norm(text: str) -> str:
    return re.sub(r'[\W_]+', '', text.lower())


def _parse_ask_count(raw: str) -> int | None:
    """Return the count, 0 for blank, or None when the value is not a non-negative integer."""
    if not raw:
        return 0
    return int(raw) if re.fullmatch(r'\d{1,6}', raw) else None


def load_ledger(path: str | Path) -> list[dict[str, Any]]:
    p = ensure_file(path, '.csv')
    rows: list[dict[str, Any]] = []
    try:
        with p.open('r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            if not cols:
                raise InputError('CSV header is missing')
            dup_cols = sorted(c for c, n in Counter(cols).items() if n > 1)
            if dup_cols:
                raise InputError('duplicate header columns: ' + ','.join(dup_cols))
            missing = [c for c in COLUMNS if c not in cols]
            if missing:
                raise InputError('missing required columns: ' + ','.join(missing))
            for line_no, row in enumerate(reader, start=1):
                if line_no > MAX_LEDGER_ROWS:
                    raise InputError(f'ledger exceeds {MAX_LEDGER_ROWS} rows')
                malformed = None in row or any(v is None for v in row.values())
                clean = {c: (row.get(c) or '').strip() for c in COLUMNS + OPTIONAL_COLUMNS}
                parsed = _parse_ask_count(clean['ask_count'])
                clean['_ask_count'] = parsed if parsed is not None else 0
                clean['_ask_count_invalid'] = parsed is None
                clean['_order'] = line_no
                clean['_malformed'] = malformed
                rows.append(clean)
    except UnicodeDecodeError as exc:
        raise InputError('ledger must be UTF-8 text') from exc
    except csv.Error as exc:
        raise InputError('malformed CSV structure') from exc
    return rows


def _row_id(row: dict[str, Any]) -> str:
    return row['id'] or f"row{row['_order']}"


def _at_retry_limit(row: dict[str, Any]) -> bool:
    """Third answer was still partial/unclear. sent/open rows are waiting or ready to send."""
    return row['status'] in NEEDS_REWRITE and row['_ask_count'] >= RETRY_LIMIT


def open_phrase_hits(text: str) -> list[str]:
    low = text.lower()
    hits = [ph for ph in OPEN_PHRASES if ph in low]
    hits += [m.group(1).lower() for m in OPEN_EN_RE.finditer(text)]
    if STANDALONE_DEUNG.search(text):
        hits.append('등')
    return hits


def _dup_key(row: dict[str, Any]) -> str:
    q = row['question']
    return _norm(q if len(q) >= SHORT_QUESTION else row['context'] + ' ' + q)


def _similar(a: str, b: str, threshold: float) -> bool:
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return (sm.real_quick_ratio() >= threshold and sm.quick_ratio() >= threshold
            and sm.ratio() >= threshold)


def lint(rows: list[dict[str, Any]], max_length: int = DEFAULT_MAX_LENGTH,
         similarity: float = DEFAULT_SIMILARITY) -> dict[str, Any]:
    issues: dict[str, list[str]] = {}
    refs: dict[str, str] = {}
    seen_ids: Counter[str] = Counter(r['id'] for r in rows if r['id'])
    # Near-duplicate comparison runs only inside one category, and only when that
    # category has at most NEAR_DUP_MAX_ROWS comparable rows (keeps lint fast).
    per_category: Counter[str] = Counter(r['category'] for r in rows
                                         if r['question'] and r['status'] != 'dropped')
    skipped = {c for c, n in per_category.items() if n > NEAR_DUP_MAX_ROWS}
    # Keep total pairwise work bounded: skip the largest remaining categories first.
    pairs = sum(n * (n - 1) // 2 for c, n in per_category.items() if c not in skipped)
    for c, n in sorted(per_category.items(), key=lambda kv: (-kv[1], kv[0])):
        if pairs <= NEAR_DUP_MAX_PAIRS:
            break
        if c not in skipped:
            skipped.add(c)
            pairs -= n * (n - 1) // 2
    compared: dict[str, list[tuple[str, str]]] = {}  # category -> [(row id, key)]
    exact: dict[str, str] = {}

    for row in rows:
        rid = _row_id(row)
        codes: list[str] = []
        q = row['question']
        if row['_malformed']:
            codes.append('malformed_row')
        if not row['id']:
            codes.append('missing_id')
        elif seen_ids[row['id']] > 1:
            codes.append('duplicate_id')
        if not q:
            codes.append('missing_question')
        if q.count('?') + q.count('？') >= 2:
            codes.append('compound_question')
        if len(q) > max_length:
            codes.append('too_long')
        if not row['context']:
            codes.append('missing_context')
        if open_phrase_hits(q):
            codes.append('open_phrase')
        if not PRIORITY_RE.match(row['priority']):
            codes.append('invalid_priority')
        if row['status'] not in STATUSES:
            codes.append('invalid_status')
        if row['_ask_count_invalid']:
            codes.append('invalid_ask_count')
        elif _at_retry_limit(row):
            codes.append('retry_limit')
        key = _dup_key(row) if q else ''
        if key and row['status'] != 'dropped':
            cat = row['category']
            if key in exact:
                codes.append('duplicate_question')
                refs[rid] = exact[key]
            else:
                if cat not in skipped:
                    for other_id, other in compared.get(cat, []):
                        if _similar(key, other, similarity):
                            codes.append('near_duplicate')
                            refs[rid] = other_id
                            break
                exact[key] = rid
            if cat not in skipped:
                compared.setdefault(cat, []).append((rid, key))
        if codes:
            issues[rid] = issues.get(rid, []) + codes

    out = []
    for rid, codes in issues.items():
        item: dict[str, Any] = {'id': rid, 'codes': codes}
        if rid in refs:
            item['similar_to'] = refs[rid]
        out.append(item)
    note = 'Only row ids and problem codes are shown.'
    if skipped:
        note += ' ' + NEAR_DUP_SKIP_NOTE + '; exact duplicates are still checked.'
    return {'rows': len(rows), 'issue_count': len(out), 'passed': not out, 'issues': out,
            'note': note}


def _priority_rank(p: str) -> int:
    return int(p[1]) if PRIORITY_RE.match(p) else 9


def next_questions(rows: list[dict[str, Any]], limit: int = 5) -> dict[str, Any]:
    pending = [r for r in rows if r['status'] in PENDING and not _at_retry_limit(r)]
    pending.sort(key=lambda r: (_priority_rank(r['priority']), r['_order']))
    picked = pending[:max(limit, 0)]
    messages = []
    for no, r in enumerate(picked, start=1):
        original = (r['context'] + ' ' + r['question']).strip()
        rewrite = r['status'] in NEEDS_REWRITE
        item: dict[str, Any] = {'no': no, 'id': _row_id(r), 'priority': r['priority'],
                                'status': r['status'], 'ask_count': r['_ask_count'],
                                'needs_rewrite': rewrite, 'context': r['context'],
                                'question': r['question']}
        if rewrite:
            item['message'] = None  # do not resend the same wording
            item['rewrite_hint'] = REWRITE_HINT
            item['reference_original'] = original
        else:
            item['message'] = original
        messages.append(item)
    return {'pending_total': len(pending), 'count': len(messages), 'messages': messages,
            'retry_limit': [_row_id(r) for r in rows if _at_retry_limit(r)],
            'note': ('One question = one fact. Send as one message per question or as a '
                     'numbered batch, following the send-unit trial. Rewrite rows marked '
                     'needs_rewrite, then set status to open and keep ask_count (on send: '
                     'sent, ask_count + 1); close a split original row as answered or '
                     'dropped. Record retry_limit rows (partial/unclear with ask_count >= 3) '
                     'as assumed.')}


def format_next_text(result: dict[str, Any]) -> str:
    lines = [f"보낼 질문 {result['count']}개 / 대기 {result['pending_total']}개 "
             "(질문 하나에 사실 하나. 전송 단위 시험 결과에 따라 메시지당 1개 또는 "
             "번호 붙인 3~5개로 묶어 검토 후 복사)"]
    if any(m['needs_rewrite'] for m in result['messages']):
        lines.append(REWRITE_RULE)
    for m in result['messages']:
        tag = STATUS_TAG.get(m['status'], '')
        head = f"[{m['no']}] {m['id']} · {m['priority']}" + (f' {tag}' if tag else '')
        lines.append('')
        if m['needs_rewrite']:
            lines.append(f"{head} [다시 쓰기 필요: {REWRITE_HINT}]")
            lines.append(f"(참고 원문, 그대로 보내지 않음) {m['reference_original']}")
        else:
            lines.append(head)
            if m['context']:
                lines.append(m['context'])
            lines.append(m['question'])
    if result['retry_limit']:
        lines.append('')
        lines.append('재질문 한도 도달(assumed로 기록하고 진행): ' + ', '.join(result['retry_limit']))
    return '\n'.join(lines)


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unresolved = [_row_id(r) for r in rows
                  if r['priority'] in ('P0', 'P1') and r['status'] not in RESOLVED]
    return {'rows': len(rows),
            'by_status': dict(Counter(r['status'] or '(blank)' for r in rows)),
            'by_category': dict(Counter(r['category'] or '(blank)' for r in rows)),
            'by_priority': dict(Counter(r['priority'] or '(blank)' for r in rows)),
            'unresolved_p0_p1': unresolved,
            'needs_rewrite': [_row_id(r) for r in rows
                              if r['status'] in NEEDS_REWRITE and not _at_retry_limit(r)],
            'retry_limit': [_row_id(r) for r in rows if _at_retry_limit(r)],
            'assumed': [_row_id(r) for r in rows if r['status'] == 'assumed'],
            'stop_condition_met': not unresolved,
            'note': 'Answer text is not printed. Assumed items still need disclosure.'}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    lp = sub.add_parser('lint', help='check question quality; exit 1 on issues')
    lp.add_argument('file')
    lp.add_argument('--max-length', type=int, default=DEFAULT_MAX_LENGTH,
                    help=f'hard upper limit for the question column (default {DEFAULT_MAX_LENGTH}); '
                         'the docs recommend about 120 characters')
    lp.add_argument('--similarity', type=float, default=DEFAULT_SIMILARITY,
                    help=f'near-duplicate ratio threshold (default {DEFAULT_SIMILARITY}); '
                         f'questions under {SHORT_QUESTION} characters are compared with their context')
    np_ = sub.add_parser('next', help='print open/partial/unclear questions; partial and unclear '
                                      'rows are marked for rewrite instead of copy. After '
                                      'rewriting, set status to open and keep ask_count')
    np_.add_argument('file')
    np_.add_argument('--limit', type=int, default=5)
    np_.add_argument('--format', choices=('json', 'text'), default='json')
    sp = sub.add_parser('summary', help='counts by status/category/priority, retry limit ids')
    sp.add_argument('file')
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows = load_ledger(args.file)
        if args.command == 'lint':
            if args.max_length < 1 or not 0 < args.similarity <= 1:
                raise InputError('invalid --max-length or --similarity')
            res = lint(rows, args.max_length, args.similarity)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0 if res['passed'] else 1
        if args.command == 'next':
            if args.limit < 1:
                raise InputError('--limit must be at least 1')
            res = next_questions(rows, args.limit)
            if args.format == 'text':
                print(format_next_text(res))
            else:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0
        print(json.dumps(summary(rows), indent=2, ensure_ascii=False))
        return 0
    except (InputError, OSError) as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
