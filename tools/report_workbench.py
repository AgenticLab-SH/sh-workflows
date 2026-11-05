#!/usr/bin/env python3
"""Local-only append-only decision/evidence report viewer. Standard library only.

No external API, no Git push, no screenshots or browser automation. The viewer
only serves explicitly recorded summary events, not source files or input CSVs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

EVENT_DIR = '.review-workbench/events'
MAX_EVENT_BYTES = 12288
MAX_EVENTS = 400
MAX_TEXT = 1500
KINDS = ('question', 'decision', 'implementation', 'test', 'result', 'risk', 'handoff')
STATUSES = ('proposed', 'confirmed', 'implemented', 'verified', 'blocked', 'not_run')
AGENT_RE = re.compile(r'^[a-z][a-z0-9_-]{0,39}$')
SENSITIVE_RE = re.compile(r'(?i)(?:gh[pousr]_[a-z0-9]{16,}|sk-[a-z0-9_-]{20,}|cand_[a-z0-9]{8,}|password\s*[:=]|api[_ -]?key\s*[:=])')


def valid_root(root: str | Path) -> Path:
    p = Path(root).resolve(strict=True)
    if not p.is_dir():
        raise ValueError('root must be an existing directory')
    return p


def events_dir(root: Path, create: bool = False) -> Path:
    parent = root / '.review-workbench'
    events = parent / 'events'
    for p in (parent, events):
        if p.is_symlink():
            raise ValueError('event directory symlink is not allowed')
    if create:
        parent.mkdir(mode=0o700, exist_ok=True)
        events.mkdir(mode=0o700, exist_ok=True)
    return events


def check_text(value: str, field: str) -> str:
    if len(value) > MAX_TEXT:
        raise ValueError(f'{field} exceeds {MAX_TEXT} characters')
    if SENSITIVE_RE.search(value):
        raise ValueError(f'{field} looks sensitive; use a sanitized summary instead')
    if '\x00' in value:
        raise ValueError(f'{field} contains NUL')
    return value.strip()


def record(root: Path, *, agent: str, kind: str, status: str, title: str,
           summary: str = '', why: str = '', alternatives: str = '',
           evidence: str = '', files: str = '', risks: str = '', next_action: str = '') -> dict:
    if not AGENT_RE.fullmatch(agent):
        raise ValueError('agent must be a short lowercase safe identifier')
    if kind not in KINDS or status not in STATUSES:
        raise ValueError('unsupported kind or status')
    fields = {k: check_text(v, k) for k, v in {
        'title': title, 'summary': summary, 'why': why,
        'alternatives': alternatives, 'evidence': evidence,
        'files': files, 'risks': risks, 'next_action': next_action
    }.items()}
    if not fields['title']:
        raise ValueError('title must not be blank')
    eid = uuid.uuid4().hex
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds')
    entry = {'schema': 1, 'id': eid, 'time_utc': stamp,
             'agent': agent, 'kind': kind, 'status': status, **fields}
    data = (json.dumps(entry, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    if len(data) > MAX_EVENT_BYTES:
        raise ValueError('event too large')
    folder = events_dir(root, create=True)
    filename = f'{stamp[:10].replace("-", "")}-{agent}-{eid}.json'
    path = folder / filename
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'wb') as fp:
        fp.write(data)
    return entry


def read_events(root: Path) -> list[dict]:
    folder = events_dir(root)
    if not folder.exists():
        return []
    if not folder.is_dir():
        raise ValueError('event path is not a directory')
    out: list[dict] = []
    for path in sorted(folder.glob('*.json'), reverse=True):
        if len(out) >= MAX_EVENTS:
            break
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_EVENT_BYTES:
            continue
        try:
            item = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(item, dict) or item.get('schema') != 1:
                continue
            if not AGENT_RE.fullmatch(str(item.get('agent', ''))):
                continue
            if item.get('kind') not in KINDS or item.get('status') not in STATUSES:
                continue
            allowed = ('id', 'time_utc', 'agent', 'kind', 'status', 'title', 'summary',
                       'why', 'alternatives', 'evidence', 'files', 'risks', 'next_action')
            safe = {k: item[k] for k in allowed if isinstance(item.get(k), str)}
            if SENSITIVE_RE.search(json.dumps(safe, ensure_ascii=False)):
                continue
            out.append(safe)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            continue
    return sorted(out, key=lambda e: (e.get('time_utc', ''), e.get('id', '')), reverse=True)


def validate_preview(url: str) -> str:
    if not url:
        return ''
    parsed = urlparse(url)
    if (parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1')
            or parsed.username or parsed.password or parsed.path not in ('', '/')
            or parsed.query or parsed.fragment or parsed.port is None):
        raise ValueError('preview URL must be a local HTTP loopback root with an explicit port')
    return url


PUBLIC_SK_CI_CSS = ":root{--accent:#EA002C;--soft:#fff1ef;}"

HTML = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Decision & Evidence Workbench</title>
<style>
:root{--bg:#f6f7f9;--ink:#162233;--muted:#526073;--border:#dce1e8;--panel:#fff;--accent:#225f81;--soft:#e5f1f6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,'Segoe UI',sans-serif}
header{padding:20px clamp(15px,4vw,45px);background:var(--panel);border-bottom:1px solid var(--border)}h1{font-size:22px;margin:0 0 3px}header p{color:var(--muted);margin:0;font-size:13px}
main{max-width:1150px;margin:auto;padding:18px 20px 50px}
nav{display:flex;gap:9px;margin:0 0 16px}button{border:1px solid var(--border);background:white;padding:9px 18px;border-radius:10px;cursor:pointer;font:inherit}button[aria-selected="true"]{background:var(--accent);color:white;border-color:var(--accent)}
#stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:0 0 16px}.stat,.card,.empty{border:1px solid var(--border);background:var(--panel);border-radius:12px;padding:15px}.stat b{display:block;font-size:23px}.stat small{color:var(--muted)}
#filters{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:15px}select{padding:8px;border:1px solid var(--border);border-radius:8px;background:white}#updated{margin-left:auto;color:var(--muted);font-size:12px}
.card{margin:10px 0}.top{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.pill{border-radius:6px;padding:2px 8px;background:var(--soft);font-size:12px;font-weight:600}.status{background:#f1f2f5}.date{color:var(--muted);font-size:12px;margin-left:auto}
h2{font-size:17px;margin:7px 0}.details{display:grid;grid-template-columns:130px 1fr;gap:5px 10px;margin:12px 0 0}.details dt{color:var(--muted)}.details dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}
#preview{margin:18px 0;padding:15px;border:1px solid var(--border);border-radius:12px;background:white}#preview iframe{width:100%;height:55vh;border:1px solid var(--border)}
.empty{text-align:center;color:var(--muted)}.hidden{display:none!important}footer{color:var(--muted);font-size:12px;padding-top:16px}a{color:var(--accent)}
@media(max-width:600px){#stats{grid-template-columns:repeat(2,1fr)}.details{grid-template-columns:1fr}main{padding:12px}}
</style></head><body><header><h1>Decision & Evidence Workbench</h1><p>Local-only, cumulative and read-only viewer. Files are recorded explicitly by authorized agents. No external transfer.</p></header>
<main><nav aria-label="Views"><button id="tab-report" aria-selected="true">Reports / decisions</button><button id="tab-output" aria-selected="false">Results / verification</button></nav>
<section id="stats"><div class="stat"><b id="n-all">0</b><small>Events</small></div><div class="stat"><b id="n-agents">0</b><small>Agents</small></div><div class="stat"><b id="n-verified">0</b><small>Verified</small></div><div class="stat"><b id="n-issues">0</b><small>Blocked / not run</small></div></section>
<div id="filters"><label for="agent">Agent </label><select id="agent"><option value="">All agents</option></select><label for="status">Status </label><select id="status"><option value="">All statuses</option></select><span id="updated">Waiting for events</span></div>
<div id="reports"></div><section id="preview" class="hidden"><h2>Optional local output preview</h2><p>If the browser proxy blocks the embedded app, open its port through the provided IDE Browser instead.</p><a id="preview-link" rel="noopener" target="_blank">Open output in local browser</a><iframe id="preview-frame" title="Local app output" referrerpolicy="no-referrer" loading="lazy"></iframe></section>
<footer>Observed file/test evidence is separate from a human UI observation. Never claim a non-run check passed. Only local sanitized summaries belong here.</footer></main>
<script>
const PREVIEW_URL=__PREVIEW_JSON__;let all=[],tab='report';
const byId=id=>document.getElementById(id);
const cell=(name,value)=>{let dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;return [dt,dd]};
function makeCard(e){let node=document.createElement('article');node.className='card';let top=document.createElement('div');top.className='top';for(let val of [e.kind,e.status,e.agent]){let badge=document.createElement('span');badge.className='pill '+(val===e.status?'status':'');badge.textContent=val;top.append(badge)}let date=document.createElement('span');date.className='date';date.textContent=e.time_utc||'';top.append(date);node.append(top);let h=document.createElement('h2');h.textContent=e.title||'(untitled)';node.append(h);let dl=document.createElement('dl');dl.className='details';for(let key of [['summary','Summary'],['why','Why / decision'],['alternatives','Alternatives'],['evidence','Observed evidence'],['files','Modules / changed files'],['risks','Risks / limits'],['next_action','Next action']]){if(e[key[0]])dl.append(...cell(key[1],e[key[0]]))}node.append(dl);return node}
function render(){let filtered=all.filter(e=>(!byId('agent').value||byId('agent').value===e.agent)&&(!byId('status').value||byId('status').value===e.status));if(tab==='output')filtered=filtered.filter(e=>['result','test'].includes(e.kind));let box=byId('reports');box.replaceChildren();if(!filtered.length){let msg=document.createElement('p');msg.className='empty';msg.textContent=tab==='output'?'No result/test evidence recorded yet.':'No local reports yet.';box.append(msg)}else for(let event of filtered)box.append(makeCard(event));byId('preview').classList.toggle('hidden',!(tab==='output'&&PREVIEW_URL));}
function setTab(t){tab=t;byId('tab-report').setAttribute('aria-selected',String(t==='report'));byId('tab-output').setAttribute('aria-selected',String(t==='output'));render()}
byId('tab-report').onclick=()=>setTab('report');byId('tab-output').onclick=()=>setTab('output');
byId('agent').onchange=render;byId('status').onchange=render;
if(PREVIEW_URL){byId('preview-link').href=PREVIEW_URL;byId('preview-frame').src=PREVIEW_URL}
async function refresh(){try{let r=await fetch('/api/events',{cache:'no-store'});if(!r.ok)throw Error('not ready');let j=await r.json();all=j.events||[];byId('n-all').textContent=all.length;byId('n-agents').textContent=new Set(all.map(e=>e.agent)).size;byId('n-verified').textContent=all.filter(e=>e.status==='verified').length;byId('n-issues').textContent=all.filter(e=>['blocked','not_run'].includes(e.status)).length;for(let [id,values] of [['agent',[...new Set(all.map(e=>e.agent))].sort()],['status',[...new Set(all.map(e=>e.status))].sort()]]){let s=byId(id),v=s.value;s.replaceChildren(new Option('All '+id+'s',''));for(let val of values)s.add(new Option(val,val));s.value=v}byId('updated').textContent='Updated '+new Date().toLocaleTimeString();render()}catch(_){byId('updated').textContent='Local viewer not ready';}}
refresh();setInterval(refresh,5000);
</script></body></html>'''


def handler_factory(root: Path, preview: str, theme: str = "neutral"):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/api/events':
                body = json.dumps({'events': read_events(root)}, ensure_ascii=False).encode('utf-8')
                return self.respond(body, 'application/json; charset=utf-8')
            if self.path == '/health':
                return self.respond(b'{"status":"ok","external_upload":false}', 'application/json')
            if self.path == '/':
                page = HTML.replace('__PREVIEW_JSON__', json.dumps(preview))
                if theme == 'sk-public':
                    page = page.replace('</style></head>', '</style><style>' + PUBLIC_SK_CI_CSS + '</style></head>')
                page = page.encode('utf-8')
                return self.respond(page, 'text/html; charset=utf-8')
            self.send_error(404, 'Not found')

        def respond(self, body: bytes, content_type: str):
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-src http://localhost:* http://127.0.0.1:*")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline-first multi-agent workbench')
    parser.add_argument('--root', default='.', help='Authorized local worktree')
    sub = parser.add_subparsers(dest='command', required=True)
    note = sub.add_parser('note', help='Append one sanitized local event')
    note.add_argument('--agent', required=True)
    note.add_argument('--kind', required=True, choices=KINDS)
    note.add_argument('--status', required=True, choices=STATUSES)
    note.add_argument('--title', required=True)
    for arg in ('summary', 'why', 'alternatives', 'evidence', 'files', 'risks', 'next-action'):
        note.add_argument('--' + arg, default='')
    serve = sub.add_parser('serve', help='Read-only local report browser')
    serve.add_argument('--host', default='127.0.0.1', choices=('127.0.0.1', '0.0.0.0'))
    serve.add_argument('--port', type=int, default=8765)
    serve.add_argument('--preview-url', default='')
    serve.add_argument('--theme', choices=('neutral','sk-public'), default='neutral')
    sub.add_parser('list', help='Read-only JSON summary to terminal')
    args = parser.parse_args(argv)
    try:
        root = valid_root(args.root)
        if args.command == 'note':
            obj = record(root, agent=args.agent, kind=args.kind, status=args.status,
                         title=args.title, summary=args.summary, why=args.why,
                         alternatives=args.alternatives, evidence=args.evidence,
                         files=args.files, risks=args.risks, next_action=args.next_action)
            print(json.dumps({'saved': True, 'id': obj['id'], 'kind': obj['kind']}, ensure_ascii=False))
        elif args.command == 'list':
            for item in read_events(root):
                print(f"{item['time_utc']} [{item['agent']}/{item['kind']}/{item['status']}] {item['title']}")
        else:
            preview = validate_preview(args.preview_url)
            if not 1 <= args.port <= 65535:
                raise ValueError('port must be between 1 and 65535')
            if args.host == '0.0.0.0':
                print('WARNING: binds to all interfaces; only use in a trusted and authorized IDE container.', file=sys.stderr)
            server = ThreadingHTTPServer((args.host, args.port), handler_factory(root, preview, args.theme))
            print(f'Read-only dashboard on http://{args.host}:{args.port} (press Ctrl+C to stop)', flush=True)
            try:
                server.serve_forever(poll_interval=0.25)
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
    except (OSError, ValueError) as e:
        parser.error(str(e))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
