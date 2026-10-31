#!/usr/bin/env python3
"""Show which project instruction files Codex would load from --root to --cwd.

Read-only. Prints metadata only (relative paths, sizes, status, whether an
override embeds the original AGENTS.md); never prints file contents, never
writes files, never reads the global Codex home. File bytes are read in memory
only for the empty-file and embedding checks.
Based on the documented AGENTS.md discovery rules; some edge cases are approximated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from kit_utils import InputError

DEFAULT_NAMES = ('AGENTS.override.md', 'AGENTS.md')
DEFAULT_MAX_BYTES = 32768
CHUNK = 65536
EMBED_READ_LIMIT = 1024 * 1024
BOM = b'\xef\xbb\xbf'
OVERRIDE = 'AGENTS.override.md'
ORIGINAL = 'AGENTS.md'
SOURCE = 'https://learn.chatgpt.com/docs/agent-configuration/agents-md'
TEMPLATE_GUIDE_LINE = '[원본 AGENTS.md가 있으면 이 줄 아래에 원본 전문을 그대로 붙인다]'.encode('utf-8')


def _is_blank(path: Path) -> bool:
    """True when the file has no non-whitespace bytes. Content is not kept."""
    with path.open('rb') as f:
        while True:
            block = f.read(CHUNK)
            if not block:
                return True
            if block.strip():
                return False


def _normalized_lines(path: Path) -> list[bytes] | None:
    """Lines with BOM removed, CRLF/CR as LF, line-end spaces/tabs removed.

    Leading and trailing blank lines are dropped, but the first line's indentation is
    kept. Returns None when the file is too large to compare. Used only for an in-memory
    comparison; the bytes are never printed or stored.
    """
    if path.stat().st_size > EMBED_READ_LIMIT:
        return None
    data = path.read_bytes()
    if data.startswith(BOM):
        data = data[len(BOM):]
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    lines = [line.rstrip(b' \t') for line in data.split(b'\n')]
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def _skip_one_preamble(lines: list[bytes], pos: int) -> int | None:
    """Index after one skippable item at `pos` (blank line, template guide line, HTML comment)."""
    if pos >= len(lines):
        return None
    line = lines[pos]
    if not line.strip() or line.strip() == TEMPLATE_GUIDE_LINE:
        return pos + 1
    stripped = line.lstrip()
    if stripped.startswith(b'<!--'):
        if b'-->' in stripped[4:]:
            return pos + 1
        for k in range(pos + 1, len(lines)):
            if b'-->' in lines[k]:
                return k + 1
    return None


def _embedded(original: Path, override: Path) -> tuple[bool | None, str | None]:
    """Whether the normalized override starts with the whole normalized original.

    Comparison is line by line from the top. Before the original, the override may only
    have blank lines, the template guide line and HTML comment blocks. Returns
    (None, 'too_large') when not compared and (None, 'empty_original') when the original
    has no content, so there is nothing to embed.
    """
    orig = _normalized_lines(original)
    over = _normalized_lines(override)
    if orig is None or over is None:
        return None, 'too_large'
    if not orig:
        return None, 'empty_original'
    pos: int | None = 0
    while pos is not None:
        if over[pos:pos + len(orig)] == orig:
            return True, None
        pos = _skip_one_preamble(over, pos)
    return False, None


def _names(fallback: str) -> list[str]:
    names = list(DEFAULT_NAMES)
    for raw in fallback.split(','):
        name = raw.strip()
        if not name:
            continue
        if '/' in name or '\\' in name or name in ('.', '..'):
            raise InputError('fallback entries must be plain file names')
        if name.lower() not in (n.lower() for n in names):
            names.append(name)
    return names


def _rel(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    return rel if rel else '.'


def inspect_chain(root: str | Path, cwd: str | Path | None = None, fallback: str = '',
                  max_bytes: int = DEFAULT_MAX_BYTES) -> dict[str, Any]:
    if max_bytes < 0:
        raise InputError('--max-bytes must be zero or positive')
    try:
        root_p = Path(root).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise InputError('root does not exist') from exc
    if not root_p.is_dir():
        raise InputError('root must be a directory')
    try:
        cwd_p = Path(cwd).resolve(strict=True) if cwd is not None else root_p
    except (OSError, RuntimeError) as exc:
        raise InputError('cwd does not exist') from exc
    if not cwd_p.is_dir():
        raise InputError('cwd must be a directory')
    if not cwd_p.is_relative_to(root_p):
        raise InputError('cwd must be inside root')
    names = _names(fallback)

    dirs = [root_p]
    for part in cwd_p.relative_to(root_p).parts:
        dirs.append(dirs[-1] / part)

    remaining = max_bytes
    total_selected = 0
    folders: list[dict[str, Any]] = []
    chain: list[str] = []
    warnings: list[str] = []
    extra_notes: list[str] = []
    for d in dirs:
        entry: dict[str, Any] = {'dir': _rel(d, root_p), 'selected': None, 'shadowed': [],
                                 'skipped_empty': [], 'original_embedded': None}
        selected_path: Path | None = None
        for name in names:
            p = d / name
            if not p.is_file():
                continue
            size = p.stat().st_size
            rel = _rel(p, root_p)
            if entry['selected'] is not None:
                item: dict[str, Any] = {'file': rel, 'bytes': size}
                if (selected_path is not None and selected_path.name.lower() == OVERRIDE.lower()
                        and name.lower() == ORIGINAL.lower()):
                    embedded, reason = _embedded(p, selected_path)
                    entry['original_embedded'] = embedded
                    item['embedded_in_selected'] = embedded
                    if reason == 'empty_original':
                        item['original_empty'] = True
                    elif reason == 'too_large':
                        item['too_large_to_compare'] = True
                entry['shadowed'].append(item)
                continue
            if _is_blank(p):
                entry['skipped_empty'].append({'file': rel, 'bytes': size})
                continue
            selected_path = p
            included = min(size, remaining)
            remaining -= included
            total_selected += size
            status = 'included' if included == size else ('partial' if included else 'not_included_limit')
            entry['selected'] = {'file': rel, 'bytes': size, 'included_bytes': included,
                                 'status': status, 'cumulative_bytes': total_selected}
            if included:
                chain.append(rel)
        sel = entry['selected']
        for empty in entry['skipped_empty']:
            warnings.append(f"{empty['file']} is empty; this check skips it, but whether Codex then reads "
                            'the next file in the same folder is not documented (behavior unconfirmed). '
                            'Do not keep an empty instruction file: fill it or remove it')
        if sel and entry['shadowed']:
            embedded = [s['file'] for s in entry['shadowed'] if s.get('embedded_in_selected') is True]
            empty_originals = [s['file'] for s in entry['shadowed'] if s.get('original_empty')]
            hidden = [s['file'] for s in entry['shadowed']
                      if s.get('embedded_in_selected') is not True and not s.get('original_empty')]
            for f in embedded:
                extra_notes.append(f"{sel['file']} embeds original {f} verbatim at the top (after line-ending "
                                   'and line-end space normalization; only blank lines, the template guide line '
                                   'and HTML comments may come before it); the original rules stay in the '
                                   'start-up instructions through the override')
            for f in empty_originals:
                extra_notes.append(f"original {f} is empty, so there is nothing to embed in {sel['file']}; "
                                   'original_embedded is null')
            if hidden:
                msg = f"{sel['file']} hides {', '.join(hidden)} in the same folder"
                if entry['original_embedded'] is False:
                    msg += '; paste the original verbatim at the top or use path B'
                elif any(s.get('too_large_to_compare') for s in entry['shadowed']):
                    msg += ('; the original is too large to compare here, so paste it verbatim at the top '
                            'or use path B')
                warnings.append(msg)
        if sel and sel['status'] != 'included':
            warnings.append(f"{sel['file']} is {sel['status']} because the {max_bytes}-byte limit was reached")
        folders.append(entry)

    if total_selected > max_bytes:
        warnings.append(f'selected files total {total_selected} bytes, over the {max_bytes}-byte limit; shorten them')
    if not (root_p / '.git').exists():
        warnings.append('root has no .git marker; Codex may pick a different project root (or only cwd)')
    return {
        'root': '.', 'cwd': _rel(cwd_p, root_p), 'candidate_names': names,
        'max_bytes': max_bytes, 'folders': folders, 'load_order': chain,
        'selected_total_bytes': total_selected,
        'included_total_bytes': max_bytes - remaining,
        'limit_reached': total_selected >= max_bytes and total_selected > 0,
        'warnings': warnings,
        'notes': [
            'Order is root to cwd; later files are closer to cwd and take precedence.',
            'Global Codex home (AGENTS.override.md / AGENTS.md there) is outside this check.',
            'Approximation of documented rules: whitespace-only counts as empty, name matching follows '
            'the local file system, separators between files are not counted, and partial inclusion '
            'at the limit may differ from the real Codex build.',
            'Empty files: the official docs say empty files are skipped but do not say whether an empty '
            'AGENTS.override.md falls through to AGENTS.md in the same folder; this check assumes it does '
            '(behavior unconfirmed), so do not rely on an empty override.',
            'original_embedded is true only when the override starts with the whole AGENTS.md, compared '
            'line by line after BOM removal, CRLF/CR to LF, line-end space/tab removal and dropping '
            'leading/trailing blank lines (first-line indentation is kept); only blank lines, the template '
            'guide line and HTML comment blocks may come before it. null means not compared or the '
            'original is empty.',
            'Instructions are assembled once at launch/session start; open a new session after changes.',
            'File contents are never printed.',
            *extra_notes,
        ],
        'source': SOURCE,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', required=True, help='project root (usually the Git root)')
    p.add_argument('--cwd', default=None, help='working folder inside root (default: root)')
    p.add_argument('--fallback', default='', help='comma-separated extra file names (project_doc_fallback_filenames)')
    p.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_BYTES, help='project_doc_max_bytes (default 32768)')
    a = p.parse_args(argv)
    try:
        res = inspect_chain(a.root, a.cwd, a.fallback, a.max_bytes)
    except (InputError, OSError) as e:
        msg = str(e) if isinstance(e, InputError) else type(e).__name__
        print(json.dumps({'error': msg}, ensure_ascii=False))
        return 2
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
