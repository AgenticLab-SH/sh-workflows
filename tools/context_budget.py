#!/usr/bin/env python3
"""Offline, read-only context size estimate for saved files under an allowed root.

Reports bytes, line counts and a rough token estimate per file, never file
contents. Does not modify files, call external services or follow symlinks.
Exit codes: 0 ok, 1 estimated total exceeds --budget, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys

MAX_FILE_BYTES = 5_000_000
MAX_FILES = 20_000
MAX_LIMIT = 500
SKIP_DIRS = frozenset({'.git', '__pycache__', 'node_modules', '.hackathon-kit', '.venv', 'venv'})
NOTE = ('Token counts are a rough approximation (about 4 ASCII characters or '
        '1 non-ASCII character per token), not the provider tokenizer. '
        'File contents are never included.')


class BudgetError(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # keep argument errors in the JSON/exit-2 contract
        raise BudgetError(message)


def estimate_tokens(text: str) -> int:
    """ceil(ASCII chars / 4) + non-ASCII chars."""
    ascii_chars = sum(1 for ch in text if ord(ch) < 128)
    return -(-ascii_chars // 4) + (len(text) - ascii_chars)


def count_lines(data: bytes) -> int:
    if not data:
        return 0
    return data.count(b'\n') + (0 if data.endswith(b'\n') else 1)


def _resolve_target(root: Path, raw: str) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 4096:
        raise BudgetError('expected a bounded path')
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise BudgetError('path does not exist') from exc
    if not resolved.is_relative_to(root):
        raise BudgetError('path is outside configured root')
    return resolved


def _measure(path: Path, excluded: dict[str, int]) -> dict | None:
    try:
        info = path.lstat()
    except OSError:
        excluded['unreadable'] += 1
        return None
    if stat.S_ISLNK(info.st_mode):
        excluded['symlink'] += 1
        return None
    if not stat.S_ISREG(info.st_mode):
        excluded['not_regular'] += 1
        return None
    if info.st_size > MAX_FILE_BYTES:
        excluded['too_large'] += 1
        return None
    try:
        data = path.read_bytes()
    except OSError:
        excluded['unreadable'] += 1
        return None
    if b'\x00' in data:
        excluded['binary'] += 1
        return None
    text = data.decode('utf-8', errors='replace')
    return {'bytes': len(data), 'lines': count_lines(data),
            'est_tokens': estimate_tokens(text)}


def _iter_files(target: Path, excluded: dict[str, int]):
    if target.is_file():
        yield target
        return
    for dirpath, dirnames, filenames in os.walk(target, followlinks=False):
        kept = []
        for name in sorted(dirnames, key=str.casefold):
            full = Path(dirpath) / name
            if name in SKIP_DIRS:
                excluded['skipped_dir'] += 1
            elif full.is_symlink():
                excluded['symlink'] += 1
            else:
                kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / name


def context_budget(paths: list[str] | None = None, root: str | Path = '.',
                   limit: int = 20, budget: int | None = None) -> dict:
    try:
        root_path = Path(root).resolve(strict=True)
    except OSError as exc:
        raise BudgetError('root does not exist') from exc
    if not root_path.is_dir():
        raise BudgetError('root must be a directory')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_LIMIT:
        raise BudgetError(f'limit must be between 1 and {MAX_LIMIT}')
    if budget is not None and (not isinstance(budget, int) or isinstance(budget, bool) or budget < 1):
        raise BudgetError('budget must be a positive integer')
    targets = [_resolve_target(root_path, p) for p in (paths or ['.'])]

    excluded = {k: 0 for k in ('skipped_dir', 'binary', 'too_large', 'symlink',
                               'not_regular', 'unreadable')}
    seen: set[Path] = set()
    files = []
    truncated = False
    for target in targets:
        if any(part in SKIP_DIRS for part in target.relative_to(root_path).parts):
            excluded['skipped_dir'] += 1
            continue
        for path in _iter_files(target, excluded):
            if path in seen:
                continue
            seen.add(path)
            if len(seen) > MAX_FILES:
                truncated = True
                break
            row = _measure(path, excluded)
            if row is not None:
                files.append({'path': path.relative_to(root_path).as_posix(), **row})
        if truncated:
            break

    files.sort(key=lambda r: (-r['est_tokens'], -r['bytes'], r['path']))
    total_tokens = sum(r['est_tokens'] for r in files)
    result = {
        'root': root_path.name or str(root_path),
        'files_counted': len(files),
        'total_bytes': sum(r['bytes'] for r in files),
        'total_lines': sum(r['lines'] for r in files),
        'total_est_tokens': total_tokens,
        'largest': files[:limit],
        'limit': limit,
        'excluded': excluded,
        'excluded_count': sum(excluded.values()),
        'truncated': truncated,
        'budget': budget,
        'over_budget': bool(budget is not None and total_tokens > budget),
        'note': NOTE,
    }
    if result['over_budget']:
        result['warning'] = (f'estimated {total_tokens} tokens exceeds budget {budget}; '
                             'read summaries or a smaller file set instead')
    return result


def main(argv=None):
    parser = _Parser(description=__doc__)
    parser.add_argument('paths', nargs='*', help='Files or folders under --root (default: root)')
    parser.add_argument('--root', default='.', help='Allowed root; defaults to current directory')
    parser.add_argument('--limit', type=int, default=20, help='Largest files to list (1-500)')
    parser.add_argument('--budget', type=int, help='Estimated token budget; exit 1 if exceeded')
    try:
        args = parser.parse_args(argv)
        result = context_budget(args.paths, args.root, args.limit, args.budget)
    except BudgetError as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2
    except (OSError, ValueError):
        print(json.dumps({'error': 'cannot inspect requested paths'}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['over_budget'] else 0


if __name__ == '__main__':
    sys.exit(main())
