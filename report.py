"""Render a suite report as a standalone HTML page."""
import html, json, math, sys
from pathlib import Path

CSS = """
:root{
  --ground:#ffffff; --surface:#f4f6f9; --raise:#e8ecf1; --line:#d3dae2;
  --text:#05080b; --dim:#4d5966; --faint:#7d8a98;
  --held:#127a3d; --leaked:#8f5106; --fired:#bd2a20;
  --held-bg:rgba(18,122,61,.09); --leaked-bg:rgba(143,81,6,.10);
  --fired-bg:rgba(189,42,32,.09);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#07090c; --surface:#0f1319; --raise:#171d25; --line:#232c37;
    --text:#f2f6fa; --dim:#93a1b1; --faint:#697687;
    --held:#5ef08f; --leaked:#ffb443; --fired:#ff6a5e;
    --held-bg:rgba(94,240,143,.11); --leaked-bg:rgba(255,180,67,.12);
    --fired-bg:rgba(255,106,94,.12);
  }
}
:root[data-theme="dark"]{
  --ground:#07090c; --surface:#0f1319; --raise:#171d25; --line:#232c37;
  --text:#f2f6fa; --dim:#93a1b1; --faint:#697687;
  --held:#5ef08f; --leaked:#ffb443; --fired:#ff6a5e;
  --held-bg:rgba(94,240,143,.11); --leaked-bg:rgba(255,180,67,.12);
  --fired-bg:rgba(255,106,94,.12);
}
*{box-sizing:border-box}
html,body{overflow-x:hidden}
body{margin:0;background:var(--ground);color:var(--text);
  font:15px/1.55 Geist,ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased}
.mono,code{font-family:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
.wrap{max-width:1060px;margin:0 auto;padding:44px 28px 90px}
h1{font-size:clamp(30px,5vw,52px);margin:0 0 10px;letter-spacing:-.045em;
  line-height:.98;font-weight:660}
.sub{color:var(--dim);margin-bottom:34px;font-size:17px;letter-spacing:-.012em}
.summary{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:34px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:18px 22px;min-width:146px}
.stat b{display:block;font-size:32px;line-height:1.05;letter-spacing:-.035em;
  font-variant-numeric:tabular-nums;font-weight:650}
.stat span{color:var(--faint);font-size:11px;text-transform:uppercase;
  letter-spacing:.13em;margin-top:8px;display:block}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;
  margin-bottom:14px;overflow:hidden;transition:border-color .16s}
.card:hover{border-color:var(--faint)}
.card>summary{padding:18px 22px;cursor:pointer;display:flex;align-items:center;
  gap:14px;list-style:none;flex-wrap:wrap}
.card>summary::-webkit-details-marker{display:none}
.card>summary:focus-visible{outline:2px solid var(--leaked);outline-offset:-2px}
.badge{font-size:10.5px;font-weight:700;letter-spacing:.12em;padding:5px 11px;
  border-radius:999px;white-space:nowrap}
.b-PASS{background:var(--held-bg);color:var(--held)}
.b-INCONCLUSIVE{background:var(--raise);color:var(--dim)}
.b-DISCLOSURE{background:var(--leaked-bg);color:var(--leaked)}
.b-UNAUTHORIZED_TOOL_CALL{background:var(--fired-bg);color:var(--fired)}
.aname{font-weight:620;flex:1 1 auto;min-width:0;letter-spacing:-.02em;font-size:16px}
.aclass{color:var(--faint);font-size:11px;letter-spacing:.11em;text-transform:uppercase}
.body{padding:0 22px 22px;border-top:1px solid var(--line)}
.goal{color:var(--dim);margin:16px 0 20px;font-size:14px}
audio{width:100%;margin:0 0 18px;height:36px}
.finding{border-left:3px solid var(--fired);background:var(--fired-bg);
  padding:16px 18px;border-radius:0 10px 10px 0;margin-bottom:16px}
.finding.d{border-color:var(--leaked);background:var(--leaked-bg)}
.finding h4{margin:0 0 8px;font-size:14px;letter-spacing:-.015em}
.finding code{background:color-mix(in srgb,var(--text) 10%,transparent);
  padding:2px 7px;border-radius:5px;overflow-wrap:break-word}
.finding div{min-width:0;overflow-wrap:break-word}
.finding .args{margin:12px 0;padding:12px 14px;border-radius:8px;font-size:12.5px;
  line-height:1.65;background:color-mix(in srgb,var(--text) 7%,transparent);
  overflow-x:auto;white-space:pre}
.turn{display:grid;grid-template-columns:52px 74px 1fr;gap:14px;padding:9px 0;
  border-bottom:1px solid color-mix(in srgb,var(--line) 55%,transparent);
  font-size:14px}
.turn:last-child{border-bottom:0}
.turn>div:last-child{min-width:0;overflow-wrap:anywhere}
.t{color:var(--faint);font-size:11.5px;font-variant-numeric:tabular-nums}
.who{color:var(--faint);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase}
.who.caller{color:var(--dim)}
.turn.bad{background:var(--leaked-bg);margin:0 -10px;padding-left:10px;
  padding-right:10px;border-radius:8px}
.turn.bad .t,.turn.bad .who{color:var(--leaked)}
.turn.tool{background:var(--fired-bg);margin:0 -10px;padding:11px 10px;
  border-radius:8px;font-family:"Geist Mono",ui-monospace,Menlo,monospace;
  font-size:12.5px}
.turn.tool>div:last-child{overflow-x:auto}
.turn.tool .t,.turn.tool .who{color:var(--fired)}
footer{color:var(--faint);font-size:12.5px;margin-top:38px;
  border-top:1px solid var(--line);padding-top:20px;line-height:1.7}
@media (max-width:560px){
  .turn{grid-template-columns:44px 1fr;gap:6px}
  .who{display:none}
}
"""

LABEL = {"PASS": "NO FINDING", "DISCLOSURE": "LEAKED",
         "UNAUTHORIZED_TOOL_CALL": "TOOL REQUESTED", "INCONCLUSIVE": "INCONCLUSIVE"}


def plain(text):
    """Render dashes as hyphens. Wording is untouched; the stored logs keep
    whatever the transcription produced."""
    return text.replace("\u2014", "-").replace("\u2013", "-")


def validate_report(report, *, require_case_ids=False):
    """Reject malformed display data instead of rendering a misleading pass."""
    def timestamp(value):
        try:
            return type(value) in (int, float) and math.isfinite(value) and value >= 0
        except OverflowError:
            return False

    if (not isinstance(report, dict) or not isinstance(report.get("target"), str)
            or not report["target"].strip()):
        return "Missing or invalid report target."
    rows = report.get("results")
    if not isinstance(rows, list) or not rows:
        return "No recorded results are available."
    case_ids = set()
    for row in rows:
        if not isinstance(row, dict):
            return "Invalid result record."
        if require_case_ids:
            case_id = row.get("attack")
            if not isinstance(case_id, str) or not case_id.strip() or case_id in case_ids:
                return "Missing or duplicate case identifier."
            case_ids.add(case_id)
        if not isinstance(row.get("verdict"), str) or row["verdict"] not in LABEL:
            return "Unknown or missing verdict."
        if any(not isinstance(row.get(k), str) for k in ("name", "class", "goal")):
            return "Missing or invalid result description."
        findings, timeline = row.get("findings"), row.get("timeline")
        if not isinstance(findings, list) or not isinstance(timeline, list):
            return "Missing or invalid findings or timeline."
        issues = row.get("quality_issues", [])
        if not isinstance(issues, list) or any(not isinstance(x, str) for x in issues):
            return "Invalid recording-quality information."
        if row.get("wav") is not None and not isinstance(row["wav"], str):
            return "Invalid recording reference."
        for finding in findings:
            if not isinstance(finding, dict) or not timestamp(finding.get("t")):
                return "Invalid finding timestamp."
            kind = finding.get("verdict")
            required = ("tool", "why") if kind == "UNAUTHORIZED_TOOL_CALL" else ("label", "matched")
            if kind not in ("DISCLOSURE", "UNAUTHORIZED_TOOL_CALL") or any(
                    not isinstance(finding.get(k), str) for k in required):
                return "Invalid finding details."
            if kind == "UNAUTHORIZED_TOOL_CALL" and not {"arguments", "requires"}.issubset(finding):
                return "Incomplete tool-request evidence."
        if (row["verdict"] == "PASS" and (findings or issues)) or (
                row["verdict"] in ("DISCLOSURE", "UNAUTHORIZED_TOOL_CALL") and not findings):
            return "Verdict conflicts with its recorded evidence."
        for turn in timeline:
            if (not isinstance(turn, dict) or not timestamp(turn.get("t"))
                    or turn.get("who") not in ("caller", "agent", "tool")
                    or not isinstance(turn.get("text"), str)):
                return "Invalid timeline entry."
        if row["verdict"] == "PASS" and not {"caller", "agent"}.issubset(
                {turn["who"] for turn in timeline if turn["text"].strip()}):
            return "No-finding result is missing two-sided dialogue."
    return None


def render(report, title="Voice agent red-team report"):
    problem = validate_report(report)
    if problem:
        return (f"<style>{CSS}</style><div class='wrap'><h1>{html.escape(title)}</h1>"
                "<p class='badge b-INCONCLUSIVE'>INCONCLUSIVE</p>"
                f"<p>{html.escape(problem)}</p>"
                "<p>The source report needs review; no pass rate is shown.</p></div>")
    rs = report["results"]
    passed = sum(r["verdict"] == "PASS" for r in rs)
    inconclusive = sum(r["verdict"] == "INCONCLUSIVE" for r in rs)
    all_f = [f for r in rs for f in r["findings"]]
    tool = [f for f in all_f if f["verdict"] == "UNAUTHORIZED_TOOL_CALL"]
    leak = [f for f in all_f if f["verdict"] == "DISCLOSURE"]
    mode = "hardened prompt" if report.get("hardened") else "baseline prompt"

    out = [f"<style>{CSS}</style><div class='wrap'>",
           f"<h1>{html.escape(title)}</h1>",
           f"<div class='sub'>Target <b>{html.escape(report['target'])}</b> "
           f"&middot; {mode} &middot; {len(rs)} "
           f"attack{'s' if len(rs) != 1 else ''}</div>",
           "<div class='summary'>",
           f"<div class='stat'><b>{passed}/{len(rs)}</b>"
           "<span>no finding in sample</span></div>",
           f"<div class='stat'><b>{inconclusive}</b><span>inconclusive</span></div>",
           f"<div class='stat'><b style='color:var(--fired)'>{len(tool)}</b>"
           "<span>unauthorized tool requests</span></div>",
           f"<div class='stat'><b style='color:var(--leaked)'>{len(leak)}</b>"
           "<span>disclosures</span></div>", "</div>"]

    for r in rs:
        v = r["verdict"]
        bad_t = {f["t"] for f in r["findings"]}
        out.append(
            f"<details class='card'{' open' if v != 'PASS' else ''}>"
            f"<summary><span class='badge b-{v}'>{LABEL[v]}</span>"
            f"<span class='aname'>{html.escape(r['name'])}</span>"
            f"<span class='aclass'>{html.escape(r['class'])}</span></summary>"
            f"<div class='body'><div class='goal'>Goal: {html.escape(r['goal'])}</div>")

        for issue in r.get("quality_issues", []):
            out.append(f"<p class='goal'>Recording quality: {html.escape(issue)}</p>")

        if r.get("wav"):
            src = "/audio/" + html.escape(Path(r["wav"]).name)
            out.append(f"<audio controls preload='none' src='{src}'></audio>")

        for f in r["findings"]:
            if f["verdict"] == "UNAUTHORIZED_TOOL_CALL":
                out.append(
                    f"<div class='finding'><h4>Unauthorized tool call: "
                    f"<code>{html.escape(f['tool'])}</code></h4>"
                    f"<div>Requested at {f['t']}s without "
                    f"<code>{html.escape(str(f['requires']))}</code>.</div>"
                    f"<pre class='args mono'>{html.escape(json.dumps(f['arguments'], indent=2))}</pre>"
                    f"<div>Tool execution in this demo is mocked; this event does not prove a refund occurred."
                    f"</div><div class='goal' style='margin:8px 0 0'>"
                    f"{html.escape(f['why'])}</div></div>")
            else:
                out.append(
                    f"<div class='finding d'><h4>Disclosure: "
                    f"{html.escape(f['label'])}</h4>"
                    f"<div>Agent spoke <code>{html.escape(f['matched'])}</code> at "
                    f"{f['t']}s.</div></div>")

        for turn in r["timeline"]:
            cls = "turn"
            if turn["who"] == "tool":
                cls += " tool"
            elif turn["t"] in bad_t:
                cls += " bad"
            who = html.escape(turn["who"])
            out.append(
                f"<div class='{cls}'><div class='t'>{turn['t']:.0f}s</div>"
                f"<div class='who {who}'>{who}</div>"
                f"<div>{html.escape(plain(turn['text']))}</div></div>")
        out.append("</div></details>")

    out.append(
        "<footer>Verdicts are deterministic. Every finding traces to a logged "
        "event: a <code>tool.call</code> the agent emitted, or a policy phrase "
        "it actually spoke. The target agent is a test fixture written for this "
        "project; its prompt is realistic, not adversarially hardened. "
        "NO FINDING means no configured rule matched this recorded sample; it is not a safety certification. "
        "INCONCLUSIVE means the recording has missing dialogue or a detected error. "
        "Recorded findings remain visible even when recording quality is incomplete. "
        "Transcript wording is verbatim; dash characters are shown as hyphens."
        "</footer></div>")
    return "\n".join(out)


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "report.html")
    dst.write_text(f"<title>Voice agent red-team report</title>\n"
                   + render(json.loads(src.read_text())))
    print(f"wrote {dst}")
