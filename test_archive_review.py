"""Passive report and navigation regressions. Never starts voice sessions."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import compare
import repro
import combined_build
from report import validate_report
from test_report_edges import sample


def document(target='Fixture', hardened=False, case='sample'):
    d = sample()
    d.update(target=target, hardened=hardened)
    d['results'][0]['attack'] = case
    return d


class ReviewBugs(unittest.TestCase):
    def test_prompt_mode_requires_boolean(self):
        for value in ['false', 0, [], None]:
            d = document(); d['hardened'] = value
            self.assertIsNotNone(validate_report(d))

    def test_verdict_matches_recorded_finding_types(self):
        d = json.loads(Path('evidence/report_base.json').read_text())
        for verdict in ['UNAUTHORIZED_TOOL_CALL', 'INCONCLUSIVE']:
            d['results'][0]['verdict'] = verdict
            self.assertIsNotNone(validate_report(d))

    def test_different_targets_not_compared(self):
        a, b = document(), document(target='Other fixture')
        with patch.object(compare, 'load', side_effect=[({'sample': a['results'][0]}, a), ({'sample': b['results'][0]}, b)]):
            with self.assertRaisesRegex(SystemExit, 'Target names differ'):
                compare.main('a', 'b')

    def test_disjoint_cases_not_compared(self):
        a, b = document(), document(case='other')
        with patch.object(compare, 'load', side_effect=[({'sample': a['results'][0]}, a), ({'other': b['results'][0]}, b)]):
            with self.assertRaisesRegex(SystemExit, 'No shared cases'):
                compare.main('a', 'b')

    def test_missing_sample_is_not_zero_findings(self):
        d = document(); r = d['results'][0]
        with patch.object(compare, 'load', side_effect=[({'sample':r,'extra':r},d), ({'sample':r},d)]), contextlib.redirect_stdout(io.StringIO()) as output:
            compare.main('a', 'b')
        self.assertIn('0 -> -', output.getvalue())
        self.assertIn('no sample, not zero findings', output.getvalue())

    def test_duplicate_report_cannot_be_a_repeat(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(repro.main(['base','base']), 1)
        self.assertIn('distinct', output.getvalue())

    def test_repeat_metadata_must_match(self):
        for other in [document(target='Other fixture'), document(hardened=True)]:
            with patch.object(repro, 'load', side_effect=[document(), other]), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(repro.main(['a','b']), 1)
            self.assertIn('metadata differs', output.getvalue())

    def test_missing_repeat_sample_prevents_all_runs_claim(self):
        with patch.object(repro, 'load', side_effect=[document(),document(),document(case='other')]), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(repro.main(['a','b','c']), 0)
        self.assertIn('sample missing', output.getvalue())
        self.assertNotIn('no finding in compared samples:', output.getvalue())

    def test_no_archives_has_explicit_empty_state(self):
        with patch.object(combined_build, 'PAGES', []), patch.object(Path, 'write_text') as write, patch.object(Path, 'stat') as stat, contextlib.redirect_stdout(io.StringIO()):
            stat.return_value.st_size=0
            combined_build.build()
        self.assertIn('No archived reports are available', write.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
