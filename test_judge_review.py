"""Regression checks for the passive judge walkthrough; no API calls."""
import json
import tempfile
import unittest
from pathlib import Path

from judge_review import render_review


class JudgeReviewTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        for name in ('report_base.json', 'report_hardened.json'):
            (self.root / name).write_bytes((Path('evidence') / name).read_bytes())
        self.target = self.root / 'target.json'
        self.target.write_bytes(Path('targets/meridian.json').read_bytes())

    def render(self):
        return render_review(self.root, self.target)

    def mutate(self, name, change):
        path = self.root / name
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_archived_walkthrough_has_evidence_and_followup(self):
        page = self.render()
        self.assertIn('Disclosure at 51.887 seconds', page)
        self.assertIn('No finding in the follow-up recording', page)
        self.assertIn('findings.html#base', page)
        self.assertIn('findings.html#hardened', page)
        self.assertEqual(page.count('<article '), 4)
        self.assertNotIn('<article hidden', page)  # content survives disabled JS

    def test_missing_or_malformed_evidence_has_no_comparison(self):
        path = self.root / 'report_hardened.json'
        for contents in ('{', 'null'):
            path.write_text(contents)
            self.assertIn('Guided review unavailable', self.render())
        path.unlink()
        self.assertNotIn('No finding in the follow-up recording', self.render())

    def test_mismatched_target_has_no_comparison(self):
        self.mutate('report_hardened.json', lambda d: d.update(target='another-fixture'))
        self.assertIn('Guided review unavailable', self.render())

    def test_wrong_prompt_mode_has_no_comparison(self):
        self.mutate('report_hardened.json', lambda d: d.update(hardened=False))
        self.assertIn('Guided review unavailable', self.render())

    def test_absent_policy_rule_has_no_finding_story(self):
        self.mutate('target.json', lambda d: d['policy'].update(no_disclosure=[]))
        self.assertIn('Guided review unavailable', self.render())

    def test_missing_selected_case_has_no_comparison(self):
        self.mutate('report_hardened.json', lambda d: d.update(results=[r for r in d['results'] if r['attack'] != '01_authority']))
        self.assertIn('Guided review unavailable', self.render())

    def test_duplicate_cases_have_no_comparison(self):
        self.mutate('report_hardened.json', lambda d: d['results'].append(d['results'][0]))
        self.assertIn('Guided review unavailable', self.render())


if __name__ == '__main__':
    unittest.main()
