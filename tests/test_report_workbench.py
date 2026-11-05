"""Synthetic-only tests. No personal files, Cofa environment or external network."""
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import report_workbench as r


class ReportWorkbenchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def note(self, **kw):
        payload = dict(agent='planner', kind='decision', status='confirmed',
                       title='Synthetic workflow scope', why='Simple workflow selected',
                       alternatives='Extra service rejected', evidence='Example only')
        payload.update(kw)
        return r.record(self.root, **payload)

    def test_does_not_write_until_record(self):
        self.assertEqual(r.read_events(self.root), [])
        self.assertFalse((self.root / '.review-workbench').exists())

    def test_cumulative_events_and_independent_files(self):
        one = self.note()
        two = self.note(agent='worker2', kind='test', status='verified', title='Synthetic test')
        self.assertNotEqual(one['id'], two['id'])
        entries = r.read_events(self.root)
        self.assertEqual(len(entries), 2)
        self.assertEqual({x['agent'] for x in entries}, {'planner', 'worker2'})
        self.assertEqual(len(list((self.root / r.EVENT_DIR).glob('*.json'))), 2)

    def test_workers_do_not_overwrite(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            items = list(pool.map(lambda i: self.note(agent=f'w{i}', title=f'Event {i}'), range(24)))
        self.assertEqual(len(set(x['id'] for x in items)), 24)
        self.assertEqual(len(r.read_events(self.root)), 24)

    def test_bad_identifiers_and_status(self):
        for kw in [{'agent': '../leak'}, {'agent': 'UPPER'}, {'kind': 'archive'},
                   {'status': 'fake'}, {'title': ''}, {'summary': 'password=secret'}]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.note(**kw)
        self.assertFalse((self.root / r.EVENT_DIR).exists())

    def test_symlink_directory_is_blocked(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / '.review-workbench').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.note()
        with self.assertRaises(ValueError):
            r.read_events(self.root)

    def test_long_text_is_rejected(self):
        with self.assertRaises(ValueError):
            self.note(summary='x' * 1600)

    def test_malformed_events_are_not_exposed(self):
        self.note()
        d = self.root / r.EVENT_DIR
        (d / 'not-json.json').write_text('not json', encoding='utf-8')
        (d / 'secret.json').write_text(json.dumps({'schema':1,'kind':'result','status':'verified','agent':'worker', 'title':'password=bad'}), encoding='utf-8')
        self.assertEqual(len(r.read_events(self.root)), 1)

    def test_preview_url_restrictions(self):
        self.assertEqual(r.validate_preview(''), '')
        self.assertEqual(r.validate_preview('http://localhost:3000'), 'http://localhost:3000')
        for uri in ['https://example.com', 'http://example.com:3000',
                    'http://localhost:3000/private', 'file:///etc/passwd',
                    'http://localhost:3000/?secret=x', 'http://user@localhost:3000']:
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                r.validate_preview(uri)

    def test_html_uses_text_content_and_two_tabs(self):
        page = r.HTML
        self.assertIn('tab-report', page)
        self.assertIn('tab-output', page)
        self.assertIn('textContent=e.title', page)
        self.assertNotIn('innerHTML', page)
        self.assertNotIn('https://', page)

    def test_local_server_is_read_only(self):
        r.record(self.root, agent='test', kind='result', status='verified',title='Synthetic passed')
        server = r.ThreadingHTTPServer(('127.0.0.1', 0), r.handler_factory(self.root, ''))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = HTTPConnection('127.0.0.1', server.server_port, timeout=2)
            conn.request('GET', '/api/events')
            resp = conn.getresponse()
            self.assertEqual(resp.status, 200)
            self.assertEqual(len(json.loads(resp.read())['events']), 1)
            conn.request('GET', '/nope')
            self.assertEqual(conn.getresponse().status, 404)
            conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)


if __name__ == '__main__':
    unittest.main()

class PublicThemeTest(unittest.TestCase):
    def test_public_tokens_are_fixed_not_logo(self):
        self.assertIn('#EA002C', r.PUBLIC_SK_CI_CSS)
        self.assertNotIn('url(', r.PUBLIC_SK_CI_CSS)
