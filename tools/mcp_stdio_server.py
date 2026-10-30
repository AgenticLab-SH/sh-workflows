#!/usr/bin/env python3
"""Small read-only MCP-over-stdio JSON-RPC server; offline, root-confined.

No hosted endpoint; no network; no file modifications; no shell execution.
Only run this when the MCP host / environment explicitly allows it.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys

from kit_utils import (restricted_path, InputError, csv_audit, validate_json,
                       compare_json, classification_metrics)
from workspace_probe import file_fingerprint, workspace_inventory, WorkspaceError

ROOT = Path(os.environ.get('MCP_ALLOWED_ROOT', '.')).resolve()
MAX_REQUEST_BYTES = 1_000_000

TOOLS = [
    {'name': 'audit_csv', 'description': 'Read-only CSV schema, missing, duplicate summary; no row values.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'}, 'required_columns': {'type': 'array', 'items': {'type': 'string'}},
         'unique_columns': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['path']}},
    {'name': 'validate_json', 'description': 'Validate local JSON top-level object and required keys without values.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'}, 'required_keys': {'type': 'array', 'items': {'type': 'string'}}},
         'required': ['path']}},
    {'name': 'compare_json', 'description': 'Compare two local JSON files; return changed paths but not values.',
     'inputSchema': {'type': 'object', 'properties': {
         'left': {'type': 'string'}, 'right': {'type': 'string'}},
         'required': ['left', 'right']}},
    {'name': 'classification_metrics', 'description': 'Read-only confusion counts/precision/recall for local CSV.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'}, 'actual': {'type': 'string'},
         'predicted': {'type': 'string'}, 'positive': {'type': 'string'}},
         'required': ['path', 'actual', 'predicted', 'positive']}},
    {'name': 'workspace_inventory', 'description': 'Bounded names and sizes of saved workspace files; no screen or file content.',
     'inputSchema': {'type': 'object', 'properties': {
         'depth': {'type': 'integer', 'minimum': 0, 'maximum': 5},
         'limit': {'type': 'integer', 'minimum': 1, 'maximum': 160}}}},
    {'name': 'file_fingerprint', 'description': 'SHA-256 and size of one saved root-local file; no file content.',
     'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
]


def local_file(path: str, suffix: str) -> Path:
    if not isinstance(path, str) or not path or len(path) > 4096:
        raise InputError('missing or oversized local path')
    return restricted_path(path, ROOT, suffix)


def arr(items):
    if not isinstance(items, list) or len(items) > 100 or any(not isinstance(x, str) or len(x) > 256 for x in items):
        raise InputError('invalid string list argument')
    return items


def tool_call(name, args):
    if not isinstance(args, dict):
        raise InputError('arguments must be an object')
    if name == 'audit_csv':
        return csv_audit(local_file(args['path'], '.csv'), arr(args.get('required_columns', [])),
                         arr(args.get('unique_columns', [])))
    if name == 'validate_json':
        return validate_json(local_file(args['path'], '.json'), arr(args.get('required_keys', [])))
    if name == 'compare_json':
        return compare_json(local_file(args['left'], '.json'), local_file(args['right'], '.json'))
    if name == 'classification_metrics':
        return classification_metrics(local_file(args['path'], '.csv'),
                                      args['actual'], args['predicted'], args['positive'])
    if name == 'workspace_inventory':
        return workspace_inventory(ROOT, args.get('depth', 2), args.get('limit', 100))
    if name == 'file_fingerprint':
        return file_fingerprint(ROOT, args['path'])
    raise InputError('unknown tool')


def handle(request):
    if not isinstance(request, dict) or request.get('jsonrpc') != '2.0':
        return {'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request,dict) else None,
                'error': {'code': -32600, 'message': 'invalid request'}}
    mid, method = request.get('id'), request.get('method')
    if method == 'notifications/initialized' or (mid is None and method.startswith('notifications/')):
        return None
    if method == 'initialize':
        return {'jsonrpc':'2.0','id':mid,'result':{
            'protocolVersion':'2025-03-26', 'capabilities':{'tools':{}},
            'serverInfo':{'name':'ai-workflow-open-kit','version':'0.2.0'},
            'instructions':'Read-only offline tools; do not use in restricted environments unless permitted.'}}
    if method == 'ping':
        return {'jsonrpc':'2.0','id':mid,'result':{}}
    if method == 'tools/list':
        return {'jsonrpc':'2.0','id':mid,'result':{'tools':TOOLS}}
    if method == 'tools/call':
        params=request.get('params') or {}
        try:
            result=tool_call(params.get('name'), params.get('arguments') or {})
            return {'jsonrpc':'2.0','id':mid,'result':{'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}]}}
        except (InputError, WorkspaceError, OSError, KeyError, ValueError, TypeError) as exc:
            # Do not echo filenames or row-level information in errors.
            message = str(exc) if isinstance(exc, (InputError, WorkspaceError)) else 'invalid tool arguments or input'
            return {'jsonrpc':'2.0','id':mid,'result':{'isError':True,
                    'content':[{'type':'text','text':message[:250]}]}}
    return {'jsonrpc':'2.0','id':mid,'error':{'code':-32601,'message':'method not found'}}


def main():
    if not ROOT.is_dir():
        print('MCP_ALLOWED_ROOT is not a directory',file=sys.stderr)
        return 2
    for data in sys.stdin.buffer:
        if len(data) > MAX_REQUEST_BYTES:
            continue
        try:
            incoming=json.loads(data)
            response=handle(incoming)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError, AttributeError):
            response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'parse error'}}
        if response is not None:
            sys.stdout.write(json.dumps(response,ensure_ascii=False,separators=(',',':'))+'\n')
            sys.stdout.flush()
    return 0


if __name__=='__main__':
    sys.exit(main())

