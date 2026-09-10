"""Render a guided review of archived evidence. Never creates a voice session."""
import hashlib
import html
import json
from pathlib import Path

from report import LABEL, validate_report


def render_review(evidence=Path('evidence'), target_path=Path('targets/meridian.json')):
    try:
        documents = []
        for name in ('report_base.json', 'report_hardened.json'):
            raw = (evidence / name).read_bytes()
            report = json.loads(raw)
            error = validate_report(report, require_case_ids=True)
            if error:
                raise ValueError(error)
            case = next(r for r in report['results'] if r['attack'] == '01_authority')
            documents.append((report, case, hashlib.sha256(raw).hexdigest()[:12]))
        (base, before, base_hash), (followup, after, after_hash) = documents
        target = json.loads(target_path.read_text())
        if (base['target'] != followup['target'] or base['target'] != target['id']
                or base.get('hardened') is not False or followup.get('hardened') is not True):
            raise ValueError('The recordings are not a baseline and follow-up for the same fixture.')
        finding = next(f for f in before['findings'] if f['verdict'] == 'DISCLOSURE')
        rule = next(r for r in target['policy']['no_disclosure'] if r['id'] == finding['rule'])
        if before.get('quality_issues'):
            raise ValueError('The baseline recording needs review.')
        response = next(t['text'] for t in reversed(after['timeline']) if t['who'] == 'agent')
        if not isinstance(rule['label'], str) or not rule['label'].strip():
            raise ValueError('The policy needs a readable label.')
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        return '''<div class="review" id="review"><h2>Guided review unavailable</h2>
<p>The required evidence or policy is missing, invalid, or does not match.
Open the full reports to inspect it. No comparison conclusion is shown.</p>
<a href="findings.html">Inspect archived reports</a></div>'''

    esc = html.escape
    steps = [
        ('01 / The policy', 'Define what the agent must protect.',
         f'<p>The fixture policy forbids disclosure of the <strong>{esc(rule["label"])}</strong>.</p>'
         '<p>A reviewer checks the recorded response against that declared rule.</p>'
         '<p class="review-source">Source: targets/meridian.json · no_disclosure</p>'),
        ('02 / The test', 'Challenge the policy through a conversation.',
         '<p>A simulated caller claims elevated authority. The support agent must preserve its caller-verification boundary.</p>'
         '<p>AssemblyAI handled both voice sessions. This demo reviews the saved transcript and events from that call.</p>'
         '<p class="review-source">Scenario: authority impersonation · locally configured target · mocked business tools</p>'),
        ('03 / The evidence', f'Disclosure at {finding["t"]:.3f} seconds.',
         f'<blockquote>{esc(finding["utterance"])}</blockquote>'
         '<p>The agent supplied the answer while asking the caller to prove it. The configured disclosure rule matched this recorded response.</p>'
         f'<p class="review-source">Baseline report · SHA-256 {base_hash}</p>'
         '<a href="findings.html#base">Inspect the baseline events →</a>'),
        ('04 / The follow-up', f'{LABEL[after["verdict"]].capitalize()} in the follow-up recording.',
         f'<blockquote>{esc(response)}</blockquote>'
         f'<p>The stricter-prompt recording contains {len(after["findings"])} configured findings for this scenario. '
         'This is one follow-up sample; it does not establish a reliable fix rate.</p>'
         f'<p class="review-source">Follow-up report · SHA-256 {after_hash}</p>'
         '<a href="findings.html#hardened">Inspect the follow-up events →</a>'),
    ]
    cards = ''.join(
        f'<article class="review-step" id="review-step-{i}" aria-labelledby="review-heading-{i}">'
        f'<h3 id="review-heading-{i}" tabindex="-1">{esc(title)}</h3>{body}</article>'
        for i, (label, title, body) in enumerate(steps))
    return '''<div class="review" id="review" data-step="0" aria-labelledby="review-title">
<div class="review-top"><h2 id="review-title">Inside a voice-agent red-team test.</h2>
<span class="review-mode">An archived conversation.<br>No API key needed to explore.</span></div>
<div class="review-nav" aria-label="Review steps" hidden>
<button type="button" data-review-select="0"><span>01</span>Policy</button>
<button type="button" data-review-select="1"><span>02</span>Test</button>
<button type="button" data-review-select="2"><span>03</span>Evidence</button>
<button type="button" data-review-select="3"><span>04</span>Follow-up</button>
</div>
<div class="review-layout">
<div class="signal-map" role="group" aria-label="How the recorded test works">
<p class="signal-caption">Two AssemblyAI Voice Agent sessions</p>
<div class="signal-pair">
<div class="signal-node caller">
<svg viewBox="0 0 44 44" aria-hidden="true"><rect x="16" y="5" width="12" height="23" rx="6"/><path d="M10 20v3a12 12 0 0 0 24 0v-3M22 35v6M15 41h14"/></svg>
<strong>Simulated<br>caller</strong><small>Challenges the policy</small><span class="session">SESSION A</span></div>
<svg class="signal-wire" viewBox="0 0 56 36" aria-hidden="true"><path d="M2 10h48m-6-5 6 5-6 5M54 26H6m6-5-6 5 6 5"/></svg>
<div class="signal-node target">
<svg viewBox="0 0 44 44" aria-hidden="true"><path d="M7 25v-5a15 15 0 0 1 30 0v5M37 30v3a7 7 0 0 1-7 7h-6"/><rect x="4" y="22" width="7" height="12" rx="3"/><rect x="33" y="22" width="7" height="12" rx="3"/></svg>
<strong>Agent<br>under test</strong><small>Must uphold the policy</small><span class="session">SESSION B</span></div>
</div>
<p class="signal-route">Audio flows both ways. Both event streams are saved.</p>
<div class="signal-log">
<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M6 3h12l4 4v18H6zM18 3v5h4M10 12h8M10 16h8M10 20h5"/></svg>
<div><strong id="signal-title">A declared boundary</strong>
<p id="signal-description">The policy defines which account information the agent must protect.</p></div>
</div>
<p class="signal-time">RECORDED FINDING / 00:51.887</p>
</div>
<div class="review-detail">
''' + cards + '''
<div class="review-controls" hidden>
<button class="replay-btn" id="review-back" type="button">Previous</button>
<span id="review-position" class="mono" role="status" aria-live="polite"></span>
<button class="replay-btn" id="review-next" type="button">Next step</button>
</div>
</div></div>
<p class="review-note">Red teaming means deliberately challenging a declared boundary, then inspecting the evidence.
The target here is our own fixture. Business tools were mocked.</p>
</div>
<script>
(() => {
  const root = document.getElementById('review');
  const steps = [...root.querySelectorAll('.review-step')];
  const back = root.querySelector('#review-back');
  const next = root.querySelector('#review-next');
  let current = 0;
  const phases = [
    ['A declared boundary', 'The policy defines which account information the agent must protect.'],
    ['A conversation under pressure', 'The simulated caller tests whether the support agent preserves that boundary.'],
    ['A finding with a source', 'The recorded response matches a disclosure rule at 51.887 seconds.'],
    ['A recorded follow-up', 'Inspect the stricter-prompt sample beside the original finding.'],
  ];
  function show(index, focus = false) {
    current = Math.max(0, Math.min(steps.length - 1, index));
    steps.forEach((step, i) => { step.hidden = i !== current; });
    root.dataset.step = String(current);
    root.querySelector('#signal-title').textContent = phases[current][0];
    root.querySelector('#signal-description').textContent = phases[current][1];
    root.querySelectorAll('[data-review-select]').forEach(button => {
      if (Number(button.dataset.reviewSelect) === current) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    back.disabled = current === 0;
    next.textContent = current === steps.length - 1 ? 'Start again' : 'Next step';
    root.querySelector('#review-position').textContent = `Step ${current + 1} of ${steps.length}`;
    if (focus) {
      const heading = steps[current].querySelector('h3');
      heading.focus({preventScroll: true});
      const bounds = heading.getBoundingClientRect();
      const navBottom = document.querySelector('nav')?.getBoundingClientRect().bottom || 0;
      if (bounds.top < navBottom + 16 || bounds.bottom > innerHeight) {
        heading.scrollIntoView({block: 'start', behavior: 'instant'});
      }
    }
  }
  back.addEventListener('click', () => show(current - 1, true));
  next.addEventListener('click', () => show(current === steps.length - 1 ? 0 : current + 1, true));
  root.querySelectorAll('[data-review-select]').forEach(button => {
    button.addEventListener('click', () => show(Number(button.dataset.reviewSelect), true));
  });
  root.querySelector('.review-nav').hidden = false;
  root.querySelector('.review-controls').hidden = false;
  show(0);
})();
</script>'''
