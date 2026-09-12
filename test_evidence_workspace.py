"""Offline workspace regressions using copies of already-recorded reports.

These tests only read, validate, and render archives. They do not import the
scorer or start any voice sessions.
"""
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import combined_build


EVIDENCE = Path(__file__).resolve().parent / 'evidence'


def recorded_report(tag='base'):
    return json.loads((EVIDENCE / f'report_{tag}.json').read_bytes())


class Document(HTMLParser):
    """Inspect static HTML before any progressive enhancement runs."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, text):
        super().__init__()
        self.stack = []
        self.articles = []
        self.events = []
        self.scripts = []
        self.archive_json = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = (any(entry[2] for entry in self.stack) or 'hidden' in attrs
                  or attrs.get('aria-hidden') == 'true')
        if tag == 'article' and 'data-case' in attrs:
            self.articles.append((attrs['data-case'], hidden))
        if tag == 'li' and 'data-speaker' in attrs:
            self.events.append((attrs['id'], hidden))
        if tag == 'script':
            self.scripts.append(attrs)
        if tag not in self.VOID:
            self.stack.append((tag, attrs, hidden))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        if self.stack and self.stack[-1][0] == 'script':
            if self.stack[-1][1].get('id') == 'archive-data':
                self.archive_json += text


class EvidenceWorkspace(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.evidence = Path(folder.name)

    def write_report(self, tag, report=None):
        if report is None:
            report = recorded_report(tag)
        path = self.evidence / f'report_{tag}.json'
        path.write_text(json.dumps(report), encoding='utf-8')
        return path

    def paired_archive(self):
        self.write_report('base')
        self.write_report('hardened')
        return combined_build.load_archive(self.evidence)

    @staticmethod
    def first_case(archive, suite):
        return next(case for case in archive['cases'] if case['suite'] == suite)

    def test_missing_or_invalid_suite_does_not_hide_valid_neighbors(self):
        self.write_report('base')
        self.write_report('hardened')
        unavailable = self.evidence / 'report_lax.json'
        selected_pages = [page for page in combined_build.PAGES
                          if page[0] in ('base', 'lax', 'hardened')]
        for raw in (None, b'{', b'null', b'[]', b'\xff',
                    b'{"target":"Fixture","results":[]}'):
            with self.subTest(raw=raw), patch.object(combined_build, 'PAGES', selected_pages):
                unavailable.unlink(missing_ok=True)
                if raw is not None:
                    unavailable.write_bytes(raw)
                archive = combined_build.load_archive(self.evidence)
                self.assertEqual([suite['tag'] for suite in archive['suites']], ['base', 'hardened'])
                self.assertEqual(len(archive['cases']), 8)
                self.assertEqual(len(archive['problems']), 1)
                self.assertIn('No conclusion', archive['problems'][0]['message'])
                page = combined_build.render_workspace(archive)
                self.assertEqual(len(Document(page).articles), 8)

    def test_every_case_and_transcript_is_available_without_javascript(self):
        archive = self.paired_archive()
        page = combined_build.render_workspace(archive)
        document = Document(page)
        self.assertEqual({key for key, _ in document.articles},
                         {case['key'] for case in archive['cases']})
        self.assertFalse(any(hidden for _, hidden in document.articles))
        self.assertEqual(len(document.events), sum(len(case['result']['timeline'])
                                                  for case in archive['cases']))
        self.assertFalse(any(hidden for _, hidden in document.events))
        self.assertIn('JavaScript is off. All archived cases are available below.', page)

    def test_html_like_metadata_stays_literal_and_embedded_json_round_trips(self):
        report = recorded_report()
        literal = 'Literal </script> <b>note</b> & café \u2028 text'
        report['results'][0]['name'] = literal
        self.write_report('base', report)
        archive = combined_build.load_archive(self.evidence)
        page = combined_build.render_workspace(archive)
        document = Document(page)
        self.assertEqual(len(document.scripts), 2)
        self.assertEqual(sum(script.get('id') == 'archive-data' for script in document.scripts), 1)
        self.assertNotIn('<', document.archive_json)
        self.assertNotIn('>', document.archive_json)
        self.assertNotIn('&', document.archive_json)
        self.assertEqual(json.loads(document.archive_json), archive)
        self.assertEqual(json.loads(document.archive_json)['cases'][0]['result']['name'], literal)
        self.assertIn('&lt;/script&gt; &lt;b&gt;note&lt;/b&gt; &amp;', page)
        self.assertNotIn('<b>note</b>', page)

    def test_comparison_links_the_same_fixture_case_and_declared_prompt_modes(self):
        archive = self.paired_archive()
        before = self.first_case(archive, 'base')
        after = self.first_case(archive, 'hardened')
        for selected in (before, after):
            with self.subTest(suite=selected['suite']):
                text = combined_build.comparison(selected, archive)
                self.assertIn('class="comparison-grid"', text)
                self.assertIn(f'href="#{before["key"]}"', text)
                self.assertIn(f'href="#{after["key"]}"', text)
                self.assertIn('1 configured finding', text)
                self.assertIn('0 configured findings', text)
                self.assertIn('does not establish a reliable fix rate', text)

    def test_different_fixture_or_case_is_never_a_comparison_pair(self):
        original = self.paired_archive()
        for mismatch in ('target', 'attack'):
            with self.subTest(mismatch=mismatch):
                archive = copy.deepcopy(original)
                before = self.first_case(archive, 'base')
                after = self.first_case(archive, 'hardened')
                if mismatch == 'target':
                    after['target'] = 'Different recorded fixture'
                else:
                    after['result']['attack'] = 'different-case'
                text = combined_build.comparison(before, archive)
                self.assertNotIn('comparison-grid', text)
                self.assertIn('Missing evidence does not mean zero findings', text)

    def test_missing_or_inconsistent_prompt_mode_prevents_comparison(self):
        original = self.paired_archive()
        for suite, value in [('base', None), ('base', True),
                             ('hardened', None), ('hardened', False)]:
            with self.subTest(suite=suite, value=value):
                archive = copy.deepcopy(original)
                self.first_case(archive, suite)['hardened'] = value
                text = combined_build.comparison(self.first_case(archive, 'base'), archive)
                self.assertNotIn('comparison-grid', text)
                self.assertIn('No comparison is shown', text)

    def test_unrecorded_followup_is_missing_not_zero(self):
        archive = self.paired_archive()
        followup_ids = {case['result']['attack'] for case in archive['cases']
                        if case['suite'] == 'hardened'}
        unpaired = next(case for case in archive['cases']
                        if case['suite'] == 'base' and case['result']['attack'] not in followup_ids)
        text = combined_build.comparison(unpaired, archive)
        self.assertNotIn('comparison-grid', text)
        self.assertNotIn('0 configured findings', text)
        self.assertIn('Missing evidence does not mean zero findings', text)

    def test_other_recording_suites_are_not_paired_even_with_matching_ids(self):
        archive = self.paired_archive()
        before = self.first_case(archive, 'base')
        for tag in ('lax', 'noisecheck', 'demoaudio', 'base2'):
            with self.subTest(suite=tag):
                other = dict(before, suite=tag)
                text = combined_build.comparison(other, archive)
                self.assertNotIn('comparison-grid', text)
                self.assertIn('No baseline/follow-up pair is assigned', text)
                self.assertIn('Repeated recordings remain separate samples', text)

    def test_incomplete_followup_does_not_imply_zero_findings_or_improvement(self):
        archive = self.paired_archive()
        after = self.first_case(archive, 'hardened')
        after['result'].update(verdict='INCONCLUSIVE', quality_issues=['A recording segment is missing.'])
        text = combined_build.comparison(self.first_case(archive, 'base'), archive)
        self.assertIn('Recording needs review', text)
        self.assertNotIn('0 configured findings', text)
        self.assertIn('no improvement conclusion is shown', text)

    def test_embedded_export_source_hash_identifies_exact_report_bytes(self):
        report = recorded_report()
        report['target'] = 'Fixture café'
        raw = ('\r\n' + json.dumps(report, ensure_ascii=False, indent=3) + '\r\n  ').encode('utf-8')
        (self.evidence / 'report_base.json').write_bytes(raw)
        output = self.evidence / 'workspace.html'
        with contextlib.redirect_stdout(io.StringIO()):
            archive = combined_build.build(self.evidence, output)
        digest = hashlib.sha256(raw).hexdigest()
        normalized_digest = hashlib.sha256(json.dumps(report).encode('utf-8')).hexdigest()
        self.assertNotEqual(digest, normalized_digest)
        self.assertEqual(archive['suites'][0]['sha256'], digest)
        self.assertTrue(all(case['sha256'] == digest for case in archive['cases']))
        embedded = json.loads(Document(output.read_text()).archive_json)
        self.assertEqual(embedded, archive)
        self.assertEqual(embedded['cases'][0]['filename'], 'report_base.json')
        self.assertEqual(embedded['cases'][0]['sha256'], digest)


if __name__ == '__main__':
    unittest.main()
