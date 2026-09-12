"""Build a static, deployable copy of the console: reports plus audio, no server."""
import json, re, shutil
from pathlib import Path
from report import render, CSS

PAGES = [("base", "Baseline", "report_base.json"),
         ("lax", "No verification step", "report_lax.json"),
         ("hardened", "After guardrail", "report_hardened.json"),
         ("noisecheck", "Audio condition", "report_noisecheck.json"),
         ("demoaudio", "Repeat sample", "report_demoaudio.json"),
         ("base2", "Second baseline", "report_base2.json")]

NAV = """<style>%s
.topnav{position:sticky;top:0;z-index:30;border-bottom:1px solid var(--line);
background:color-mix(in srgb,var(--ground) 84%%,transparent);backdrop-filter:blur(14px)}
.topnav .inner{max-width:1060px;margin:0 auto;padding:0 28px;min-height:64px;
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

LIVE_NOTE = ("Archived report viewer. Tool execution was mocked. "
             "Call audio and live attack runs need the server running locally, "
             "see the repo README.")


def local_overview_links(page):
    return page.replace('href="./"', 'href="overview.html"').replace(
        'href="./#', 'href="overview.html#')


def build(source_dir=Path("."), out_dir=None):
    """Build from local saved files; remove pages for reports no longer present."""
    source = Path(source_dir)
    out = Path(out_dir) if out_dir is not None else source / "static"
    out.mkdir(parents=True, exist_ok=True)
    (out / "audio").mkdir(exist_ok=True)
    shutil.copytree(source / 'assets', out / 'assets', dirs_exist_ok=True)
    shutil.copy(source / "design.css", out / "design.css")

    available = []
    for tag, label, filename in PAGES:
        path = source / "evidence" / filename
        if path.is_file():
            available.append((tag, label, path))
        else:
            name = "index.html" if tag == "base" else f"{tag}.html"
            (out / name).unlink(missing_ok=True)
            print(f"skip {tag}, no {filename}")

    links = lambda cur: ('<a href="overview.html">Overview</a>' + "".join(
        f'<a href="{"index.html" if t == "base" else t + ".html"}" '
        f'class="{"on" if t == cur else ""}">{lbl}</a>'
        for t, lbl, _ in available))

    for tag, label, path in available:
        report = json.loads(path.read_text())
        body = render(report, title=f"{label} report")
        # static audio lives beside the page, and compressed
        # audio ships with the local server, not the static copy
        body = re.sub(r"<audio[^>]*></audio>", "", body)
        html = (f"<title>Voxrede {label}</title>\n"
                + NAV % (CSS, links(tag), LIVE_NOTE) + body)
        name = "index.html" if tag == "base" else f"{tag}.html"
        (out / name).write_text(html)
        print(f"wrote {out / name}")

    shutil.copy(source / "landing.html", out / "overview.html")
    (out / "findings.html").write_text(local_overview_links((source / "findings.html").read_text()))
    shutil.copy(source / "deck.html", out / "deck.html")
    if (source / "watch.html").is_file():
        (out / "watch.html").write_text(local_overview_links((source / "watch.html").read_text()))
    else:
        (out / "watch.html").unlink(missing_ok=True)
    print(f"wrote {out / 'overview.html'}, findings.html, deck.html")
    return out


if __name__ == "__main__":
    build()
