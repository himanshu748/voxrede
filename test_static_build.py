"""Offline static packaging regressions using small synthetic saved reports."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import static_build


class StaticBuildTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.source = Path(self.folder.name) / 'source'
        self.out = Path(self.folder.name) / 'site'
        (self.source / 'evidence').mkdir(parents=True)
        (self.source / 'assets').mkdir()
        (self.source / 'assets' / 'archive.js').write_text('// archived review controls')
        (self.source / 'assets' / 'archive.css').write_text('.archive { color: plum; }')
        (self.source / 'design.css').write_text(':root { color: plum; }')
        (self.source / 'landing.html').write_text('<h1>Overview source</h1>')
        (self.source / 'findings.html').write_text(
            '<a href="./">Overview</a><a href="./#review">Guided review</a>'
            '<a href="./assets/example.json">Source</a><h1>Findings</h1>')
        (self.source / 'deck.html').write_text('<h1>Deck</h1>')

    def report(self, filename):
        doc = {'target': 'Example fixture', 'hardened': False, 'results': [{
            'name': 'Saved conversation', 'class': 'dialogue', 'goal': 'Review recorded text',
            'verdict': 'PASS', 'findings': [], 'quality_issues': [], 'wav': 'example.wav',
            'timeline': [{'t': 0, 'who': 'caller', 'text': 'Hello.'},
                         {'t': 1, 'who': 'agent', 'text': 'Hello, how can I help?'}],
        }]}
        (self.source / 'evidence' / filename).write_text(json.dumps(doc))

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return static_build.build(self.source, self.out)

    def test_missing_reports_remove_old_pages_and_navigation(self):
        self.report('report_base.json')
        self.report('report_lax.json')
        self.assertEqual(self.build(), self.out)
        self.assertTrue((self.out / 'lax.html').is_file())
        self.assertIn('href="lax.html"', (self.out / 'index.html').read_text())
        self.assertNotIn('href="hardened.html"', (self.out / 'index.html').read_text())
        (self.out / 'keep.txt').write_text('Unrelated output')

        (self.source / 'evidence' / 'report_lax.json').unlink()
        self.build()
        self.assertFalse((self.out / 'lax.html').exists())
        self.assertNotIn('href="lax.html"', (self.out / 'index.html').read_text())
        self.assertEqual((self.out / 'keep.txt').read_text(), 'Unrelated output')

        (self.source / 'evidence' / 'report_base.json').unlink()
        self.build()
        self.assertFalse((self.out / 'index.html').exists())
        self.assertTrue((self.out / 'overview.html').is_file())

    def test_missing_watch_still_copies_styles_assets_and_local_layout(self):
        self.report('report_base.json')
        self.build()
        self.assertEqual((self.out / 'design.css').read_text(), ':root { color: plum; }')
        for name in ('archive.js', 'archive.css'):
            self.assertEqual((self.out / 'assets' / name).read_bytes(),
                             (self.source / 'assets' / name).read_bytes())
        self.assertIn('Baseline report', (self.out / 'index.html').read_text())
        self.assertNotIn('<audio ', (self.out / 'index.html').read_text())
        self.assertEqual((self.out / 'overview.html').read_text(), '<h1>Overview source</h1>')
        self.assertIn('href="overview.html"', (self.out / 'findings.html').read_text())
        self.assertIn('href="overview.html#review"', (self.out / 'findings.html').read_text())
        self.assertNotIn('href="./#review"', (self.out / 'findings.html').read_text())
        self.assertIn('href="./assets/example.json"', (self.out / 'findings.html').read_text())
        self.assertFalse((self.out / 'watch.html').exists())

    def test_removed_watch_is_not_left_in_successive_builds(self):
        (self.source / 'watch.html').write_text('<a href="./">Overview</a>')
        self.build()
        self.assertIn('href="overview.html"', (self.out / 'watch.html').read_text())
        (self.source / 'watch.html').unlink()
        (self.source / 'design.css').write_text(':root { color: olive; }')
        self.build()
        self.assertFalse((self.out / 'watch.html').exists())
        self.assertEqual((self.out / 'design.css').read_text(), ':root { color: olive; }')

    def test_import_does_not_build(self):
        module_dir = str(Path(static_build.__file__).resolve().parent)
        code = f'import sys; sys.path.insert(0, {module_dir!r}); import static_build'
        result = subprocess.run([sys.executable, '-c', code], cwd=self.source,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertFalse((self.source / 'static').exists())


if __name__ == '__main__':
    unittest.main()
