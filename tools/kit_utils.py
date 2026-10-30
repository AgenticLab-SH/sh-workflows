"""Read-only, bounded local data checks. No remote calls or row-level output."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import Counter
from typing import Any

MAX_FILE_BYTES = 5_000_000
MAX_ROWS = 100_000
MAX_DEPTH = 20
MAX_DIFF_PATHS = 40


class InputError(ValueError):
    """Invalid user input or unsupported local file."""


def ensure_file(path: str | Path, suffix: str | None = None, max_bytes: int = MAX_FILE_BYTES) -> Path:
    p = Path(path).resolve(strict=True)
    if not p.is_file():
        raise InputError("expected a regular file")
    if suffix and p.suffix.lower() != suffix:
        raise InputError(f"expected a {suffix} file")
    if p.stat().st_size > max_bytes:
        raise InputError(f"file exceeds {max_bytes} byte limit")
    return p


def restricted_path(path: str | Path, allowed_root: str | Path, suffix: str) -> Path:
    root = Path(allowed_root).resolve(strict=True)
    p = ensure_file(path, suffix=suffix)
    if not p.is_relative_to(root):
        raise InputError("file is outside configured allowed root")
    return p


def read_json(path: str | Path) -> Any:
    p = ensure_file(path, '.json')
    try:
        with p.open('r', encoding='utf-8-sig') as file:
            return json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InputError(f"invalid JSON: {type(exc).__name__}") from exc


def validate_json(path: str | Path, required_keys: list[str] | None = None) -> dict[str, Any]:
    obj = read_json(path)
    if not isinstance(obj, dict):
        return {"valid": False, "type": type(obj).__name__, "reason": "top-level object required"}
    keys = set(obj.keys())
    missing = sorted(set(required_keys or []) - keys)
    return {"valid": not missing, "type": "object", "keys": sorted(keys)[:100],
            "key_count": len(keys), "missing_required_keys": missing}


def csv_audit(path: str | Path, required_columns: list[str] | None = None,
              unique_columns: list[str] | None = None) -> dict[str, Any]:
    p = ensure_file(path, '.csv')
    required = list(dict.fromkeys(required_columns or []))
    unique = list(dict.fromkeys(unique_columns or []))
    with p.open('r', encoding='utf-8-sig', newline='') as f:
        try:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            if not cols:
                raise InputError('CSV header is missing')
            if any(c is None or not c.strip() for c in cols):
                raise InputError('CSV contains an empty column name')
            missing = sorted(set(required) - set(cols))
            missing_unique = sorted(set(unique) - set(cols))
            duplicate_header_columns = sorted(col for col, n in Counter(cols).items() if n > 1)
            empty = Counter({col: 0 for col in cols})
            seen = set()
            dup = 0
            malformed = 0
            count = 0
            invalid_unique_rows = 0
            for row in reader:
                count += 1
                if count > MAX_ROWS:
                    raise InputError('CSV row limit exceeded')
                if None in row or any(v is None for v in row.values()):
                    malformed += 1
                for col in cols:
                    val = row.get(col)
                    if val is None or not str(val).strip():
                        empty[col] += 1
                if unique and not missing_unique:
                    key = tuple(row.get(c) for c in unique)
                    if any(v is None or not str(v).strip() for v in key):
                        invalid_unique_rows += 1
                    elif key in seen:
                        dup += 1
                    else:
                        seen.add(key)
        except csv.Error as exc:
            raise InputError('malformed CSV structure') from exc
    return {"row_count": count, "column_count": len(cols), "columns": cols,
            "required_columns_missing": missing, "duplicate_header_columns": duplicate_header_columns,
            "missing_values_by_column": dict(empty), "malformed_row_count": malformed,
            "unique_columns_missing": missing_unique, "duplicate_key_rows": dup,
            "empty_key_rows": invalid_unique_rows,
            "required_value_missing_count": sum(empty[k] for k in required if k in empty),
            "passed_requested_checks": not (missing or missing_unique or duplicate_header_columns or malformed or dup or invalid_unique_rows or any(empty[k] for k in required if k in empty)),
            "note": "No row-level values are included in the output. Check domain rules separately."}


def compare_json(left: str | Path, right: str | Path) -> dict[str, Any]:
    a, b = read_json(left), read_json(right)
    changed: list[dict[str, str]] = []
    counters: Counter[str] = Counter()

    def walk(x: Any, y: Any, p: str, depth: int = 0) -> None:
        if depth > MAX_DEPTH:
            counters['max_depth_skips'] += 1
            return
        if type(x) is not type(y):
            tag = 'type_changed'
            counters[tag] += 1
            if len(changed) < MAX_DIFF_PATHS:
                changed.append({'path': p or '$', 'kind': tag})
            return
        if isinstance(x, dict):
            for k in sorted(x.keys() | y.keys()):
                node = (p + '.' if p else '$.') + str(k)
                if k not in x or k not in y:
                    tag = 'added' if k not in x else 'removed'
                    counters[tag] += 1
                    if len(changed) < MAX_DIFF_PATHS:
                        changed.append({'path': node, 'kind': tag})
                else:
                    walk(x[k], y[k], node, depth+1)
        elif isinstance(x, list):
            for i in range(max(len(x), len(y))):
                node = p + '[' + str(i) + ']'
                if i >= len(x) or i >= len(y):
                    tag = 'added' if i >= len(x) else 'removed'
                    counters[tag] += 1
                    if len(changed) < MAX_DIFF_PATHS:
                        changed.append({'path': node, 'kind': tag})
                else:
                    walk(x[i], y[i], node, depth+1)
        elif x != y:
            counters['changed'] += 1
            if len(changed) < MAX_DIFF_PATHS:
                changed.append({'path': p or '$', 'kind': 'changed'})

    walk(a, b, '')
    return {'equal': sum(counters.values()) == 0, 'changes': dict(counters),
            'changed_paths_sample': changed, 'truncated_path_list': sum(counters.values()) > len(changed),
            'note': 'Changed *values* are deliberately not echoed.'}


def classification_metrics(path: str | Path, actual: str, pred: str,
                           positive: str) -> dict[str, Any]:
    p = ensure_file(path, '.csv')
    counts: Counter[str] = Counter()
    total = 0
    with p.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or actual not in reader.fieldnames or pred not in reader.fieldnames:
            raise InputError('actual/predicted columns not found')
        try:
            for row in reader:
                total += 1
                if total > MAX_ROWS:
                    raise InputError('CSV row limit exceeded')
                a, b = row.get(actual), row.get(pred)
                if a is None or b is None or not a.strip() or not b.strip():
                    raise InputError('blank or malformed classification label')
                if a == positive and b == positive:
                    counts['tp'] += 1
                elif a != positive and b == positive:
                    counts['fp'] += 1
                elif a == positive and b != positive:
                    counts['fn'] += 1
                else:
                    counts['tn'] += 1
        except csv.Error as exc:
            raise InputError('malformed CSV structure') from exc
    tp, fp, fn, tn = (counts[k] for k in ('tp', 'fp', 'fn', 'tn'))
    def div(n: int, d: int) -> float | None:
        return round(n/d, 6) if d else None
    precision = div(tp, tp+fp)
    recall = div(tp, tp+fn)
    return {'rows': total, 'positive_label': positive, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'accuracy': div(tp+tn, total), 'precision': precision, 'recall': recall,
            'f1': div(2*tp, 2*tp+fp+fn),
            'note': 'One-vs-rest: any non-positive label is negative; null for undefined ratios.'}

