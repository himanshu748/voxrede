"""Generate the pitch deck from the same verified data as the other pages."""
import html, json
from pathlib import Path
from scorer import score

T = json.loads(Path("targets/meridian.json").read_text())
TL = json.loads(Path("targets/meridian_lax.json").read_text())
base = score("evidence/logs/base_01_authority.jsonl", T)
lax = score("evidence/logs/lax_01_authority.jsonl", TL)
rep = json.loads(Path("evidence/report_base.json").read_text())

leak = base["findings"][0]
tool = lax["findings"][0]
held = sum(1 for r in rep["results"] if r["verdict"] == "PASS")
total = len(rep["results"])

CSS = """
:root{--ground:#07090c;--surface:#0f1319;--line:#232c37;--text:#f2f6fa;
--dim:#93a1b1;--faint:#697687;--leaked:#ffb443;--fired:#ff6a5e;--held:#5ef08f}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--ground);color:var(--text);
font-family:Geist,ui-sans-serif,-apple-system,"Segoe UI",sans-serif}
.mono{font-family:"Geist Mono",ui-monospace,Menlo,monospace}
.deck{height:100vh;overflow-y:auto;scroll-snap-type:y mandatory}
.s{height:100vh;scroll-snap-align:start;display:flex;flex-direction:column;
justify-content:center;padding:7vh 8vw;position:relative;border-bottom:1px solid var(--line)}
.n{position:absolute;top:4vh;right:8vw;font-size:12px;color:var(--faint);
letter-spacing:.14em}
.eye{font-size:12px;letter-spacing:.2em;text-transform:uppercase;
color:var(--faint);margin-bottom:22px}
h1{font-size:clamp(34px,6.4vw,86px);line-height:.95;letter-spacing:-.05em;
margin:0;font-weight:660;max-width:18ch}
h2{font-size:clamp(26px,4.2vw,54px);line-height:1.02;letter-spacing:-.042em;
margin:0;font-weight:640;max-width:20ch}
p{font-size:clamp(15px,1.7vw,21px);color:var(--dim);max-width:60ch;
line-height:1.55;margin:26px 0 0;letter-spacing:-.012em}
p b{color:var(--text);font-weight:560}
.quote{font-size:clamp(19px,3.1vw,40px);line-height:1.25;letter-spacing:-.03em;
margin:30px 0 0;max-width:22ch;font-weight:500}
.quote mark{background:var(--leaked);color:var(--ground);padding:.02em .16em;
border-radius:5px}
.ev{margin-top:30px;padding:20px 24px;border-left:3px solid var(--fired);
background:rgba(255,106,94,.08);border-radius:0 10px 10px 0;overflow-x:auto}
.ev code{font-family:"Geist Mono",Menlo,monospace;font-size:clamp(12px,1.3vw,16px);
color:var(--fired);white-space:pre}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:38px;
border-top:1px solid var(--line)}
.grid div{padding:24px 26px 0 0;border-right:1px solid var(--line)}
.grid div:last-child{border-right:0}
.grid h3{margin:0 0 10px;font-size:clamp(15px,1.7vw,20px);font-weight:600;
letter-spacing:-.022em}
.grid p{margin:0;font-size:clamp(13px,1.3vw,15px)}
.tbl{margin-top:34px;border-top:1px solid var(--line);max-width:760px}
.row{display:grid;grid-template-columns:1fr auto auto;gap:24px;padding:14px 0;
border-bottom:1px solid var(--line);font-size:clamp(13px,1.5vw,17px)}
.row .b{color:var(--leaked);text-align:right}
.row .a{color:var(--held);text-align:right;min-width:70px}
.big{font-size:clamp(46px,9vw,120px);line-height:.9;letter-spacing:-.05em;
font-weight:660;margin-top:20px}
.sub{color:var(--faint);font-size:14px;margin-top:auto;padding-top:30px}
a{color:var(--leaked)}
@media print{
  html,body{height:auto}
  .deck{height:auto;overflow:visible}
  .s{height:auto;min-height:0;page-break-after:always;border-bottom:0;
     padding:40px 50px}
}
"""

def slide(n, body):
    return f'<section class="s"><div class="n mono">{n}</div>{body}</section>'

SLIDES = [
    ('<div class="eye mono">Voxrede</div>'
     '<h1>It asked for proof, then read out the answer.</h1>'
     '<p>Policy findings traced to recorded voice-agent events.</p>'
     '<div class="sub mono">Built on the AssemblyAI Voice Agent API</div>'),
    ('<div class="eye mono">The user</div>'
     '<h2>Support teams need evidence they can inspect.</h2>'
     '<p>A voice agent can sound careful while disclosing a protected value. '
     'Teams reviewing support calls need to see the response, the policy it violated, '
     'and the event timestamp together.</p>'),
    ('<div class="eye mono">Existing tools</div>'
     '<h2>Voice-agent testing already includes security.</h2>'
     '<p>Bluejay offers voice simulation and red teaming with AssemblyAI integration. '
     'Voxrede focuses this demo on a small, inspectable record: a declared rule, '
     'a transcript or tool event, and a timestamp.</p>'
     '<p><a href="https://getbluejay.ai/blog/bluejay-x-assemblyai-test-voice-agents-built-on-the-voice-agent-api">Bluejay + AssemblyAI, September 3, 2026</a></p>'),
    ('<div class="eye mono">The recorded finding</div>'
     '<h2>The agent named the answer to its own challenge.</h2>'
     f'<div class="quote mono">{html.escape(leak["utterance"][leak["utterance"].find("Could you"):])}</div>'
     f'<p>Disclosure at {leak["t"]:.3f}s. Later refusals do not undo it. '
     'This finding is also detectable from the transcript.</p>'),
    ('<div class="eye mono">A separate fixture</div>'
     '<h2>A tool request is evidence of a request.</h2>'
     f'<div class="ev"><code>{tool["t"]:.3f}s  tool.call  {html.escape(tool["tool"])}\n'
     'proof     none recorded</code></div>'
     '<p>The fixture omitted the ownership check. The agent requested a refund. '
     '<b>The tool handler was mocked. No money moved.</b></p>'),
    ('<div class="eye mono">AssemblyAI role</div>'
     '<h2>Voice conversations, recorded as events.</h2>'
     '<div class="grid"><div><h3>Voice sessions</h3><p>AssemblyAI Voice Agent API '
     'powered both sides of the archived conversations.</p></div>'
     '<div><h3>Event logs</h3><p>Saved transcripts and tool requests preserve '
     'what the agent emitted and when.</p></div>'
     '<div><h3>Review</h3><p>Deterministic rules link findings back to recorded '
     'events. Judges can inspect the static reports without an API key.</p></div></div>'),
    ('<div class="eye mono">Archived comparison</div>'
     f'<h2>{total - held} of {total} baseline samples contained findings.</h2>'
     '<p>Two previously flagged scenarios had no finding in the recorded '
     'follow-up with a stricter prompt. The count fell from five findings to zero '
     'across those two samples.</p>'
     '<p><b>This is a small sample comparison, not a measured fix rate.</b></p>'),
    ('<div class="eye mono">Recording quality</div>'
     '<h2>Missing evidence cannot count as a pass.</h2>'
     '<p>Unreadable logs, missing dialogue, and detected provider errors produce '
     'an Inconclusive verdict. Existing findings remain visible.</p>'
     '<p>No finding means no configured rule matched that sample. '
     'It does not certify complete recording or policy coverage.</p>'),
    ('<div class="eye mono">Scope</div>'
     '<h2>Own fixtures. Mocked tools. Recorded samples.</h2>'
     '<p>The six scenarios are not a benchmark. No production system or payment '
     'service was tested. There is no telephony leg.</p>'
     '<p>Both sides used generated dialogue, so outcomes vary between recordings. '
     'The public demo is an archived report viewer.</p>'),
    ('<div class="eye mono">Voxrede</div>'
     '<h1>Inspect the finding.</h1>'
     '<p>Read the policy-linked event, then compare it with the recorded follow-up.</p>'
     '<div class="sub mono">github.com/himanshu748/voxrede<br>'
     'himanshu748.github.io/voxrede/findings.html</div>'),
]

page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Voxrede deck</title>\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Geist:wght@400;500;560;600;640;660&family=Geist+Mono:wght@400;500&'
        'display=swap">\n'
        f"<style>{CSS}</style>\n<div class='deck'>"
        + "".join(slide(f"{i+1:02d} / {len(SLIDES):02d}", b)
                  for i, b in enumerate(SLIDES))
        + "</div>")
Path("deck.html").write_text(page)
print(f"wrote deck.html, {len(SLIDES)} slides, {len(page)} bytes")
