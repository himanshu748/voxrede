"""One page carrying the archived reports, tab-switched client side."""
import json, re
from pathlib import Path
from report import render, CSS

PAGES = [("base", "Baseline", "report_base.json",
          "The agent as a competent developer would ship it: the prompt tells it "
          "to verify the caller owns the account."),
         ("lax", "No verification step", "report_lax.json",
          "The same agent with the ownership check missing from the prompt. The "
          "tool was wired up, the guardrail was never written."),
         ("hardened", "After guardrail", "report_hardened.json",
          "The same two attacks re-run after appending the guardrail the report "
          "suggests. These samples do not establish a fix rate."),
         ("noisecheck", "Audio condition", "report_noisecheck.json", "One archived audio-condition sample; no coverage claim."),
         ("demoaudio", "Repeat sample", "report_demoaudio.json", "A later recording. Outcomes vary between calls."),
         ("base2", "Second baseline", "report_base2.json", "A second baseline recording. Compare only the scenarios present in both samples.")]

SHELL = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Voxrede Findings</title>
<style>%s
.topnav{position:sticky;top:0;z-index:30;border-bottom:1px solid var(--line);
background:color-mix(in srgb,var(--ground) 84%%,transparent);backdrop-filter:blur(14px)}
.topnav .inner{max-width:1060px;margin:0 auto;padding:0 28px;min-height:64px;
display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.topnav .bd{font-weight:680;letter-spacing:-.04em;font-size:18px;margin-right:auto}
.tabs{display:flex;gap:10px;flex-wrap:wrap;padding:10px 0}
.tb{padding:8px 15px;border:1px solid var(--line);border-radius:999px;
color:var(--dim);font-size:13px;font-weight:540;cursor:pointer;background:none;
font-family:inherit;transition:border-color .15s,color .15s}
.tb:hover{color:var(--text);border-color:var(--faint)}
.tb[aria-selected="true"]{background:var(--text);color:var(--ground);
border-color:var(--text)}
.tb:focus-visible{outline:2px solid var(--leaked);outline-offset:2px}
.ctx{max-width:1060px;margin:0 auto;padding:26px 28px 0;color:var(--dim);
font-size:15.5px;max-width:70ch}
.foot{max-width:1060px;margin:0 auto;padding:0 28px 60px;color:var(--faint);
font-size:13px;line-height:1.7}
</style>
<div class="topnav"><div class="inner">
<span class="bd">Voxrede</span><a class="tb" href="./" style="text-decoration:none">Overview</a>
<div class="tabs" role="tablist" aria-label="Recorded suites">%s</div>
</div></div>
%s
<div class="foot">This page displays archived event logs. Audio is not embedded here.
Tool execution was mocked. Scoring is deterministic, the calls are not: both sides are LLM-driven,
so the same attack can break an agent on one run and hold on the next.</div>
<script>
const tabs=[...document.querySelectorAll("button[data-t]")];
function show(id){
  if(!tabs.length) return;
  if(!tabs.some(t=>t.dataset.t===id)) id=tabs[0].dataset.t;
  tabs.forEach(function(t){
    const selected=t.dataset.t===id;
    t.setAttribute("aria-selected", String(selected));
    t.tabIndex=selected?0:-1;
  });
  document.querySelectorAll(".panel").forEach(function(p){p.hidden = p.dataset.t!==id;});
}
function fromHash(){show(location.hash.slice(1));}
tabs.forEach(function(t,i){
  t.addEventListener("click",function(){location.hash=t.dataset.t;show(t.dataset.t);});
  t.addEventListener("keydown",function(e){
    let next;
    if(e.key==="ArrowRight") next=(i+1)%%tabs.length;
    else if(e.key==="ArrowLeft") next=(i+tabs.length-1)%%tabs.length;
    else if(e.key==="Home") next=0;
    else if(e.key==="End") next=tabs.length-1;
    else return;
    e.preventDefault();tabs[next].focus();tabs[next].click();
  });
});
window.addEventListener("hashchange",fromHash);
fromHash();
</script>"""


def build():
    btns, panels = [], []
    for tag, label, src, blurb in PAGES:
        p = Path("evidence") / src
        if not p.exists():
            continue
        btns.append(f'<button class="tb" data-t="{tag}" role="tab" '
                    f'id="tab-{tag}" aria-controls="panel-{tag}" tabindex="-1" '
                    f'aria-selected="false">{label}</button>')
        body = render(json.loads(p.read_text()), title=f"{label}")
        body = re.sub(r"<audio[^>]*></audio>", "", body)
        panels.append(f'<div class="panel" data-t="{tag}" id="panel-{tag}" '
                      f'role="tabpanel" aria-labelledby="tab-{tag}" tabindex="0" hidden>'
                      f'<div class="ctx">{blurb}</div>{body}</div>')
    if not panels:
        panels.append('<div class="ctx">No archived reports are available. No conclusion can be drawn.</div>')
    Path("findings.html").write_text(
        SHELL % (CSS, "".join(btns), "".join(panels)))
    print(f"wrote findings.html with {len(panels)} reports, "
          f"{Path('findings.html').stat().st_size//1024} KB")


if __name__ == "__main__":
    build()
