#!/usr/bin/env python3
"""Draft candidate stakeholder questions from local CSV files (read-only).

Finds decision points that data alone cannot settle and writes them as question
ledger rows (templates/QUESTION_LEDGER.csv columns) to stdout:
  - blank cells, zero and negative numbers
  - mixed units in a numeric-looking column (for example 90분, 1.5h, 45)
  - key values that collide only after trimming spaces and upper-casing
  - repeated keys (which row is valid)
  - repeated timestamps (tie order)
  - text columns with a few repeated values (combinations that must not share a group)
  - reference values missing from another file (--ref)

The output is a draft. The participant removes questions already answered by the
task README, sets priorities and sends them. Example values are taken from the
files so questions can point at a concrete case (use --examples 0 to omit them);
output stays on stdout and is never written to a file or sent anywhere.

Usage:
  python tools/question_candidates.py data.csv [more.csv] [--key data.csv:id]
      [--ref data.csv:choice1,choice2=master.csv:id] [--examples 1] [--format csv|json]
Exit codes: 0 ok, 2 input error ({"error": ...}).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_utils import MAX_ROWS, InputError, ensure_file  # noqa: E402

LEDGER_COLUMNS = ['id', 'category', 'priority', 'context', 'question',
                  'status', 'answer', 'decision', 'test_case', 'ask_count']
NUM_UNIT = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*([^\d\s.,-][^\d\s]*)?\s*$')
TIMESTAMP = re.compile(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}')
CODE = re.compile(r'^[A-Za-z]{1,4}[-_]?\d{1,6}$')  # identifier-like values such as S01, AB-12
MAX_FILES = 10
MAX_EXAMPLES = 3


def _norm_key(v: str) -> str:
    return v.strip().upper()


def _load(path: str) -> tuple[str, list[str], list[dict[str, str]]]:
    p = ensure_file(path, '.csv')
    try:
        text = p.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError as exc:
        raise InputError(f'{p.name}: CSV must be UTF-8 text') from exc
    reader = csv.DictReader(io.StringIO(text))
    cols = reader.fieldnames or []
    if not cols:
        raise InputError(f'{p.name}: CSV header is missing')
    if len(set(cols)) != len(cols):
        raise InputError(f'{p.name}: duplicate header columns')
    rows = []
    for i, row in enumerate(reader, start=1):
        if i > MAX_ROWS:
            raise InputError(f'{p.name}: more than {MAX_ROWS} rows')
        rows.append({c: (row.get(c) or '') for c in cols})
    return p.name, cols, rows


def _ex(values: list[str], k: int) -> str:
    """Up to k distinct example values, quoted so leading/trailing spaces stay visible."""
    seen: list[str] = []
    for v in values:
        if v not in seen:
            seen.append(v)
        if len(seen) >= k:
            break
    return ', '.join(f"'{v}'" for v in seen)


def _parse_spec(spec: str, what: str) -> tuple[str, list[str]]:
    if ':' not in spec:
        raise InputError(f'{what} must look like file.csv:column')
    name, cols = spec.rsplit(':', 1)
    cols_list = [c.strip() for c in cols.split(',') if c.strip()]
    if not cols_list:
        raise InputError(f'{what} needs at least one column')
    return Path(name).name, cols_list


class Builder:
    def __init__(self, examples: int):
        self.examples = examples
        self.rows: list[dict[str, str]] = []

    def eg(self, values: list[str]) -> str:
        return f'(예: {_ex(values, self.examples)})' if self.examples and values else ''

    def add(self, category: str, priority: str, context: str, question: str) -> None:
        self.rows.append({'id': f'C{len(self.rows) + 1}', 'category': category, 'priority': priority,
                          'context': context, 'question': question, 'status': 'open', 'answer': '',
                          'decision': '', 'test_case': '', 'ask_count': '0'})


def _column_checks(b: Builder, name: str, col: str, values: list[str], sparse: list[str]) -> None:
    n = len(values)
    blanks = [i for i, v in enumerate(values) if not v.strip()]
    filled = [v for v in values if v.strip()]
    if blanks and filled and len(blanks) * 2 > n:
        sparse.append(col)
    parsed = [(v, NUM_UNIT.match(v)) for v in filled]
    if filled and all(m for _, m in parsed):
        units = Counter((m.group(2) or '').lower() for _, m in parsed)
        if len(units) > 1:
            shown = [v for v, m in parsed]
            unitless = [v for v, m in parsed if not m.group(2)]
            common = max((u for u in units if u), key=lambda u: (units[u], u))
            spelled = {}  # original spelling per lower-cased unit, first seen wins
            for _, m in parsed:
                if m.group(2):
                    spelled.setdefault(m.group(2).lower(), m.group(2))
            distinct = sorted(set(shown), key=shown.index)
            per_unit = [next(v for v in distinct if ((NUM_UNIT.match(v).group(2) or '').lower()) == u)
                        for u in units]
            eg = f'(예: {_ex(per_unit, MAX_EXAMPLES)})' if b.examples else ''
            ctx = f'{name}의 {col} 열에 단위 표기가 섞여 있습니다{eg}.'
            if unitless:
                b.add('unit', 'P0', ctx, f'{col}에서 단위 없는 숫자{b.eg(unitless)}는 {spelled[common]} 단위로 보면 되나요?')
            others = sorted(u for u in units if u and u != common)
            if others:
                b.add('unit', 'P0', ctx, f'{col}의 {spelled[others[0]]} 표기는 {spelled[common]} 단위로 환산해 같은 기준으로 비교하나요?')
        nums = [(v, float(m.group(1))) for v, m in parsed]
        zeros = [v for v, x in nums if x == 0]
        negs = [v for v, x in nums if x < 0]
        if zeros and len(zeros) < len(nums):
            b.add('boundary', 'P0', f'{name}의 {col} 값이 0인 행이 {len(zeros)}개 있습니다.',
                  f'{col} 값이 0인 행은 사용할 수 없는 대상으로 보고 제외하나요?')
        if negs:
            b.add('outlier', 'P1', f'{name}의 {col}에 음수 값이 {len(negs)}개 있습니다{b.eg(negs)}.',
                  f'음수인 {col} 값은 입력 오류로 보고 결과에서 제외하나요?')


def _blank_summary(b: Builder, name: str, cols: list[str], rows: list[dict[str, str]],
                   sparse: list[str]) -> None:
    n = len(rows)
    partly = [c for c in cols if c not in sparse
              and 0 < sum(not r[c].strip() for r in rows) < n]
    if partly:
        counts = '·'.join(str(sum(not r[c].strip() for r in rows)) for c in partly)
        if len(partly) == 1:
            b.add('missing', 'P1', f'{name}의 {partly[0]} 열에 빈 칸이 {counts}/{n}행 있습니다.',
                  f'{partly[0]}이 빈 행은 계산에서 빼고 따로 확인 목록에 두면 되나요?')
        else:
            b.add('missing', 'P1', f'{name}의 {"·".join(partly)} 열에 빈 칸이 각각 {counts}/{n}행 있습니다.',
                  '이 열들의 빈 칸은 값이 없는 것으로 보고 그 칸만 계산에서 빼면 되나요?')
    for c in sparse:
        filled = sum(bool(r[c].strip()) for r in rows)
        b.add('missing', 'P1', f'{name}의 {c} 열은 {filled}/{n}행에만 값이 있습니다.',
              f'{c} 열은 값이 있는 행에만 따로 적용되는 선택 항목인가요?')


def _category_checks(b: Builder, name: str, cols: list[str], rows: list[dict[str, str]],
                     skip: set[str]) -> None:
    """Text columns with a few repeated values often carry hidden rules (allowed mixes, order)."""
    n = len(rows)
    for c in cols:
        if c in skip or n < 8:
            continue
        vals = [r[c].strip() for r in rows if r[c].strip()]
        if len(vals) < n * 0.8 or any(NUM_UNIT.match(v) or TIMESTAMP.match(v) or CODE.match(v) for v in vals):
            continue
        kinds = sorted(set(vals), key=vals.index)
        if 2 <= len(kinds) <= 8 and len(kinds) * 2 <= len(vals):
            b.add('rule_conflict', 'P1', f'{name}의 {c} 열은 값이 {len(kinds)}종류입니다{b.eg(kinds)}.',
                  f'{c} 값끼리 같은 묶음에 함께 두면 안 되는 조합이 있나요?')


def _key_checks(b: Builder, name: str, col: str, rows: list[dict[str, str]], cols: list[str]) -> None:
    raw = [r[col] for r in rows]
    norm = [_norm_key(v) for v in raw]
    odd = [v for v, nv in zip(raw, norm) if v != nv and v.strip()]
    if odd and len(set(norm)) < len(set(raw)):
        b.add('duplicate', 'P0', f'{name}의 {col}에 공백·대소문자만 다른 값이 있습니다{b.eg(odd)}.',
              f'앞뒤 공백을 지우고 대문자로 맞춘 {col} 값이 같으면 같은 대상으로 보나요?')
    counts = Counter(v for v in norm if v)
    dups = [k for k, c in counts.items() if c > 1]
    if dups:
        ts_cols = [c for c in cols if c != col and rows and
                   sum(bool(TIMESTAMP.match(r[c].strip())) for r in rows) >= max(1, len(rows) // 2)]
        ctx = f'{name}에서 {col} 값이 같은 행이 {len(dups)}건 있습니다{b.eg(dups)}.'
        if ts_cols:
            b.add('duplicate', 'P0', ctx, f'{col} 값이 같은 행이 여러 개면 {ts_cols[0]} 값이 가장 늦은 행 하나만 유효한가요?')
        else:
            b.add('duplicate', 'P0', ctx, f'{col} 값이 같은 행이 여러 개면 파일의 마지막 행 하나만 유효한가요?')


def _timestamp_ties(b: Builder, name: str, cols: list[str], rows: list[dict[str, str]]) -> None:
    for c in cols:
        vals = [r[c].strip() for r in rows if r[c].strip()]
        if not vals or sum(bool(TIMESTAMP.match(v)) for v in vals) < max(1, len(vals) // 2):
            continue
        ties = [k for k, n in Counter(vals).items() if n > 1]
        if ties:
            b.add('tie_priority', 'P1', f'{name}의 {c} 값이 같은 행이 {len(ties)}쌍 이상 있습니다{b.eg(ties)}.',
                  f'{c} 값이 같으면 파일에 먼저 나온 행을 먼저 처리하나요?')


def build(files: list[str], keys: list[str] | None = None, refs: list[str] | None = None,
          examples: int = 1) -> dict[str, Any]:
    if not files or len(files) > MAX_FILES:
        raise InputError(f'give 1 to {MAX_FILES} CSV files')
    if not 0 <= examples <= MAX_EXAMPLES:
        raise InputError(f'--examples must be between 0 and {MAX_EXAMPLES}')
    data: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    for f in files:
        name, cols, rows = _load(f)
        if name in data:
            raise InputError(f'two files share the name {name}')
        data[name] = (cols, rows)
    b = Builder(examples)
    key_specs = [_parse_spec(k, '--key') for k in (keys or [])]
    for name, (cols, rows) in data.items():
        sparse: list[str] = []
        for col in cols:
            _column_checks(b, name, col, [r[col] for r in rows], sparse)
        _blank_summary(b, name, cols, rows, sparse)
        auto = [c for c in cols[:1] if re.search(r'(^|_)id$', c.lower())]
        chosen = [c for n, cs in key_specs if n == name for c in cs] or auto
        for col in chosen:
            if col not in cols:
                raise InputError(f'{name}: no column {col}')
            _key_checks(b, name, col, rows, cols)
        _timestamp_ties(b, name, cols, rows)
        _category_checks(b, name, cols, rows, set(chosen))
    for spec in refs or []:
        if '=' not in spec:
            raise InputError('--ref must look like src.csv:col1,col2=dst.csv:col')
        left, right = spec.split('=', 1)
        src, src_cols = _parse_spec(left, '--ref source')
        dst, dst_cols = _parse_spec(right, '--ref target')
        if src not in data or dst not in data:
            raise InputError('--ref files must also be given as inputs')
        if len(dst_cols) != 1 or dst_cols[0] not in data[dst][0]:
            raise InputError(f'{dst}: --ref target needs one existing column')
        known = {_norm_key(r[dst_cols[0]]) for r in data[dst][1]}
        missing: list[str] = []
        for c in src_cols:
            if c not in data[src][0]:
                raise InputError(f'{src}: no column {c}')
            missing += [r[c].strip() for r in data[src][1] if r[c].strip() and _norm_key(r[c]) not in known]
        if missing:
            b.add('doc_data_gap', 'P0',
                  f'{src}의 {", ".join(src_cols)}에 {dst}의 {dst_cols[0]}에 없는 값이 {len(missing)}칸 있습니다{b.eg(missing)}.',
                  f'{dst}에 없는 값을 적은 칸은 빈 칸과 같게 보나요?')
    return {'files': list(data), 'count': len(b.rows), 'rows': b.rows,
            'note': ('Draft only. Drop questions the task README already answers, adjust priorities, '
                     'then lint with question_ledger.py. Rules the data cannot show (objectives, '
                     'roles, screens, output format) still need your own questions.')}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('files', nargs='+')
    p.add_argument('--key', action='append', default=[], help='file.csv:column treated as an identifier')
    p.add_argument('--ref', action='append', default=[], help='src.csv:col1,col2=dst.csv:col reference check')
    p.add_argument('--examples', type=int, default=1, help='example values per question (0-3, default 1)')
    p.add_argument('--format', choices=('csv', 'json'), default='csv')
    a = p.parse_args(argv)
    try:
        res = build(a.files, a.key, a.ref, a.examples)
    except (InputError, OSError) as e:
        print(json.dumps({'error': str(e) if isinstance(e, InputError) else type(e).__name__},
                         ensure_ascii=False))
        return 2
    if a.format == 'json':
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=LEDGER_COLUMNS, lineterminator='\n')
        w.writeheader()
        w.writerows(res['rows'])
        sys.stdout.write(out.getvalue())
    return 0


if __name__ == '__main__':
    sys.exit(main())
