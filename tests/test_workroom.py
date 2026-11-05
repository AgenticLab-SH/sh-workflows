"""Offline synthetic tests: no user machine paths, no assessment data or network."""
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import workroom as w


class WorkroomTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'exercise'  # synthetic root
        self.root.mkdir()
        (self.root/'README.md').write_text('Synthetic demo',encoding='utf-8')
        self.control=self.root/w.CONTROL
        self.control.mkdir()
        (self.control/'ROOT_PATH.txt').write_text(str(self.root)+'\n',encoding='utf-8')
        (self.control/'INITIAL_STATE.md').write_text('# original files before clone\n',encoding='utf-8')
        (self.control/'FILES_AT_START.tsv').write_text('README.md\t14\n',encoding='utf-8')
        (self.control/'kit'/'tools').mkdir(parents=True)
        (self.control/'kit'/'tools'/'workroom.py').write_text('# synthetic kit marker',encoding='utf-8')

    def test_preclone_guard(self):
        (self.control/'INITIAL_STATE.md').unlink()
        with self.assertRaisesRegex(ValueError,'Baseline'):
            w.init(self.root)
        self.assertFalse((self.control/'docs').exists())

    def test_explicit_root_mismatch(self):
        (self.control/'ROOT_PATH.txt').write_text('/tmp/another-root\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'differs'):
            w.init(self.root)

    def test_no_home_or_top_root(self):
        with self.assertRaises(ValueError):
            w.confirmed_root('/')
        with self.assertRaises(ValueError):
            w.confirmed_root(str(Path.home()))

    def test_init_preserves_files_and_existing_documents(self):
        (self.control/'docs').mkdir()
        (self.control/'docs'/'DECISIONS.md').write_text('my-existing-decision',encoding='utf-8')
        original=(self.root/'README.md').read_text()
        x=w.init(self.root)
        self.assertEqual(x['preserved_existing'],1)
        self.assertEqual((self.control/'docs'/'DECISIONS.md').read_text(),'my-existing-decision')
        self.assertEqual((self.root/'README.md').read_text(),original)
        self.assertEqual(w.snapshot_count(self.control),1)

    def test_does_not_scan_parent(self):
        (self.root.parent/'SECRET.txt').write_text('OUTSIDE-DATA',encoding='utf-8')
        w.init(self.root)
        x=w.summary(self.root)
        self.assertNotIn('SECRET',json.dumps(x))

    def test_symlink_in_control_refused(self):
        outside=self.root.parent/'external';outside.mkdir()
        (self.control/'events').symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Unsafe'):
            w.init(self.root)

    def test_parallel_event_records_own_files(self):
        w.init(self.root)
        def create(i):
            return w.note(self.root,f'worker{i%8}', 'decision','confirmed',{'title':f'Option {i}', 'reason':'Compared a simple alternative'})
        with ThreadPoolExecutor(max_workers=8) as pool:
            values=list(pool.map(create,range(70)))
        self.assertEqual(len(set(x['id'] for x in values)),70)
        self.assertEqual(len(w.list_events(self.control)),70)
        self.assertEqual(len(list((self.control/'events').glob('*.json'))),70)

    def test_rejects_tokens_email_and_long_text(self):
        w.init(self.root)
        for name in ('password=123','test@private.com','ghp_abc1234567890123456'):
            with self.subTest(name=name),self.assertRaises(ValueError):
                w.note(self.root,'worker','test' if False else 'verification','pass',{'title':name})
        with self.assertRaises(ValueError):
            w.note(self.root,'worker','decision','proposed',{'title':'ok','summary':'x'*1800})
        self.assertEqual(w.list_events(self.control),[])

    def test_events_read_only_and_summary(self):
        w.init(self.root)
        w.note(self.root,'worker','verification','pass',{'title':'Synthetic check','evidence':'Synthetic PASS'})
        x=w.summary(self.root)
        self.assertTrue(x['root_confirmed'])
        self.assertEqual(x['total_events'],1)
        self.assertFalse(x['external_upload'])
        self.assertEqual(x['service_port'],3001)
        self.assertEqual(x['report_port'],3000)

    def test_event_html_xss_not_interpreted(self):
        html=Path(w.__file__).with_name('workroom_ui.html').read_text(encoding='utf-8')
        self.assertIn('textContent',html)
        self.assertNotIn('innerHTML=',html)
        self.assertIn('data-view="verify"',html)
        self.assertIn('data-view="initial"',html)
        self.assertIn('http://localhost:3001/',html)

    def test_all_views_can_be_shown_by_js(self):
        html=Path(w.__file__).with_name('workroom_ui.html').read_text(encoding='utf-8')
        self.assertIn("button.dataset.view", html)
        self.assertIn(".hidden=name!==view", html)
        self.assertIn('.view[hidden]{display:none!important}', html)
        self.assertNotIn('#view-verify,#view-initial{display:none}',html)

    def test_read_only_http_endpoints(self):
        w.init(self.root)
        # Run function server in a thread using a patched port; no external binding
        import http.server
        original = w.ThreadingHTTPServer
        holder = {}
        class FakeServer(original):
            def __init__(self,address,Handler):
                super().__init__(('127.0.0.1',0),Handler)
                holder['port']=self.server_port
                holder['server']=self
        w.ThreadingHTTPServer=FakeServer
        thr=Thread(target=w.serve,args=(self.root,3000,'127.0.0.1'),daemon=True)
        thr.start()
        import time
        for _ in range(100):
            if 'server' in holder:break
            time.sleep(.01)
        try:
            self.assertIn('port',holder)
            conn=HTTPConnection('127.0.0.1',holder['port'],timeout=3)
            conn.request('GET','/api/state')
            response=conn.getresponse();self.assertEqual(response.status,200)
            self.assertFalse(json.loads(response.read())['external_upload'])
            conn.request('GET','/')
            response=conn.getresponse();self.assertEqual(response.status,200)
            self.assertIn(b'WORKROOM',response.read())
            conn.request('POST','/api/state')
            response=conn.getresponse();self.assertEqual(response.status,405)
            response.read()
            conn.request('GET','/README.md')
            response=conn.getresponse();self.assertEqual(response.status,404)
            response.read();conn.close()
        finally:
            holder['server'].shutdown()
            holder['server'].server_close()
            thr.join(timeout=3)
            w.ThreadingHTTPServer=original


if __name__=='__main__':
    unittest.main()
