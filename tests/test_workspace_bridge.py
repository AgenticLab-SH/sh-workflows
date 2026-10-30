"""Offline safety and integration tests for saved-workspace inspection."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from workspace_probe import WorkspaceError, file_fingerprint, workspace_inventory


class WorkspaceBridgeTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)/'project'
        self.root.mkdir()
        (self.root/'README.md').write_text('hello world', encoding='utf-8')
        (self.root/'src').mkdir()
        (self.root/'src'/'app.py').write_text('print(1)', encoding='utf-8')
        (self.root/'.git').mkdir()
        (self.root/'.git'/'config').write_text('SECRET_VALUE', encoding='utf-8')
        (self.root/'.env.local').write_text('GH_TOKEN=SECRET_VALUE', encoding='utf-8')
        (self.root/'node_modules').mkdir()
        (self.root/'node_modules'/'package.json').write_text('{}',encoding='utf-8')

    def test_inventory_lists_saved_files_only(self):
        summary = workspace_inventory(self.root, 2, 100)
        names = [x['path'] for x in summary['entries']]
        self.assertIn('README.md', names)
        self.assertIn('src/app.py', names)
        self.assertNotIn('.env.local', names)
        self.assertFalse(any(x.startswith('.git/') or 'node_modules' in x for x in names))
        self.assertNotIn('SECRET_VALUE', json.dumps(summary))

    def test_limits_and_nesting(self):
        first = workspace_inventory(self.root, 0, 100)
        self.assertIn('src', [x['path'] for x in first['entries']])
        self.assertNotIn('src/app.py', [x['path'] for x in first['entries']])
        small = workspace_inventory(self.root, 2, 1)
        self.assertEqual(small['entries_returned'], 1)
        self.assertTrue(small['truncated'])
        for depth,limit in [(-1,20),(7,20),(2,0),(2,161),(True,20),(2,False)]:
            with self.assertRaises(WorkspaceError):
                workspace_inventory(self.root,depth,limit)

    def test_hash_tracks_saved_content(self):
        before = file_fingerprint(self.root,'README.md')
        self.assertEqual(before['sha256'], hashlib.sha256(b'hello world').hexdigest())
        self.assertNotIn('hello world', json.dumps(before))
        (self.root/'README.md').write_text('new content',encoding='utf-8')
        after = file_fingerprint(self.root,'README.md')
        self.assertNotEqual(before['sha256'], after['sha256'])

    def test_traversal_symlink_and_sensitive_paths_denied(self):
        outside = Path(self.folder.name)/'private.txt'
        outside.write_text('SECRET_VALUE',encoding='utf-8')
        (self.root/'escape.txt').symlink_to(outside)
        for path in ['../private.txt',str(outside),'.env.local','.git/config','escape.txt']:
            with self.subTest(path=path),self.assertRaises(WorkspaceError):
                file_fingerprint(self.root,path)
        listing=workspace_inventory(self.root,2,100)
        self.assertNotIn('escape.txt',[x['path'] for x in listing['entries']])

    def test_large_file_denied(self):
        large = self.root/'large.bin'
        with large.open('wb') as o: o.truncate(8_000_001)
        with self.assertRaises(WorkspaceError):
            file_fingerprint(self.root, 'large.bin')

    def test_cli_exit_codes_and_no_writes(self):
        cli=ROOT/'tools'/'workspace_probe.py'
        files_before=sorted(x.relative_to(self.root).as_posix() for x in self.root.rglob('*'))
        p=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'fingerprint','README.md'],
            capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        sha=json.loads(p.stdout)['sha256']
        p2=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'fingerprint','README.md',
                             '--expect-sha256',sha],capture_output=True,text=True,timeout=10)
        self.assertEqual(p2.returncode,0,p2.stderr)
        p3=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'fingerprint','README.md',
                             '--expect-sha256','0'*64],capture_output=True,text=True,timeout=10)
        self.assertEqual(p3.returncode,1,p3.stderr)
        bad=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'fingerprint','.env.local'],
                           capture_output=True,text=True,timeout=10)
        self.assertEqual(bad.returncode,2)
        self.assertNotIn('SECRET_VALUE',bad.stdout+bad.stderr)
        files_after=sorted(x.relative_to(self.root).as_posix() for x in self.root.rglob('*'))
        self.assertEqual(files_before,files_after)

    def test_mcp_inventory_and_fingerprint(self):
        server=ROOT/'tools'/'mcp_stdio_server.py'
        requests=[{'jsonrpc':'2.0','id':1,'method':'tools/list'},
                  {'jsonrpc':'2.0','id':2,'method':'tools/call',
                   'params':{'name':'workspace_inventory','arguments':{'depth':1,'limit':30}}},
                  {'jsonrpc':'2.0','id':3,'method':'tools/call',
                   'params':{'name':'file_fingerprint','arguments':{'path':'README.md'}}},
                  {'jsonrpc':'2.0','id':4,'method':'tools/call',
                   'params':{'name':'file_fingerprint','arguments':{'path':'.env.local'}}},
                  {'jsonrpc':'2.0','id':5,'method':'tools/call',
                   'params':{'name':'workspace_inventory','arguments':{'depth':99}}}]
        p=subprocess.run([sys.executable,str(server)],input=''.join(json.dumps(x)+'\n' for x in requests),
                         capture_output=True,text=True,timeout=10,env={**os.environ,'MCP_ALLOWED_ROOT':str(self.root)})
        self.assertEqual(p.returncode,0,p.stderr)
        replies=[json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(len(replies[0]['result']['tools']),6)
        names=[x['name'] for x in replies[0]['result']['tools']]
        self.assertIn('workspace_inventory',names)
        self.assertIn('file_fingerprint',names)
        self.assertIn('README.md',replies[1]['result']['content'][0]['text'])
        self.assertIn('sha256',replies[2]['result']['content'][0]['text'])
        self.assertTrue(replies[3]['result']['isError'])
        self.assertTrue(replies[4]['result']['isError'])
        self.assertNotIn('SECRET_VALUE',p.stdout)


if __name__=='__main__':
    unittest.main()

