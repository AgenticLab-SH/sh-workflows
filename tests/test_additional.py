"""Additional CLI, boundary and optional HTTP tests for the open toolkit."""
from pathlib import Path
import http.server
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from kit_utils import csv_audit, read_json, InputError, compare_json, MAX_FILE_BYTES


class MoreDataTests(unittest.TestCase):
    def test_missing_required_value_blocks_pass(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'a.csv'; f.write_text('id,name\n1,\n',encoding='utf-8')
            r=csv_audit(f,['id','name'],['id'])
            self.assertFalse(r['passed_requested_checks'])
            self.assertEqual(r['required_value_missing_count'],1)

    def test_duplicate_headers_blocks_pass(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'a.csv'; f.write_text('id,id\n1,1\n',encoding='utf-8')
            r=csv_audit(f,required_columns=['id'])
            self.assertEqual(r['duplicate_header_columns'],['id'])
            self.assertFalse(r['passed_requested_checks'])

    def test_invalid_json_error_no_content(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.json';f.write_text('{"password":"SECRET_VALUE",',encoding='utf-8')
            with self.assertRaises(InputError) as c:read_json(f)
            self.assertNotIn('SECRET_VALUE',str(c.exception))

    def test_oversized_file_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'big.csv'
            with f.open('wb') as out:out.truncate(MAX_FILE_BYTES+1)
            with self.assertRaises(InputError):csv_audit(f)

    def test_comparison_equal_no_changes(self):
        p=ROOT/'examples/config.json'
        r=compare_json(p,p)
        self.assertTrue(r['equal'])
        self.assertEqual(r['changed_paths_sample'],[])

    def test_cli_validate_json_failure_status(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools/validate_json.py'),str(ROOT/'examples/config.json'),
                          '--required','missing'],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,1)
        self.assertIn('missing_required_keys',p.stdout)

    def test_http_smoke_is_local_only(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200);self.end_headers();self.wfile.write(b'ok')
            def log_message(self,*args): pass
        server=http.server.HTTPServer(('127.0.0.1',0),Handler)
        th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
        try:
            p=subprocess.run([sys.executable,str(ROOT/'tools/smoke_http.py'),'--port',str(server.server_port)],
                             capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)['status'],200)
        finally:
            server.shutdown();server.server_close();th.join(5)

    def test_http_bad_port_is_rejected(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools/smoke_http.py'),'--port','80000'],
            capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,2)


if __name__=='__main__':unittest.main()

