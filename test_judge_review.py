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
        self.assertRegex(page, r'href="findings.html#base/01_authority/event-\d+"')
        self.assertIn('href="findings.html#hardened/01_authority"', page)
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

    def test_missing_or_invalid_utterance_has_no_comparison(self):
        path = self.root / 'report_base.json'
        original = path.read_bytes()
        for value in [None, [], '', 'Different saved text.']:
            with self.subTest(value=value):
                path.write_bytes(original)
                self.mutate('report_base.json', lambda d: d['results'][0]['findings'][0].update(utterance=value))
                self.assertIn('Guided review unavailable', self.render())
        path.write_bytes(original)
        self.mutate('report_base.json', lambda d: d['results'][0]['findings'][0].pop('utterance'))
        self.assertIn('Guided review unavailable', self.render())

    def test_orphan_finding_has_no_comparison(self):
        self.mutate('report_base.json', lambda d: d['results'][0]['findings'][0].update(t=9999))
        self.assertIn('Guided review unavailable', self.render())

    def test_baseline_permalink_follows_the_matching_agent_event(self):
        path = self.root / 'report_base.json'
        report = json.loads(path.read_text())
        row = next(r for r in report['results'] if r['attack'] == '01_authority')
        finding = next(f for f in row['findings'] if f['verdict'] == 'DISCLOSURE')
        event = next(i for i, turn in enumerate(row['timeline'])
                     if turn['who'] == 'agent' and turn['t'] == finding['t']
                     and turn['text'] == finding['utterance'])
        self.assertIn(f'href="findings.html#base/01_authority/event-{event}"', self.render())

        # Matching words from a different speaker must not become the source.
        row['timeline'].insert(event, dict(t=finding['t'], who='caller', text=finding['utterance']))
        path.write_text(json.dumps(report))
        page = self.render()
        self.assertIn(f'href="findings.html#base/01_authority/event-{event + 1}"', page)
        self.assertNotIn(f'href="findings.html#base/01_authority/event-{event}"', page)

    def test_missing_prompt_mode_has_no_comparison(self):
        self.mutate('report_hardened.json', lambda d: d.pop('hardened'))
        self.assertIn('Guided review unavailable', self.render())

    def test_diagram_timestamp_follows_selected_evidence(self):
        def change_time(doc):
            row = doc['results'][0]
            old = row['findings'][0]['t']
            row['findings'][0]['t'] = 51.888
            for turn in row['timeline']:
                if turn['t'] == old:
                    turn['t'] = 51.888
        self.mutate('report_base.json', change_time)
        page = self.render()
        self.assertIn('Disclosure at 51.888 seconds', page)
        self.assertIn('RECORDED FINDING / 51.888s', page)
        self.assertNotIn('51.887', page)

    def test_empty_final_agent_entry_does_not_replace_followup_quote(self):
        def append_blank(doc):
            row = next(r for r in doc['results'] if r['attack'] == '01_authority')
            row['timeline'].append(dict(t=row['timeline'][-1]['t'] + 1, who='agent', text='  '))
        self.mutate('report_hardened.json', append_blank)
        page = self.render()
        self.assertIn('No finding in the follow-up recording', page)
        self.assertNotIn('<blockquote>  </blockquote>', page)

    def test_followup_recording_quality_stays_visible(self):
        def incomplete(doc):
            row = next(r for r in doc['results'] if r['attack'] == '01_authority')
            row.update(verdict='INCONCLUSIVE', quality_issues=['Missing ending <segment>.'])
        self.mutate('report_hardened.json', incomplete)
        page = self.render()
        self.assertIn('Inconclusive in the follow-up recording', page)
        self.assertIn('Recording quality: Missing ending &lt;segment&gt;.', page)
        self.assertNotIn('No finding in the follow-up recording', page)


if __name__ == '__main__':
    unittest.main()
