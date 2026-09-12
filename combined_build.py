"""Build a passive, searchable workspace from recorded evidence. No API calls."""
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import quote

from report import finding_matches_turn, validate_report

PAGES = [
    ('base', 'Baseline', 'report_base.json', 'The original fixture, with caller verification required.'),
    ('lax', 'No verification step', 'report_lax.json', 'A separate fixture with the ownership check omitted. Business tools were mocked.'),
    ('hardened', 'Stricter prompt', 'report_hardened.json', 'Recorded follow-ups for two baseline cases. These samples do not establish a fix rate.'),
    ('noisecheck', 'Audio condition', 'report_noisecheck.json', 'One archived audio-condition sample. No coverage claim.'),
    ('demoaudio', 'Repeat sample', 'report_demoaudio.json', 'Later recordings of two scenarios. Outcomes vary between calls.'),
    ('base2', 'Second baseline', 'report_base2.json', 'A second baseline recording with four scenarios. Missing cases are not zero findings.'),
]
E = html.escape


def case_key(tag, case):
    return tag + '/' + quote(case, safe='')


def case_id(key):
    return key


def status(row):
    return {'PASS': 'No finding', 'DISCLOSURE': 'Disclosure',
            'UNAUTHORIZED_TOOL_CALL': 'Tool requested', 'INCONCLUSIVE': 'Inconclusive'}[row['verdict']]


def prompt_mode(value):
    return 'Stricter prompt' if value is True else 'Baseline prompt' if value is False else 'Prompt mode not recorded'


def load_archive(evidence):
    suites, cases, problems = [], [], []
    for tag, label, filename, description in PAGES:
        path = evidence / filename
        try:
            raw = path.read_bytes()
            report = json.loads(raw)
            problem = validate_report(report, require_case_ids=True)
            if problem:
                raise ValueError(problem)
        except (OSError, ValueError, TypeError) as exc:
            problems.append({'suite': label, 'message': 'Recording unavailable or invalid. No conclusion is shown.'})
            continue
        suite = dict(tag=tag, label=label, description=description, target=report['target'],
                     hardened=report.get('hardened'), sha256=hashlib.sha256(raw).hexdigest(), filename=filename)
        suites.append(suite)
        for row in report['results']:
            key = case_key(tag, row['attack'])
            cases.append(dict(key=key, dom_id=case_id(key), suite=tag, suite_label=label,
                              target=report['target'], hardened=report.get('hardened'),
                              sha256=suite['sha256'], filename=filename, **{'result': row}))
    return dict(suites=suites, cases=cases, problems=problems)


def comparison(case, archive):
    """Only pair the declared baseline/follow-up, same fixture and case ID."""
    if case['suite'] not in ('base', 'hardened'):
        return '<p class="comparison-unavailable">No baseline/follow-up pair is assigned to this recording. Repeated recordings remain separate samples.</p>'
    other_suite = 'hardened' if case['suite'] == 'base' else 'base'
    other = next((c for c in archive['cases'] if c['suite'] == other_suite and
                  c['result']['attack'] == case['result']['attack'] and c['target'] == case['target']), None)
    if other is None:
        return '<p class="comparison-unavailable">No matching follow-up pair was recorded for this case. Missing evidence does not mean zero findings.</p>'
    before, after = (case, other) if case['suite'] == 'base' else (other, case)
    if before['hardened'] is not False or after['hardened'] is not True:
        return '<p class="comparison-unavailable">Prompt metadata does not identify a baseline and stricter-prompt pair. No comparison is shown.</p>'
    blocks = []
    for item, label in ((before, 'Baseline'), (after, 'Stricter prompt')):
        row = item['result']
        issue = row.get('quality_issues') or row['verdict'] == 'INCONCLUSIVE'
        result = 'Recording needs review' if issue else f"{len(row['findings'])} configured finding{'s' if len(row['findings']) != 1 else ''}"
        blocks.append(f'<div><h4>{label}</h4><p class="comparison-result">{E(result)}</p>'
                      f'<span class="verdict v-{row["verdict"]}">{E(status(row))}</span>'
                      f'<a class="text-link" href="#{E(item["key"])}">Open {label.lower()} recording</a></div>')
    caveat = ('Recording quality needs review; no improvement conclusion is shown.' if any(
        x['result'].get('quality_issues') or x['result']['verdict'] == 'INCONCLUSIVE' for x in (before, after))
        else 'One baseline and one follow-up sample. This comparison does not establish a reliable fix rate.')
    return '<div class="comparison-grid">' + ''.join(blocks) + '</div><p class="fine">' + caveat + '</p>'


def render_case(case, archive):
    r, key, ident = case['result'], case['key'], case['dom_id']
    findings, event_rows, event_ids = [], [], set()
    for i, finding in enumerate(r['findings']):
        who = 'agent' if finding['verdict'] == 'DISCLOSURE' else 'tool'
        event = next(j for j, t in enumerate(r['timeline']) if finding_matches_turn(finding, t))
        event_ids.add(event)
        title = finding['label'] if who == 'agent' else finding['tool']
        detail = (f'<blockquote>{E(finding["utterance"])}</blockquote>' if who == 'agent' else
                  f'<pre>{E(json.dumps(finding["arguments"], indent=2))}</pre><p>{E(finding["why"])}</p>')
        boundary = ('Configured rule: ' + finding['rule'] if who == 'agent' else 'Tool execution was mocked. No money moved.')
        findings.append(f'<section class="finding" id="{E(ident)}-finding-{i}"><div class="finding-top">'
                        f'<h3>{E(title)}</h3><a class="event-jump" href="#{E(key)}/event-{event}">{finding["t"]:.3f}s <span>View event</span></a></div>'
                        f'{detail}<p class="fine">{E(boundary)}</p></section>')
    if not findings:
        note = ('The recording is incomplete or has a detected error. It cannot support a no-finding conclusion.' if r['verdict'] == 'INCONCLUSIVE'
                else 'No configured rule matched this recorded sample. This does not certify safety or complete coverage.')
        findings.append(f'<div class="no-findings"><h3>{E(status(r))} in this sample</h3><p>{note}</p></div>')
    for i, turn in enumerate(r['timeline']):
        flagged = i in event_ids
        event_rows.append(f'<li class="event{ " flagged" if flagged else ""}" id="{E(ident)}/event-{i}" data-speaker="{E(turn["who"])}" tabindex="-1">'
                          f'<a class="event-time" aria-label="Link to event at {turn["t"]:.3f} seconds" href="#{E(key)}/event-{i}">{turn["t"]:.3f}s</a>'
                          f'<div><span class="speaker">{E(turn["who"].capitalize())}{" · Finding" if flagged else ""}</span>'
                          f'<p>{E(turn["text"])}</p></div></li>')
    issues = ''.join(f'<li>{E(issue)}</li>' for issue in r.get('quality_issues', []))
    quality = f'<aside class="quality"><h3>Recording needs review</h3><ul>{issues}</ul></aside>' if issues else ''
    return f'''<article class="case-document" id="{E(ident)}" data-case="{E(key)}" tabindex="-1" aria-labelledby="{E(ident)}-title">
<header class="case-header"><div class="case-heading"><span class="suite-name">{E(case['suite_label'])} · {E(case['target'])}</span>
<h2 id="{E(ident)}-title">{E(r['name'])}</h2><p>{E(prompt_mode(case['hardened']))} · {E(r['class'])}</p></div>
<span class="verdict v-{r['verdict']}">{E(status(r))}</span></header>
<div class="case-actions" hidden><button type="button" data-copy="{E(key)}">Copy case link</button>
<button type="button" data-export="{E(key)}">Export evidence JSON</button></div>
{quality}<div class="case-content"><h3 class="section-title">Recorded findings <span>{len(r['findings'])}</span></h3>{''.join(findings)}
<section class="comparison"><h3 class="section-title">Recorded comparison</h3>{comparison(case, archive)}</section>
<section class="transcript"><div class="transcript-head"><div><h3 class="section-title">Conversation record</h3><p class="fine">{len(r['timeline'])} events · Exact timestamps · Original call audio is not embedded</p></div>
<label class="speaker-filter" hidden>Show <select data-speakers="{E(key)}"><option value="all">All speakers</option><option value="agent">Agent</option><option value="caller">Caller</option><option value="tool">Tool requests</option></select></label></div>
<p class="transcript-empty" hidden>No events from this speaker in the recording.</p><ol class="events">{''.join(event_rows)}</ol></section>
<details class="source"><summary>Source and recording scope</summary><dl><dt>Case</dt><dd>{E(r['attack'])}</dd><dt>Source report</dt><dd>{E(case['filename'])}</dd><dt>SHA-256</dt><dd>{case['sha256']}</dd></dl>
<p>Source hash identifies the archived report bytes. Targets are project-owned fixtures and business tools were mocked. Repeated voice conversations can produce different outcomes.</p></details></div></article>'''


def render_workspace(archive):
    items = []
    for case in archive['cases']:
        r = case['result']
        items.append(f'<li data-index-case="{E(case["key"])}"><a class="case-link" href="#{E(case["key"])}" data-open="{E(case["key"])}">'
                     f'<span class="index-suite">{E(case["suite_label"])}</span><strong>{E(r["name"])}</strong>'
                     f'<span class="index-result"><span class="status-dot v-{r["verdict"]}"></span>{E(status(r))}<span>{len(r["findings"])} finding{"s" if len(r["findings"]) != 1 else ""}</span></span></a></li>')
    options = ''.join(f'<option value="{E(s["tag"])}">{E(s["label"])}</option>' for s in archive['suites'])
    problems = ''.join(f'<li><strong>{E(p["suite"])}</strong> — {E(p["message"])}</li>' for p in archive['problems'])
    issue_notice = f'<details class="archive-issues"><summary>{len(archive["problems"])} unavailable recording suites</summary><ul>{problems}</ul></details>' if problems else ''
    body = ''.join(render_case(c, archive) for c in archive['cases'])
    if not body:
        body = '<div class="empty"><h2>No archived reports are available</h2><p>No conclusion can be drawn. Restore valid reports in the evidence folder and rebuild.</p></div>'
    payload = json.dumps(archive, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Voxrede · Evidence workspace</title><meta name="description" content="Inspect recorded voice-agent policy findings, their exact source events, and matching follow-up samples.">
<link rel="stylesheet" href="design.css"><link rel="stylesheet" href="assets/archive.css"><script src="assets/archive.js" defer></script></head>
<body><a class="skip-link" href="#workspace">Skip to evidence</a>
<header class="archive-nav"><a class="wordmark" href="./">Voxrede<span>Evidence workspace</span></a><div><a href="./#review">How it works</a><a href="watch.html">Watch demo</a></div></header>
<main><div class="archive-intro"><div><h1>Follow the <em>evidence.</em></h1><p>Inspect a recorded finding, read its source event, and compare the follow-up.</p></div>
<div class="archive-context"><strong>{len(archive['cases'])} recorded samples · {len(archive['suites'])} suites</strong><span>AssemblyAI voice sessions · Project-owned fixtures<br>Archived evidence · No API key needed</span></div></div>
{issue_notice}<div id="workspace" class="workspace"><aside class="case-index" aria-label="Recorded cases"><details class="recording-browser" open><summary>Browse {len(archive['cases'])} recordings</summary><div class="index-controls" hidden>
<label for="case-search">Find a recording</label><input type="search" id="case-search" placeholder="Search cases or transcript…" autocomplete="off">
<div class="filter-row"><label for="suite-filter">Recording suite<select id="suite-filter"><option value="all">All suites</option>{options}</select></label>
<label for="outcome-filter">Outcome<select id="outcome-filter"><option value="all">All outcomes</option><option value="findings">With findings</option><option value="clear">No finding</option><option value="incomplete">Needs review</option></select></label></div>
<div class="result-count"><span id="result-count" role="status" aria-live="polite"></span><button type="button" id="clear-filters">Reset</button></div></div>
<noscript><p>JavaScript is off. All archived cases are available below.</p></noscript><ul class="case-list">{''.join(items)}</ul></details></aside>
<div class="document-area"><div class="empty" id="search-empty" hidden><h2>No recordings match</h2><p>Try a shorter search or reset the filters.</p><button type="button" id="empty-reset">Reset filters</button></div>{body}</div></div>
<p class="archive-foot">A finding describes a recorded event. No finding is not a safety certificate. Comparisons use matching case IDs and fixture metadata; missing samples stay missing.</p></main>
<div class="action-status" id="action-status" role="status" aria-live="polite" hidden></div>
<div class="copy-fallback" id="copy-fallback" hidden><label for="copy-url">Copy this case link</label><input id="copy-url" readonly><button type="button" id="close-copy">Close</button></div>
<script id="archive-data" type="application/json">{payload}</script></body></html>'''


def build(evidence=Path('evidence'), output=Path('findings.html')):
    archive = load_archive(evidence)
    output.write_text(render_workspace(archive))
    print(f"wrote {output} with {len(archive['cases'])} recorded samples")
    return archive


if __name__ == '__main__':
    build()
