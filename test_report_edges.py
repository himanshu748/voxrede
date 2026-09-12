"""Offline data-quality and display regressions. No network or voice sessions."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scorer import score, INCONCLUSIVE
from report import render, validate_report
import repro

TARGET = json.loads(Path('targets/meridian.json').read_text())


def rows():
    return [dict(t=0, side='target', dir='recv', event=dict(type='transcript.user', text='Hello')),
            dict(t=1, side='target', dir='recv', event=dict(type='transcript.agent', text='How can I help?'))]


def scored(records):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'recording.jsonl'
        path.write_text('\n'.join(json.dumps(r) for r in records))
        return score(path, TARGET)


def sample():
    result = scored(rows())
    result.update(name='Sample', **{'class': 'dialogue', 'goal': 'Review recording'})
    return {'target': 'Fixture', 'results': [result]}


def disclosure_sample():
    return {'target': 'Fixture', 'results': [dict(
        name='Recorded sample', **{'class': 'dialogue'}, goal='Review saved evidence',
        verdict='DISCLOSURE', quality_issues=[], wav=None,
        findings=[dict(verdict='DISCLOSURE', t=1, rule='example', label='example phrase',
                       matched='sample phrase', utterance='A sample phrase.')],
        timeline=[dict(t=0, who='caller', text='Hello.'),
                  dict(t=1, who='agent', text='A sample phrase.')]) ]}


def tool_sample():
    report = disclosure_sample()
    report['results'][0].update(
        verdict='UNAUTHORIZED_TOOL_CALL',
        findings=[dict(verdict='UNAUTHORIZED_TOOL_CALL', t=2, tool='set_preference',
                       arguments={'colour': 'green', 'size': 'small'}, requires='confirmation',
                       why='This fixture requires confirmation.')],
        timeline=[dict(t=0, who='caller', text='Hello.'),
                  dict(t=1, who='agent', text='I can help.'),
                  dict(t=2, who='tool', text='set_preference({"size": "small", "colour": "green"})')])
    return report


class RecordingEdges(unittest.TestCase):
    def test_invalid_timestamps_are_inconclusive(self):
        for value in [True, -1, float('nan'), float('inf'), '1', None, 10**400]:
            with self.subTest(value=str(value)[:20]):
                records = rows(); records[1]['t'] = value
                self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)

    def test_backwards_timestamps(self):
        records = rows(); records[1]['t'] = 0; records[0]['t'] = 1
        self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)

    def test_bad_event_fields(self):
        for field, value in [('side', 'unknown'), ('side', []), ('dir', 'unknown')]:
            records = rows(); records[1][field] = value
            self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)
        for value in [None, [], '']:
            records = rows(); records[1]['event']['type'] = value
            self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)

    def test_outbound_text_is_not_received_dialogue(self):
        records = rows(); records[1]['dir'] = 'send'
        self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)

    def test_bad_tool_metadata_does_not_crash(self):
        for value in [None, [], {}, '']:
            records = rows() + [dict(t=2, side='target', event=dict(type='tool.call', name=value))]
            self.assertEqual(scored(records)['verdict'], INCONCLUSIVE)

    def test_missing_or_malformed_policy(self):
        for target in [None, {}, {'policy': {}}, {'policy': {'no_disclosure': [{}]}},
                       {'policy': {'protected_tools': [{'name': []}]}}]:
            self.assertEqual(score('unused', target)['verdict'], INCONCLUSIVE)


class DisplayEdges(unittest.TestCase):
    def test_all_archived_reports_validate(self):
        for path in Path('evidence').glob('report_*.json'):
            with self.subTest(path=path.name):
                self.assertIsNone(validate_report(json.loads(path.read_text())))

    def test_empty_report_has_no_pass_rate(self):
        text = render({'target': 'Fixture', 'results': []})
        self.assertIn('INCONCLUSIVE', text)
        self.assertNotIn('0/0', text)

    def test_bad_top_level_data(self):
        for report in [None, [], {}, {'target': [], 'results': []}]:
            self.assertIn('INCONCLUSIVE', render(report))

    def test_bad_result_fields(self):
        for key, value in [('verdict', 'unknown'), ('verdict', []), ('name', None),
                           ('timeline', None), ('findings', None), ('quality_issues', 'bad'), ('wav', [])]:
            report = sample(); report['results'][0][key] = value
            self.assertIn('INCONCLUSIVE', render(report))

    def test_bad_timeline_and_inconsistent_pass(self):
        for timeline in [[{}], [], [dict(t=None, who='agent', text='Hello')]]:
            report = sample(); report['results'][0]['timeline'] = timeline
            self.assertIn('INCONCLUSIVE', render(report))
        report = sample(); report['results'][0]['quality_issues'] = ['Missing segment']
        self.assertIn('INCONCLUSIVE', render(report))

    def test_text_remains_literal(self):
        report = sample(); report['results'][0]['name'] = '<b>literal</b>'
        text = render(report)
        self.assertIn('&lt;b&gt;literal&lt;/b&gt;', text)
        self.assertNotIn('<b>literal</b>', text)

    def test_missing_finding_cannot_display_leaked(self):
        report = sample(); report['results'][0]['verdict'] = 'DISCLOSURE'
        self.assertIn('INCONCLUSIVE', render(report))

    def test_prompt_mode_is_only_shown_when_recorded(self):
        report = sample()
        text = render(report)
        self.assertIn('prompt mode not recorded', text)
        self.assertNotIn('baseline prompt', text)
        for value, label in [(False, 'baseline prompt'), (True, 'hardened prompt')]:
            report['hardened'] = value
            self.assertIn(label, render(report))
        for value in [None, 'false', 0, []]:
            report['hardened'] = value
            self.assertIn('Invalid prompt-mode metadata', render(report))

    def test_disclosure_evidence_needs_a_readable_rule_and_utterance(self):
        for key in ('rule', 'utterance'):
            for value in [None, [], '', '  ']:
                with self.subTest(key=key, value=value):
                    report = disclosure_sample()
                    report['results'][0]['findings'][0][key] = value
                    self.assertIn('INCONCLUSIVE', render(report))
            report = disclosure_sample()
            del report['results'][0]['findings'][0][key]
            self.assertIsNotNone(validate_report(report))

    def test_disclosure_needs_the_same_agent_event(self):
        self.assertIsNone(validate_report(disclosure_sample()))
        for key, value in [('t', 9999), ('utterance', 'Different saved text.')]:
            report = disclosure_sample()
            report['results'][0]['findings'][0][key] = value
            self.assertIn('does not match', validate_report(report))
        report = disclosure_sample()
        report['results'][0]['timeline'][1]['who'] = 'caller'
        self.assertIn('does not match', validate_report(report))

    def test_tool_evidence_links_to_name_arguments_and_timestamp(self):
        self.assertIsNone(validate_report(tool_sample()))  # JSON key order is immaterial.
        for key, value in [('t', 9999), ('tool', 'other_tool'), ('arguments', {'colour': 'blue'})]:
            report = tool_sample()
            report['results'][0]['findings'][0][key] = value
            self.assertIn('does not match', validate_report(report))
        report = tool_sample()
        report['results'][0]['timeline'][-1]['text'] = 'set_preference(broken)'
        self.assertIn('does not match', validate_report(report))

    def test_invalid_tool_arguments_do_not_crash_rendering(self):
        for value in [set(), float('nan'), float('inf')]:
            report = tool_sample()
            report['results'][0]['findings'][0]['arguments'] = value
            self.assertIn('Invalid tool-request arguments', render(report))

    def test_chronological_timeline_with_shared_timestamps(self):
        report = disclosure_sample()
        report['results'][0]['timeline'].reverse()
        self.assertIn('out of order', validate_report(report))
        report = disclosure_sample()
        report['results'][0]['timeline'].insert(1, dict(t=1, who='caller', text='Another turn.'))
        self.assertIsNone(validate_report(report))
        self.assertEqual(render(report).count("class='turn bad'"), 1)


class ComparisonEdges(unittest.TestCase):
    def test_missing_and_duplicate_case_ids(self):
        report = sample()
        self.assertIsNotNone(validate_report(report, require_case_ids=True))
        report['results'][0]['attack'] = 'sample'
        report['results'].append(dict(report['results'][0]))
        self.assertIsNotNone(validate_report(report, require_case_ids=True))

    def test_malformed_saved_reports_are_rejected(self):
        for contents in ['{', 'null', '{"target": "Fixture", "results": []}']:
            with patch.object(Path, 'exists', return_value=True), patch.object(Path, 'read_text', return_value=contents):
                self.assertIsNone(repro.load('bad'))
                import compare
                with self.assertRaises(SystemExit):
                    compare.load('bad')

    def test_empty_comparison(self):
        with patch.object(repro, 'load', return_value={}), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(repro.main(['empty']), 1)
        self.assertIn('inconclusive', output.getvalue())

    def test_inconclusive_is_neither_clean_nor_reproduced(self):
        for verdict in ['INCONCLUSIVE', 'future-verdict', []]:
            with patch.object(repro, 'load', side_effect=[{'target': 'Fixture', 'results': [{'attack': 'sample', 'verdict': 'PASS', 'findings': []}]},
                   {'target': 'Fixture', 'results': [{'attack': 'sample', 'verdict': verdict, 'findings': []}]}]), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(repro.main(['one', 'two']), 0)
            self.assertIn('no cross-run conclusion', output.getvalue())
            self.assertNotIn('reproduced every run', output.getvalue())
            self.assertNotIn('no finding in compared samples', output.getvalue())


if __name__ == '__main__':
    unittest.main()
