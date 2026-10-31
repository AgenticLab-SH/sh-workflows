#!/usr/bin/env python3
"""Offline, bounded inspection of *saved* files in an authorized worktree.

Not a browser/screenshot/desktop inspection tool. Does not modify files, call
external services, run project commands, or inspect unsaved editor buffers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import deque
from pathlib import Path
import re
import stat
import sys

MAX_DEPTH = 5
MAX_ENTRIES = 160
MAX_FINGERPRINT_BYTES = 8_000_000
SKIP_DIRS = frozenset({
    '.git', '.hg', '.svn', '.venv', 'venv', '__pycache__',
    'node_modules', '.next', 'dist', 'build', 'target', '.cache',
    'coverage', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
})
SECRET_PART = re.compile(
    r'(?:^\.env(?:\..*)?$|(?:^|[._-])(?:secret|secrets|credential|credentials|'
    r'private.?key|id_rsa|id_ed25519|token|tokens|password|passwd|'
    r'auth.?key)(?:$|[._-])|\.(?:pem|p12|pfx|key)$)', re.IGNORECASE,
)


class WorkspaceError(ValueError):
    pass


def _secret(name: str) -> bool:
    return bool(SECRET_PART.search(name))


def _root(root: str | Path) -> Path:
    p = Path(root).resolve(strict=True)
    if not p.is_dir():
        raise WorkspaceError('workspace root must be a directory')
    return p


def _allowed_file(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or len(rel) > 4096:
        raise WorkspaceError('expected a bounded relative file path')
    source = Path(rel)
    if source.is_absolute() or any(x in ('..', '') for x in source.parts):
        raise WorkspaceError('only paths within workspace root are permitted')
    if any(x.startswith('.') or x.lower() == 'auth.json' or _secret(x) or x in SKIP_DIRS for x in source.parts):
        raise WorkspaceError('sensitive or excluded paths cannot be inspected')
    p = (root / source).resolve(strict=True)
    if not p.is_relative_to(root):
        raise WorkspaceError('path is outside workspace root')
    # Refuse symlinks at every step, even symlinks targeting a path within root.
    cur = root
    for part in source.parts:
        cur = cur / part
        if cur.is_symlink():
            raise WorkspaceError('symlink inspection is disabled')
    if not p.is_file():
        raise WorkspaceError('expected a regular saved file')
    return p


def file_fingerprint(root: str | Path, relative_path: str) -> dict:
    """Metadata and SHA-256 only, never emits file contents."""
    root = _root(root)
    p = _allowed_file(root, relative_path)
    st = p.stat()
    if st.st_size > MAX_FINGERPRINT_BYTES:
        raise WorkspaceError('file exceeds fingerprint size limit')
    sha = hashlib.sha256()
    with p.open('rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha.update(chunk)
    return {'path': p.relative_to(root).as_posix(), 'size_bytes': st.st_size,
            'sha256': sha.hexdigest(), 'mtime_ns': st.st_mtime_ns,
            'note': 'Saved disk file only; unsaved editor buffers are not visible.'}


def workspace_inventory(root: str | Path, depth: int = 2,
                        limit: int = 100) -> dict:
    """Only regular file names/types/sizes; bounded, no symlinks or file data."""
    root = _root(root)
    if not isinstance(depth, int) or isinstance(depth, bool) or not 0 <= depth <= MAX_DEPTH:
        raise WorkspaceError('depth must be between 0 and 5')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_ENTRIES:
        raise WorkspaceError('entry limit must be between 1 and 160')
    q = deque([(root, 0)])
    entries = []
    excluded = 0
    truncated = False
    while q:
        directory, level = q.popleft()
        try:
            with os.scandir(directory) as it:
                children = sorted(it, key=lambda f: f.name.casefold())
        except OSError:
            excluded += 1
            continue
        for entry in children:
            name = entry.name
            if name.startswith('.') or name.lower() == 'auth.json' or name in SKIP_DIRS or _secret(name):
                excluded += 1
                continue
            try:
                if entry.is_symlink():
                    excluded += 1
                    continue
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    typ = 'dir'
                elif stat.S_ISREG(info.st_mode):
                    typ = 'file'
                else:
                    excluded += 1
                    continue
                rel = Path(entry.path).relative_to(root).as_posix()
                entries.append({'path': rel, 'type': typ,
                                'size_bytes': info.st_size if typ == 'file' else None})
                if len(entries) >= limit:
                    truncated = True
                    q.clear()
                    break
                if typ == 'dir' and level < depth:
                    q.append((Path(entry.path), level + 1))
            except OSError:
                excluded += 1
    return {'entries': entries, 'entries_returned': len(entries),
            'truncated': truncated, 'excluded_count': excluded,
            'max_depth': depth, 'note': 'File names and sizes only; no content or GUI data.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Authorized workspace root; defaults to current directory')
    sub = parser.add_subparsers(dest='action', required=True)
    inventory = sub.add_parser('inventory', help='List a bounded tree of saved files, no content')
    inventory.add_argument('--depth', type=int, default=2)
    inventory.add_argument('--limit', type=int, default=100)
    fingerprint = sub.add_parser('fingerprint', help='Read one saved file hash and size')
    fingerprint.add_argument('path', help='Relative path under --root')
    fingerprint.add_argument('--expect-sha256', help='Optional previously observed SHA-256')
    try:
        args = parser.parse_args(argv)
        if args.action == 'inventory':
            result = workspace_inventory(args.root, args.depth, args.limit)
        else:
            result = file_fingerprint(args.root, args.path)
            if args.expect_sha256:
                if not re.fullmatch(r'[a-fA-F0-9]{64}', args.expect_sha256):
                    raise WorkspaceError('expected SHA-256 must have 64 hexadecimal digits')
                result['matches_expected'] = result['sha256'] == args.expect_sha256.lower()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.action == 'fingerprint' and args.expect_sha256 and not result['matches_expected'] else 0
    except (WorkspaceError, OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc) if isinstance(exc, WorkspaceError) else 'cannot inspect requested saved file'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

