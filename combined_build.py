"""One page carrying all three reports, tab-switched client side."""
import json
from pathlib import Path
from report import render, CSS

PAGES = [("base", "Baseline", "report_base.json",
          "The agent as a competent developer would ship it: the prompt tells it "
          "to verify the caller owns the account."),
         ("lax", "No verification step", "report_lax.json",
          "The same agent with the ownership check missing from the prompt. The "
          "tool was wired up, the guardrail was never written."),
         ("hardened", "After the fix", "report_hardened.json",
          "The same two attacks re-run after appending the guardrail the report "
          "suggests.")]

SHELL = """<title>Voxrede Findings</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;550;600;650&family=Geist+Mono:wght@400;500;600&display=swap">
<style>%s
.topnav{position:sticky;top:0;z-index:30;border-bottom:1px solid var(--line);
background:color-mix(in srgb,var(--ground) 84%%,transparent);backdrop-filter:blur(14px)}
.topnav .inner{max-width:1060px;margin:0 auto;padding:0 28px;min-height:64px;
display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.topnav .bd{font-weight:680;letter-spacing:-.04em;font-size:18px;margin-right:auto}
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
<span class="bd">Voxrede</span><a class="tb" href="https://claude.ai/code/artifact/d4831598-06da-49eb-8fbc-8766a25bd8d1" style="text-decoration:none">Overview</a>%s
</div></div>
%s
<div class="foot">Call audio and live attack runs need the server running
locally. Scoring is deterministic, the calls are not: both sides are LLM-driven,
so the same attack can break an agent on one run and hold on the next.</div>
<script>
const tabs=[...document.querySelectorAll(".tb")];
function show(id){
  tabs.forEach(function(t){t.setAttribute("aria-selected", String(t.dataset.t===id));});
  document.querySelectorAll(".panel").forEach(function(p){p.hidden = p.dataset.t!==id;});
}
tabs.forEach(function(t){t.addEventListener("click",function(){show(t.dataset.t);});});
show("base");
</script>"""


def build():
    btns, panels = [], []
    for tag, label, src, blurb in PAGES:
        p = Path("evidence") / src
        if not p.exists():
            continue
        btns.append(f'<button class="tb" data-t="{tag}" role="tab" '
                    f'aria-selected="false">{label}</button>')
        body = render(json.loads(p.read_text()), title=f"{label}")
        panels.append(f'<div class="panel" data-t="{tag}" hidden>'
                      f'<div class="ctx">{blurb}</div>{body}</div>')
    Path("findings.html").write_text(
        SHELL % (CSS, "".join(btns), "".join(panels)))
    print(f"wrote findings.html with {len(panels)} reports, "
          f"{Path('findings.html').stat().st_size//1024} KB")


build()
