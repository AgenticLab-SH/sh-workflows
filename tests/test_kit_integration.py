"""Offline consistency checks across Skills, docs, templates and links (synthetic repository content only)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
NEW_SKILLS = ['stakeholder-agent-questioning', 'role-separated-design',
              'optimization-modeling', 'cost-aware-execution']
LINK = re.compile(r'\]\(([^)\s]+)\)')


def md_files():
    for p in ROOT.rglob('*.md'):
        if '.git' not in p.parts:
            yield p


class KitIntegrationTest(unittest.TestCase):
    def test_skill_folders_match_front_matter_and_yaml(self):
        dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
        self.assertEqual(len(dirs), 41)
        for d in dirs:
            text = (d / 'SKILL.md').read_text(encoding='utf-8')
            m = re.match(r'---\nname: ([^\n]+)\ndescription: ([^\n]+)\n---\n', text)
            self.assertIsNotNone(m, d.name)
            self.assertEqual(m.group(1).strip(), d.name)
            yaml = (d / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
            self.assertIn('display_name:', yaml, d.name)
            self.assertIn('short_description:', yaml, d.name)

    def test_index_lists_every_skill(self):
        index = (ROOT / 'docs' / 'SKILLS_INDEX.md').read_text(encoding='utf-8')
        for d in SKILLS.iterdir():
            if d.is_dir():
                self.assertTrue(f'| {d.name} |' in index or f'[{d.name}](' in index, d.name)
        self.assertIn('41개', index)

    def test_entry_points_link_new_skills(self):
        driver = (SKILLS / 'hackathon-task-driver' / 'SKILL.md').read_text(encoding='utf-8')
        start = (ROOT / 'START_PROMPT.md').read_text(encoding='utf-8')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for name in NEW_SKILLS:
            self.assertIn(name, driver, name)
            self.assertIn(name, start, name)
            self.assertIn(name, readme, name)
        for text in (driver, start, readme):
            self.assertIn('OVERRIDE_INSTRUCTIONS.md', text)

    def test_relative_markdown_links_resolve(self):
        broken = []
        for p in md_files():
            for target in LINK.findall(p.read_text(encoding='utf-8')):
                if re.match(r'^[a-z]+:', target) or target.startswith('#'):
                    continue
                path = target.split('#', 1)[0]
                if path and not (p.parent / path).exists():
                    broken.append(f'{p.relative_to(ROOT).as_posix()} -> {target}')
        self.assertEqual(broken, [])

    def test_no_live_override_file_in_kit(self):
        live = [p for p in ROOT.rglob('AGENTS.override.md') if '.git' not in p.parts]
        self.assertEqual(live, [])
        template = ROOT / 'templates' / 'AGENTS.override.template.md'
        self.assertLess(template.stat().st_size, 4096)
        text = template.read_text(encoding='utf-8')
        self.assertIn('AGENTS.md(제공 원본)가 있으면 먼저 읽고', text)

    def test_question_ledger_template_header(self):
        first = (ROOT / 'templates' / 'QUESTION_LEDGER.csv').read_text(encoding='utf-8').splitlines()[0]
        self.assertEqual(first, 'id,category,priority,context,question,status,answer,decision,test_case,ask_count')


if __name__ == '__main__':
    unittest.main()
