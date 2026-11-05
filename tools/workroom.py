#!/usr/bin/env python3
"""Isolated, local-first workroom for an explicitly confirmed project root.

No working directory discovery, home crawling, Git push, screenshot capture,
external API calls, hidden project edits, source execution, or overwrite.
All created files remain under <confirmed-root>/.cofa-workbench/.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from uuid import uuid4

CONTROL = '.cofa-workbench'
DOCS = {
    'REQUIREMENTS_MAP.md': '# Requirements, evidence and required deliverables\n\nOnly work from the authorized root README and local files. Link required output and each rule to its source, test and owner. Never rewrite the original README.\n\n| ID | Origin (README / stakeholder / observed data / assumption) | Requirement | Output / path | Test / status | Owner |\n| --- | --- | --- | --- | --- | --- |\n',
    'DATA_PROFILE.md': '# Input data profile (LOCAL ONLY)\n\nDescribe authorized file names, row granularity, column types, missingness counts, join keys and unusual cases. **Do not duplicate confidential raw rows here.** The original data stays in the task folder.\n\n| Source file | Row grain | Columns / types | Missing / duplicate counts | Cross-file relationships | Open question |\n| --- | --- | --- | --- | --- | --- |\n',
    'HR_QUESTIONS.md': '# Questions to authorized stakeholder\n\nUse one concrete, decision-changing question at a time or an officially permitted batch.\n\n| ID | Priority | Source/ambiguity | Copy-ready question | Status | Related requirement |\n| --- | --- | --- | --- | --- | --- |\n',
    'HR_ANSWERS.md': '# Authorized stakeholder answers (LOCAL ONLY)\n\nPaste answers **here inside the confirmed project** only when allowed. Do not copy to the public kit or remote services. Keep source, time, question ID, actual answer and remaining uncertainty.\n',
    'DECISIONS.md': '# Human-owned decisions\n\n| ID | Confirmed source / unresolved | Chosen option | Alternative | Reason | Affected module / test | Owner |\n| --- | --- | --- | --- | --- | --- | --- |\n',
    'MODULE_MAP.md': '# Architecture and source ownership\n\n| Module / function | Input | Output | Validation / error handling | State owner | Writer agent |\n| --- | --- | --- | --- | --- | --- |\n',
    'VERIFICATION.md': '# Expected vs actual evidence\n\n| ID | Requirement | Input class | Expected | Actual observed | PASS / FAIL / NOT_RUN | File / command |\n| --- | --- | --- | --- | --- | --- | --- |\n',
    'AGENT_ASSIGNMENTS.md': '# Parallel agent assignments\n\nA single writer owns each source file. Other agents review without writing. Coordinator integrates; no global settings edits.\n\n| Agent | File ownership | Assignment / stop condition | Result evidence |\n| --- | --- | --- | --- |\n',
    '00_WORKROOM_INDEX.md': '# Workroom evidence ladder (local only)\n\nL0 원본·초기 상태 → L1 요구·질문 → L2 사람의 결정 → L3 구현 → L4 검증.\n\nP0~P3는 긴급도이며 자료 레벨과 무관. 상태는 PROPOSED/CONFIRMED/IMPLEMENTED/PASS/FAIL/NOT_RUN/BLOCKED로 구분.\n\n각 에이전트는 독립 이벤트를 기록하고 코드 파일은 한 작성자만 수정. PASS는 실제 관측 명령과 결과가 있을 때만. 실제 과제·개인 자료 외부 전송 금지.\n\n| Level | Canonical record | Owner |\n| --- | --- | --- |\n| L0 | ROOT_PATH / INITIAL_STATE / FILES_AT_START | Participant |\n| L1 | REQUIREMENTS_MAP / DATA_PROFILE / HR_QUESTIONS / HR_ANSWERS | Requirements or data |\n| L2 | DECISIONS / MODULE_MAP | Participant + coordinator |\n| L3 | AGENT_ASSIGNMENTS / implementation events | One writer per source file |\n| L4 | VERIFICATION / FINAL_EXPLANATION | QA + participant |\n',
    'FINAL_EXPLANATION.md': '# Explain in your own words (before any no-AI stage)\n\nExplain chosen approach and alternatives; module/data flow and accepted-state owner; implemented vs confirmed assumption vs excluded; normal and failure handling; measurable validation and future improvement; what AI proposed, accepted, revised or rejected and why.\n\nThis is a generic understanding checklist, not an answer sheet. Stop AI assistance when a monitored no-AI phase begins.\n',
}
KINDS = ('question', 'decision', 'implementation', 'verification', 'risk', 'handoff', 'result')
STATES = ('proposed', 'confirmed', 'implemented', 'pass', 'fail', 'not_run', 'blocked')
# Data levels describe the evidence chain, not severity or approval.
LEVELS = ('L0', 'L1', 'L2', 'L3', 'L4')
DEFAULT_LEVEL = {'question': 'L1', 'risk': 'L1', 'decision': 'L2',
                 'implementation': 'L3', 'handoff': 'L3',
                 'verification': 'L4', 'result': 'L4'}
PRIORITIES = ('none', 'P0', 'P1', 'P2', 'P3')
BASES = ('unspecified', 'official', 'stakeholder', 'human', 'observed', 'assumption', 'agent')
ROLES = ('coordinator', 'requirements', 'data', 'stakeholder', 'algorithm',
         'implementation', 'ui', 'qa', 'integration', 'other')
DECISION_BY = ('unconfirmed', 'human', 'stakeholder', 'official')
METADATA = ('level', 'priority', 'basis', 'role', 'source_ref', 'decision_by')
FIELDS = ('title', 'summary', 'reason', 'alternative', 'evidence', 'module', 'limitation', 'next_action')
IDENTIFIER = re.compile(r'^[a-z][a-z0-9_-]{0,39}$')
SENSITIVE = re.compile(r'(?i)(gh[pousr]_[a-z0-9]{12,}|sk-[a-z0-9_-]{18,}|cand_[a-z0-9]{8,}|(?:password|api[_-]?key|secret|token)\s*[:=]|[\w.+-]+@[\w.-]+\.[a-z]{2,})')
MAX_BYTES = 12288
MAX_TEXT = 1500
MAX_EVENTS = 450


def confirmed_root(text: str) -> Path:
    root = Path(text).resolve(strict=True)
    if not root.is_dir() or root == root.parent or root == Path.home().resolve():
        raise ValueError('Only an explicitly confirmed project folder, not / or the home directory')
    return root


def control_root(root: Path, require: bool = True) -> Path:
    dest = root / CONTROL
    if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
        raise ValueError('Control folder is unsafe or symlinked')
    if require and not dest.is_dir():
        raise ValueError('Pre-clone baseline missing. Confirm pwd, then create the baseline before Clone')
    for segment in ('kit', 'docs', 'events'):
        p = dest / segment
        if p.is_symlink() or (p.exists() and not p.is_dir()):
            raise ValueError(f'Unsafe control subfolder: {segment}')
    return dest


def verify_root(root: Path, require_kit: bool = True) -> Path:
    dest = control_root(root)
    marker = dest / 'ROOT_PATH.txt'
    baseline = dest / 'INITIAL_STATE.md'
    listing = dest / 'FILES_AT_START.tsv'
    for p in (marker, baseline, listing):
        if not p.is_file() or p.is_symlink():
            raise ValueError(f'Baseline file missing or unsafe: {p.name}')
    recorded = marker.read_text(encoding='utf-8').strip()
    if recorded != str(root):
        raise ValueError('The recorded root differs from --root; stop instead of changing directory')
    if require_kit and not (dest / 'kit' / 'tools' / 'workroom.py').is_file():
        raise ValueError('Public kit not present under the confirmed control folder')
    return dest


def write_once(path: Path, text: str) -> bool:
    if path.is_symlink():
        raise ValueError(f'Unsafe symlink: {path.name}')
    try:
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    return True


def init(root: Path) -> dict:
    dest = verify_root(root)
    for name in ('docs', 'events'):
        (dest / name).mkdir(mode=0o700, exist_ok=True)
    created = [name for name, text in DOCS.items() if write_once(dest / 'docs' / name, text)]
    return {'result': 'initialized', 'root_matches_initial': True, 'created_docs': created,
            'preserved_existing': len(DOCS) - len(created), 'working_dir': CONTROL,
            'report_port': 3000, 'service_port': 3001,
            'source_files_changed': False, 'git_push': False}


def clean(value: str, key: str) -> str:
    if len(value) > MAX_TEXT or '\x00' in value or SENSITIVE.search(value):
        raise ValueError(f'{key} contains a possibly sensitive string or is too long')
    return value.strip()


def note(root: Path, agent: str, kind: str, state: str, data: dict[str, str]) -> dict:
    dest = verify_root(root)
    if not IDENTIFIER.fullmatch(agent):
        raise ValueError('Agent label must be lowercase and short')
    if kind not in KINDS or state not in STATES:
        raise ValueError('Invalid event kind/state')
    fields = {k: clean(data.get(k, ''), k) for k in FIELDS}
    level = data.get('level', 'auto') or 'auto'
    level = DEFAULT_LEVEL[kind] if level == 'auto' else level
    priority = data.get('priority', 'none') or 'none'
    basis = data.get('basis', 'unspecified') or 'unspecified'
    role = data.get('role', 'other') or 'other'
    source_ref = clean(data.get('source_ref', ''), 'source_ref')
    decision_by = data.get('decision_by', 'unconfirmed') or 'unconfirmed'
    if level not in LEVELS or priority not in PRIORITIES or basis not in BASES or role not in ROLES or decision_by not in DECISION_BY:
        raise ValueError('Invalid report level, priority, basis, role or decision owner')
    if kind == 'decision' and state == 'confirmed' and decision_by == 'unconfirmed':
        raise ValueError('Confirmed decision needs the participant, stakeholder or official owner')
    if not fields['title']:
        raise ValueError('Event title must not be empty')
    if state == 'pass' and (kind not in ('verification', 'result') or not fields['evidence'] or basis != 'observed'):
        raise ValueError('PASS requires observed verification/result evidence (basis=observed)')
    payload = {'version': 2, 'id': uuid4().hex,
               'time_utc': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
               'agent': agent, 'kind': kind, 'state': state,
               'level': level, 'priority': priority, 'basis': basis, 'role': role,
               'source_ref': source_ref, 'decision_by': decision_by, **fields}
    blob = (json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    if len(blob) > MAX_BYTES:
        raise ValueError('Event too large')
    directory = dest / 'events'
    directory.mkdir(mode=0o700, exist_ok=True)
    path = directory / f'{payload["time_utc"][:10].replace("-", "")}_{agent}_{payload["id"]}.json'
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'wb') as fp:
        fp.write(blob)
    return {'saved_local_only': True, 'id': payload['id'], 'kind': kind, 'state': state}


def list_events(dest: Path) -> list[dict]:
    directory = dest / 'events'
    if not directory.is_dir() or directory.is_symlink():
        return []
    events = []
    for p in sorted(directory.glob('*.json'), reverse=True):
        if len(events) >= MAX_EVENTS:
            break
        try:
            if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
                continue
            raw = json.loads(p.read_text(encoding='utf-8'))
            if raw.get('version') not in (1, 2) or raw.get('kind') not in KINDS or raw.get('state') not in STATES:
                continue
            if not IDENTIFIER.fullmatch(str(raw.get('agent', ''))):
                continue
            level = str(raw.get('level', DEFAULT_LEVEL[raw['kind']]))
            if level not in LEVELS:
                continue
            accepted = {k: str(raw.get(k, '')) for k in ('id', 'time_utc', 'agent', 'kind', 'state') + FIELDS}
            accepted.update({'level': level, 'priority': str(raw.get('priority', 'none')),
                             'basis': str(raw.get('basis', 'unspecified')),
                             'role': str(raw.get('role', 'other')),
                             'source_ref': str(raw.get('source_ref', '')),
                             'decision_by': str(raw.get('decision_by', 'unconfirmed'))})
            if (accepted['priority'] not in PRIORITIES or accepted['basis'] not in BASES or
                    accepted['role'] not in ROLES or accepted['decision_by'] not in DECISION_BY):
                continue
            if SENSITIVE.search(json.dumps(accepted, ensure_ascii=False)):
                continue
            events.append(accepted)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError):
            continue
    return sorted(events, key=lambda v: (v['time_utc'], v['id']), reverse=True)


def snapshot_count(dest: Path) -> int:
    listing = dest / 'FILES_AT_START.tsv'
    try:
        with listing.open(encoding='utf-8') as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def summary(root: Path) -> dict:
    dest = verify_root(root)
    events = list_events(dest)
    cats = Counter(e['kind'] for e in events)
    states = Counter(e['state'] for e in events)
    return {'app': 'Cofa Workroom', 'scope': 'confirmed_root_only',
            'root_confirmed': True, 'baseline_saved': True,
            'initial_file_count': snapshot_count(dest),
            'docs': {name: (dest / 'docs' / name).is_file() for name in DOCS},
            'total_events': len(events),
            'counts_by_level': dict(Counter(e['level'] for e in events)),
            'counts_by_priority': dict(Counter(e['priority'] for e in events)),
            'counts_by_kind': dict(cats),
            'counts_by_state': dict(states), 'agents': sorted(set(e['agent'] for e in events)),
            'events': events, 'report_port': 3000, 'service_port': 3001,
            'service_status': 'MANUAL_CHECK', 'external_upload': False,
            'source_files_changed_by_workroom': False}


def serve(root: Path, port: int, host: str):
    dest = verify_root(root)
    if not 1 <= port <= 65535:
        raise ValueError('Invalid port')
    if host not in ('127.0.0.1', '0.0.0.0'):
        raise ValueError('Only local or opt-in trusted IDE binding is allowed')
    ui = Path(__file__).resolve().with_name('workroom_ui.html')
    if not ui.is_file():
        raise ValueError('Dashboard HTML is missing from public kit')
    page = ui.read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                return self.send_content(200, page, 'text/html; charset=utf-8')
            if self.path == '/api/state':
                blob = json.dumps(summary(root), ensure_ascii=False).encode('utf-8')
                return self.send_content(200, blob, 'application/json; charset=utf-8')
            if self.path == '/health':
                return self.send_content(200, b'{"ok":true,"report_port":3000}', 'application/json')
            return self.send_content(404, b'Not found', 'text/plain')

        def do_POST(self):
            return self.send_content(405, b'Read only', 'text/plain')

        def send_content(self, code, blob, typ):
            self.send_response(code)
            for k, v in {
                'Content-Type': typ, 'Content-Length': str(len(blob)),
                'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
                'Referrer-Policy': 'no-referrer',
                'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-src http://127.0.0.1:3001 http://localhost:3001",
            }.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(blob)

        def log_message(self, fmt, *args):
            return  # Avoid local request logging of private URLs.

    if host == '0.0.0.0':
        print('WARNING: binds to all container interfaces; use only in trusted explicitly authorized IDE.', file=sys.stderr)
    server = ThreadingHTTPServer((host, port), Handler)
    print(f'Local report viewer http://{host}:{port}  | service uses separate port 3001', flush=True)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv=None):
    p = argparse.ArgumentParser(description='Strictly bounded local-only workroom')
    p.add_argument('--root', required=True, help='Explicitly confirmed task folder; no automatic directory search')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Preserve pre-Clone baseline and create local docs only')
    sub.add_parser('status', help='Print current local metadata/events as JSON')
    log = sub.add_parser('note', help='Append one independent local event')
    log.add_argument('--agent', required=True)
    log.add_argument('--kind', choices=KINDS, required=True)
    log.add_argument('--state', choices=STATES, required=True)
    log.add_argument('--title', required=True)
    for field in FIELDS:
        if field != 'title':
            log.add_argument('--' + field.replace('_', '-'), default='')
    log.add_argument('--level', choices=('auto',) + LEVELS, default='auto')
    log.add_argument('--priority', choices=PRIORITIES, default='none')
    log.add_argument('--basis', choices=BASES, default='unspecified')
    log.add_argument('--role', choices=ROLES, default='other')
    log.add_argument('--source-ref', default='', help='Local reference ID only; no private raw content')
    log.add_argument('--decision-by', choices=DECISION_BY, default='unconfirmed')
    viewer = sub.add_parser('serve', help='Read-only UI, port 3000 by default')
    viewer.add_argument('--host', choices=('127.0.0.1', '0.0.0.0'), default='127.0.0.1')
    viewer.add_argument('--port', type=int, default=3000)
    args = p.parse_args(argv)
    try:
        root = confirmed_root(args.root)
        if args.command == 'init':
            value = init(root)
        elif args.command == 'status':
            value = summary(root)
        elif args.command == 'note':
            value = note(root, args.agent, args.kind, args.state,
                         {field: getattr(args, field) for field in FIELDS + METADATA})
        else:
            serve(root, args.port, args.host)
            return 0
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
