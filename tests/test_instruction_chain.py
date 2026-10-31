"""Offline tests for tools/instruction_chain.py on synthetic temp folders."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools' / 'instruction_chain.py'
sys.path.insert(0, str(ROOT / 'tools'))
from instruction_chain import inspect_chain  # noqa: E402
from kit_utils import InputError  # noqa: E402

SECRET = 'SYNTHETIC-MARKER-greenhouse-sensor-7731'


def run_cli(*args):
    p = subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True,
                       timeout=20, encoding='utf-8')
    return p.returncode, p.stdout


class InstructionChainTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / 'project'
        self.root.mkdir()
        (self.root / '.git').mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def test_root_only_agents(self):
        self.write('AGENTS.md', 'greenhouse rules\n')
        r = inspect_chain(self.root)
        self.assertEqual(r['load_order'], ['AGENTS.md'])
        self.assertEqual(r['folders'][0]['selected']['status'], 'included')
        self.assertEqual(r['warnings'], [])

    def test_override_shadows_original_in_same_folder(self):
        self.write('AGENTS.md', 'provided original\n')
        self.write('AGENTS.override.md', 'participant override\n')
        r = inspect_chain(self.root)
        f = r['folders'][0]
        self.assertEqual(f['selected']['file'], 'AGENTS.override.md')
        self.assertEqual([s['file'] for s in f['shadowed']], ['AGENTS.md'])
        self.assertTrue(any('hides AGENTS.md' in w for w in r['warnings']))
        self.assertIs(f['original_embedded'], False)

    def test_nested_order_root_to_cwd(self):
        self.write('AGENTS.md', 'root\n')
        self.write('work/AGENTS.override.md', 'work\n')
        self.write('work/inner/AGENTS.md', 'inner\n')
        self.write('other/AGENTS.md', 'unrelated\n')
        r = inspect_chain(self.root, self.root / 'work' / 'inner')
        self.assertEqual(r['load_order'],
                         ['AGENTS.md', 'work/AGENTS.override.md', 'work/inner/AGENTS.md'])
        self.assertEqual([f['dir'] for f in r['folders']], ['.', 'work', 'work/inner'])
        self.assertEqual(r['cwd'], 'work/inner')

    def test_empty_override_is_skipped(self):
        self.write('AGENTS.override.md', '  \n\t\n')
        self.write('AGENTS.md', 'real\n')
        r = inspect_chain(self.root)
        f = r['folders'][0]
        self.assertEqual(f['selected']['file'], 'AGENTS.md')
        self.assertEqual([s['file'] for s in f['skipped_empty']], ['AGENTS.override.md'])
        self.assertEqual(f['shadowed'], [])

    def test_empty_override_warns_behavior_unconfirmed(self):
        self.write('AGENTS.override.md', '\n')
        self.write('AGENTS.md', 'real\n')
        r = inspect_chain(self.root)
        self.assertEqual(r['load_order'], ['AGENTS.md'])
        empty = [w for w in r['warnings'] if 'behavior unconfirmed' in w]
        self.assertEqual(len(empty), 1)
        self.assertIn('AGENTS.override.md is empty', empty[0])
        self.assertTrue(any('behavior unconfirmed' in n for n in r['notes']))

    def test_original_embedded_true(self):
        original = '# provided rules\n- keep files\n- ask first\n'
        self.write('AGENTS.md', original)
        self.write('AGENTS.override.md', original + '\n--- 아래는 참가자 작업 방식 ---\n# mine\n- short\n')
        r = inspect_chain(self.root)
        f = r['folders'][0]
        self.assertTrue(f['original_embedded'])
        self.assertEqual(f['shadowed'][0]['embedded_in_selected'], True)
        self.assertFalse(any('hides' in w for w in r['warnings']))
        self.assertTrue(any('embeds original AGENTS.md' in n for n in r['notes']))
        self.assertEqual(r['warnings'], [])

    def test_original_embedded_false_when_changed(self):
        self.write('AGENTS.md', '# provided rules\n- keep files\n- ask first\n')
        self.write('AGENTS.override.md', '# provided rules\n- keep file\n- ask first\n\n# mine\n')
        r = inspect_chain(self.root)
        self.assertIs(r['folders'][0]['original_embedded'], False)
        hides = [w for w in r['warnings'] if 'hides AGENTS.md' in w]
        self.assertEqual(len(hides), 1)
        self.assertIn('paste the original verbatim at the top or use path B', hides[0])
        self.assertFalse(any('embeds original' in n for n in r['notes']))

    def test_original_embedded_normalizes_crlf_and_trailing_space(self):
        (self.root / 'AGENTS.md').write_bytes(b'\xef\xbb\xbf\r\n# rules  \r\n- one\t\r\n- two\r\n\r\n\r\n')
        (self.root / 'AGENTS.override.md').write_bytes(b'# rules\n- one\n- two\n\n--- mine ---\n- three\n')
        r = inspect_chain(self.root)
        self.assertTrue(r['folders'][0]['original_embedded'])
        (self.root / 'AGENTS.md').write_bytes(b'# rules\n- one\n- two\n')
        (self.root / 'AGENTS.override.md').write_bytes(b'# rules\r\n- one\r\n- two\r\n--- mine ---\r\n')
        r = inspect_chain(self.root)
        self.assertTrue(r['folders'][0]['original_embedded'])

    def test_original_embedded_false_when_pasted_at_bottom(self):
        original = '# provided rules\n- keep files\n- ask first\n'
        self.write('AGENTS.md', original)
        self.write('AGENTS.override.md', '# mine\n- short\n\n' + original)
        r = inspect_chain(self.root)
        self.assertIs(r['folders'][0]['original_embedded'], False)
        self.assertTrue(any('paste the original verbatim at the top' in w for w in r['warnings']))

    def test_original_embedded_true_below_template_guide_and_comment(self):
        original = '    indented first line\n- keep files\n'
        self.write('AGENTS.md', original)
        guide = '[원본 AGENTS.md가 있으면 이 줄 아래에 원본 전문을 그대로 붙인다]'
        self.write('AGENTS.override.md', '<!-- template note\nsecond comment line -->\n' + guide + '\n'
                   + original + '\n--- 아래는 참가자 작업 방식 ---\n# mine\n')
        r = inspect_chain(self.root)
        self.assertIs(r['folders'][0]['original_embedded'], True)
        self.assertEqual(r['warnings'], [])
        # guide line without comment, CRLF override
        (self.root / 'AGENTS.override.md').write_bytes(
            (guide + '\r\n' + original.replace('\n', '\r\n') + '# mine\r\n').encode('utf-8'))
        self.assertIs(inspect_chain(self.root)['folders'][0]['original_embedded'], True)

    def test_original_embedded_false_on_partial_indentation_or_line_match(self):
        self.write('AGENTS.md', '    code\n- x\n')
        self.write('AGENTS.override.md', 'xx    code\n- x\n')
        self.assertIs(inspect_chain(self.root)['folders'][0]['original_embedded'], False)
        self.write('AGENTS.override.md', 'code\n- x\n')  # indentation lost
        self.assertIs(inspect_chain(self.root)['folders'][0]['original_embedded'], False)
        self.write('AGENTS.md', '# rules\n- ask\n')
        self.write('AGENTS.override.md', '# rules\n- ask first\n')  # last line only partly equal
        self.assertIs(inspect_chain(self.root)['folders'][0]['original_embedded'], False)

    def test_original_embedded_with_leading_comment_in_original(self):
        original = '<!-- provided header -->\n# rules\n- one\n'
        self.write('AGENTS.md', original)
        self.write('AGENTS.override.md', original + '\n# mine\n')
        self.assertIs(inspect_chain(self.root)['folders'][0]['original_embedded'], True)

    def test_empty_original_is_null_with_note(self):
        self.write('AGENTS.md', ' \n\n')
        self.write('AGENTS.override.md', '# mine\n- short\n')
        r = inspect_chain(self.root)
        f = r['folders'][0]
        self.assertIsNone(f['original_embedded'])
        self.assertTrue(f['shadowed'][0]['original_empty'])
        self.assertFalse(any('paste the original' in w for w in r['warnings']))
        self.assertFalse(any('hides AGENTS.md' in w for w in r['warnings']))
        self.assertTrue(any('original AGENTS.md is empty' in n for n in r['notes']))

    def test_original_embedded_not_reported_without_override(self):
        self.write('AGENTS.md', 'x\n')
        r = inspect_chain(self.root)
        self.assertIsNone(r['folders'][0]['original_embedded'])

    def test_limit_reached(self):
        self.write('AGENTS.md', 'a' * 60 + '\n')
        self.write('sub/AGENTS.md', 'b' * 60 + '\n')
        self.write('sub/deep/AGENTS.md', 'c' * 10 + '\n')
        r = inspect_chain(self.root, self.root / 'sub' / 'deep', max_bytes=100)
        st = [f['selected']['status'] for f in r['folders']]
        self.assertEqual(st, ['included', 'partial', 'not_included_limit'])
        self.assertEqual(r['included_total_bytes'], 100)
        self.assertTrue(r['limit_reached'])
        self.assertNotIn('sub/deep/AGENTS.md', r['load_order'])
        self.assertTrue(any('over the 100-byte limit' in w for w in r['warnings']))

    def test_fallback_name_used_when_no_agents(self):
        self.write('TEAM_GUIDE.md', 'guide\n')
        r = inspect_chain(self.root, fallback='TEAM_GUIDE.md, ')
        self.assertEqual(r['load_order'], ['TEAM_GUIDE.md'])
        self.assertEqual(r['candidate_names'][-1], 'TEAM_GUIDE.md')

    def test_fallback_shadowed_by_agents(self):
        self.write('AGENTS.md', 'x\n')
        self.write('TEAM_GUIDE.md', 'y\n')
        r = inspect_chain(self.root, fallback='TEAM_GUIDE.md')
        self.assertEqual([s['file'] for s in r['folders'][0]['shadowed']], ['TEAM_GUIDE.md'])
        self.assertIsNone(r['folders'][0]['original_embedded'])
        hides = [w for w in r['warnings'] if 'hides TEAM_GUIDE.md' in w]
        self.assertEqual(len(hides), 1)
        self.assertNotIn('path B', hides[0])

    def test_fallback_with_path_rejected(self):
        with self.assertRaises(InputError):
            inspect_chain(self.root, fallback='../x.md')

    def test_cwd_outside_root_exit_2(self):
        outside = Path(self._tmp.name) / 'outside'
        outside.mkdir()
        code, out = run_cli('--root', str(self.root), '--cwd', str(outside))
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))

    def test_missing_root_exit_2(self):
        code, out = run_cli('--root', str(self.root / 'nope'))
        self.assertEqual(code, 2)
        self.assertIn('error', json.loads(out))

    def test_cli_never_prints_contents_or_absolute_paths(self):
        self.write('AGENTS.md', SECRET + '\n')
        self.write('AGENTS.override.md', SECRET + '\n\n--- override ---\n')
        code, out = run_cli('--root', str(self.root))
        self.assertEqual(code, 0)
        self.assertNotIn(SECRET, out)
        self.assertNotIn(self._tmp.name, out)
        data = json.loads(out)
        self.assertEqual(data['load_order'], ['AGENTS.override.md'])
        self.assertIs(data['folders'][0]['original_embedded'], True)

    def test_no_git_marker_warns(self):
        (self.root / '.git').rmdir()
        self.write('AGENTS.md', 'x\n')
        r = inspect_chain(self.root)
        self.assertTrue(any('.git' in w for w in r['warnings']))

    def test_no_files_gives_empty_chain(self):
        r = inspect_chain(self.root)
        self.assertEqual(r['load_order'], [])
        self.assertFalse(r['limit_reached'])


if __name__ == '__main__':
    unittest.main()
