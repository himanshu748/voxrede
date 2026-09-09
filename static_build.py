"""Build a static, deployable copy of the console: reports plus audio, no server."""
import json, shutil
from pathlib import Path
from report import render, CSS

PAGES = [("base", "Baseline", "report_base.json"),
         ("lax", "No verification step", "report_lax.json"),
         ("hardened", "After the fix", "report_hardened.json")]

NAV = """<style>%s
.topnav{position:sticky;top:0;z-index:30;border-bottom:1px solid var(--line);
background:color-mix(in srgb,var(--ground) 84%%,transparent);backdrop-filter:blur(14px)}
.topnav .inner{max-width:1060px;margin:0 auto;padding:0 28px;height:64px;
display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.topnav .bd{font-weight:680;letter-spacing:-.04em;font-size:18px;margin-right:auto}
.topnav a{padding:8px 15px;border:1px solid var(--line);border-radius:999px;
color:var(--dim);text-decoration:none;font-size:13px;font-weight:540}
.topnav a:hover{color:var(--text);border-color:var(--faint)}
.topnav a.on{background:var(--text);color:var(--ground);border-color:var(--text)}
.note{max-width:1060px;margin:0 auto;padding:20px 28px 0;color:var(--faint);
font-size:13px}
</style>
<div class="topnav"><div class="inner">
<span class="bd">Voxrede</span>%s
</div></div>
<div class="note">%s</div>"""

LIVE_NOTE = ("Static report viewer. Every finding here came from a real call. "
             "Call audio and live attack runs need the server running locally, "
             "see the repo README.")


def build():
    out = Path("static")
    out.mkdir(exist_ok=True)
    (out / "audio").mkdir(exist_ok=True)

    links = lambda cur: ('<a href="/overview.html">Overview</a>' + "".join(
        f'<a href="/{"" if t == "base" else t + ".html"}" '
        f'class="{"on" if t == cur else ""}">{lbl}</a>'
        for t, lbl, _ in PAGES))

    for tag, label, src in PAGES:
        p = Path("evidence") / src
        if not p.exists():
            print(f"skip {tag}, no {src}")
            continue
        report = json.loads(p.read_text())
        body = render(report, title=f"{label} report")
        # static audio lives beside the page, and compressed
        # audio ships with the local server, not the static copy
        import re as _re
        body = _re.sub(r"<audio[^>]*></audio>", "", body)
        html = (f"<title>Voxrede {label}</title>\n"
                + NAV % (CSS, links(tag), LIVE_NOTE) + body)
        name = "index.html" if tag == "base" else f"{tag}.html"
        (out / name).write_text(html)
        print(f"wrote static/{name}")

    shutil.copy("landing.html", out / "overview.html")
    print("wrote static/overview.html")


build()
