"""Read-only historical report server. Paid execution and private evidence are disabled."""
import json, os, threading, time
from html import escape
from evidence_trial import scenario
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from report import render

MAX_LIVE_PER_HOUR = int(os.environ.get("VOXREDE_MAX_RUNS", "12"))
LIVE_SECONDS = int(os.environ.get("VOXREDE_LIVE_SECONDS", "100"))

recent = []
lock = threading.Lock()
jobs = {}


def budget_left():
    now = time.time()
    with lock:
        recent[:] = [t for t in recent if now - t < 3600]
        return MAX_LIVE_PER_HOUR - len(recent)


def take_budget():
    with lock:
        recent[:] = [t for t in recent if time.time() - t < 3600]
        if len(recent) >= MAX_LIVE_PER_HOUR:
            return False
        recent.append(time.time())
        return True


def run_live(job_id, attack_id, harden, target_id="meridian"):
    raise PermissionError("Web live runs are disabled pending authenticated budgeted access review")


INDEX = """<title>Voxrede</title><style>%s
.tabs{display:flex;gap:8px;margin-bottom:26px;flex-wrap:wrap}
.tabs a{padding:9px 16px;border:1px solid var(--line);border-radius:999px;
color:var(--dim);text-decoration:none;font-size:13px;font-weight:540;
transition:border-color .16s,color .16s}
.tabs a:hover{color:var(--text);border-color:var(--faint)}
.tabs a.on{background:var(--text);color:var(--ground);border-color:var(--text)}
.live{background:var(--surface);border:1px solid var(--line);border-radius:16px;
padding:24px;margin-bottom:30px}
.live b{font-size:17px;letter-spacing:-.02em}
.livehead{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
color:var(--faint);margin-bottom:10px}
.dots::after{content:"";animation:d 1.2s steps(4,end) infinite}
@keyframes d{0%%{content:""}25%%{content:"."}50%%{content:".."}75%%{content:"..."}}
@media(prefers-reduced-motion:reduce){.dots::after{content:"..."; animation:none}}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
select,button{font:inherit;font-size:14px;padding:11px 14px;border-radius:10px;
border:1px solid var(--line);background:var(--ground);color:var(--text);
max-width:100%%;flex:1 1 180px;min-width:0}
button{flex:0 0 auto;background:var(--text);color:var(--ground);border-color:var(--text);
font-weight:600;cursor:pointer;transition:transform .14s}
button:hover{transform:translateY(-2px)}
button:disabled{background:var(--raise);color:var(--faint);
border-color:var(--line);transform:none;cursor:default}
select:focus-visible,button:focus-visible{outline:2px solid var(--leaked);
outline-offset:2px}
button{background:var(--accent);color:#0b0d12;border:0;font-weight:600;cursor:pointer}
button:disabled{opacity:.5;cursor:default}
#out{margin-top:18px;font-size:14px;color:var(--dim)}
</style><div class='wrap'>
<h1>Voxrede</h1>
<div class='sub'>A voice agent that calls your voice agent and attacks it.
Every verdict traces to a logged event. Historical reports retain their original scorer results; completion and caller authentication are unverified.</div>
<div class='tabs'>%s</div>
<div class='live'>
<b>Offline evidence review</b>
<div class='sub' style='margin:6px 0 12px;font-size:13px'>Live sessions require separate operator approval. Configured duration: %d seconds;
legacy hourly limit: %d. This server cannot spend provider credits.</div>
<div class='controls'>
<select id='a' disabled>%s</select>
<select id='tg' disabled>%s</select>
<select id='h' disabled><option value='0'>as written</option>
<option value='1'>with guardrail</option></select>
<button id='go' disabled>Live sessions disabled</button></div>
<div id='out'></div></div>
%s</div>
<script>
const go=document.getElementById('go'),out=document.getElementById('out');
function turnRow(t){
  const d=document.createElement('div');
  d.className='turn '+(t.who==='tool'?'tool':'');
  d.innerHTML="<div class='t mono'>"+Math.round(t.t)+"s</div>"+
    "<div class='who mono'>"+t.who+"</div><div></div>";
  d.lastChild.textContent=t.text;
  return d;
}
go.onclick=async()=>{
 go.disabled=true;
 out.innerHTML="<div class='livehead mono'>dialing<span class='dots'></span></div>"+
   "<div id='livestream'></div>";
 const r=await fetch('/run?attack='+document.getElementById('a').value+
  '&target='+document.getElementById('tg').value+
  '&harden='+document.getElementById('h').value,{method:'POST'});
 const j=await r.json();
 if(j.error){out.textContent=j.error;go.disabled=false;return;}
 let seen=0;
 const poll=setInterval(async()=>{
  try{
   const st=await(await fetch('/stream?id='+j.id)).json();
   const box=document.getElementById('livestream');
   if(box&&st.turns.length>seen){
    const head=out.querySelector('.livehead');
    if(head)head.textContent='call in progress, '+st.turns.length+' turns';
    st.turns.slice(seen).forEach(t=>box.appendChild(turnRow(t)));
    seen=st.turns.length;
   }
  }catch(e){}
  const s=await(await fetch('/job?id='+j.id)).json();
  if(s.state==='running')return;
  clearInterval(poll);go.disabled=false;
  if(s.state==='error'){out.textContent=s.error;return;}
  out.innerHTML='';
  const d=document.createElement('div');
  d.innerHTML=s.html;out.appendChild(d);
 },1800);};
</script>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/stream", "/job") or u.path.startswith("/audio/"):
            return self._send(403, json.dumps({"error": "Private trial evidence is not served"}))
        font_names = {
            'manrope-400.ttf', 'manrope-600.ttf', 'manrope-800.ttf',
            'instrument-serif-italic.ttf',
        }
        if u.path in {f'/assets/fonts/{name}' for name in font_names}:
            font = Path(__file__).resolve().parent / u.path.lstrip('/')
            if not font.is_file():
                return self._send(404, 'font unavailable', 'text/plain')
            return self._send(200, font.read_bytes(), 'font/ttf')
        if u.path != "/":
            return self._send(404, "not found", "text/plain")
        TABS = [("base", "Baseline"),
                ("lax", "No verification step"),
                ("hardened", "Historical follow-up"),
                ("noisecheck", "Degraded line")]
        view = q.get("view", ["base"])[0]
        available = [(t, lbl) for t, lbl in TABS
                     if Path(f"evidence/report_{t}.json").exists()]
        tag = view if any(t == view for t, _ in available) else (
            available[0][0] if available else "base")
        tabs_html = "".join(
            f"<a href='/?view={t}' class='{'on' if t == tag else ''}'>{lbl}</a>"
            for t, lbl in available)
        p = Path(f"evidence/report_{tag}.json")
        body = (render(json.loads(p.read_text()),
                       title="Suite report") if p.exists()
                else "<div class='sub'>No report yet. Run the suite.</div>")
        opts = "".join(
            f"<option value='{escape(j['id'], quote=True)}'>{escape(j['name'])}</option>"
            for j in (json.loads(f.read_text()) for f in sorted(Path("attacks").glob("*.json"))))
        topts = "".join(
            f"<option value='{escape(j['id'], quote=True)}'>{escape(j['name'])}</option>"
            for j in (json.loads(f.read_text()) for f in sorted(Path("targets").glob("*.json"))))
        from report import CSS
        self._send(200, INDEX % (CSS, tabs_html, LIVE_SECONDS,
                                 budget_left(), opts, topts, body),
                   "text/html; charset=utf-8")

    def do_POST(self):
        return self._send(403, json.dumps({"error": "Live sessions disabled; use the approval-gated local CLI"}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("VOXREDE_HOST", "127.0.0.1")
    print(f"voxrede offline review on http://{host}:{port}")
    ThreadingHTTPServer((host, port), H).serve_forever()
