"""Offline tests for tools/context_budget.py on synthetic temporary files."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from context_budget import (BudgetError, context_budget, count_lines,
                            estimate_tokens, main)

SECRET_MARKER = 'synthetic-inventory-marker-7Q'


def run_cli(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(argv)
    return code, out.getvalue()


class ContextBudgetTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / 'work'
        self.root.mkdir()
        (self.root / 'small.txt').write_text('abcd\n', encoding='utf-8')
        (self.root / 'big.md').write_text((SECRET_MARKER + '\n') * 50, encoding='utf-8')
        (self.root / 'korean.txt').write_text('재고 수량', encoding='utf-8')
        sub = self.root / 'src'
        sub.mkdir()
        (sub / 'mid.py').write_text('x = 1\n' * 10, encoding='utf-8')

    def tearDown(self):
        self._tmp.cleanup()

    def test_token_approximation(self):
        self.assertEqual(estimate_tokens(''), 0)
        self.assertEqual(estimate_tokens('abcd'), 1)
        self.assertEqual(estimate_tokens('abcde'), 2)
        self.assertEqual(estimate_tokens('재고'), 2)
        self.assertEqual(estimate_tokens('ab재고'), 3)
        self.assertEqual(count_lines(b''), 0)
        self.assertEqual(count_lines(b'a\nb'), 2)
        self.assertEqual(count_lines(b'a\nb\n'), 2)

    def test_sorted_by_tokens_and_limited(self):
        r = context_budget(root=self.root, limit=2)
        self.assertEqual(r['files_counted'], 4)
        self.assertEqual(len(r['largest']), 2)
        self.assertEqual([f['path'] for f in r['largest']], ['big.md', 'src/mid.py'])
        tokens = [f['est_tokens'] for f in context_budget(root=self.root, limit=10)['largest']]
        self.assertEqual(tokens, sorted(tokens, reverse=True))
        self.assertEqual(r['total_est_tokens'], sum(tokens))
        self.assertIn('approximation', r['note'])

    def test_specific_paths(self):
        r = context_budget(['src', 'small.txt'], root=self.root)
        self.assertEqual(sorted(f['path'] for f in r['largest']), ['small.txt', 'src/mid.py'])

    def test_budget_exceeded_exit_1(self):
        code, out = run_cli(['--root', str(self.root), '--budget', '10'])
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertTrue(data['over_budget'])
        self.assertIn('warning', data)
        code, out = run_cli(['--root', str(self.root), '--budget', '1000000'])
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(out)['over_budget'])

    def test_exclusions(self):
        git = self.root / '.git'
        git.mkdir()
        (git / 'config').write_text('ignored\n' * 100, encoding='utf-8')
        (self.root / 'image.bin').write_bytes(b'\x89PNG\x00\x00data')
        large = self.root / 'large.txt'
        with large.open('wb') as f:
            f.seek(5_000_001)
            f.write(b'a')
        r = context_budget(root=self.root, limit=50)
        paths = [f['path'] for f in r['largest']]
        self.assertFalse(any(p.startswith('.git') for p in paths))
        self.assertNotIn('image.bin', paths)
        self.assertNotIn('large.txt', paths)
        self.assertEqual(r['excluded']['skipped_dir'], 1)
        self.assertEqual(r['excluded']['binary'], 1)
        self.assertEqual(r['excluded']['too_large'], 1)
        self.assertGreaterEqual(r['excluded_count'], 3)

    def test_outside_root_exit_2(self):
        outside = Path(self._tmp.name) / 'outside.txt'
        outside.write_text('data\n', encoding='utf-8')
        code, out = run_cli(['--root', str(self.root), str(outside)])
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))
        code, out = run_cli(['--root', str(self.root), '../outside.txt'])
        self.assertEqual(code, 2)
        with self.assertRaises(BudgetError):
            context_budget(['missing.txt'], root=self.root)

    def test_invalid_arguments_exit_2(self):
        for argv in (['--root', str(self.root), '--limit', '0'],
                     ['--root', str(self.root), '--budget', '0'],
                     ['--root', str(self.root), '--limit', 'many']):
            code, out = run_cli(argv)
            self.assertEqual(code, 2)
            self.assertIn('error', json.loads(out))

    def test_output_has_no_file_content(self):
        code, out = run_cli(['--root', str(self.root), '--limit', '50'])
        self.assertEqual(code, 0)
        self.assertNotIn(SECRET_MARKER, out)
        self.assertNotIn('재고', out)
        self.assertNotIn('x = 1', out)
        self.assertNotIn(str(self.root.parent), out)


if __name__ == '__main__':
    unittest.main()
