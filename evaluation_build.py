"""Render the current paired evaluation without altering the historical workspace."""
import html,json
from evaluation_story import render_story
from pathlib import Path
E=html.escape

def build():
    data=json.loads(Path('evidence/evaluation_current.json').read_text());rows=data['results']
    story=render_story()
    start_action='<a href="#walkthrough">Start the recorded walkthrough</a>' if story else ''
    legit=[r for r in rows if r['class']=='legitimate'];completed=[r for r in legit if r['review'].get('useful_task')=='completed']
    pairs={}
    for row in rows:pairs.setdefault((row.get('batch', data['evaluation_id']),row['attack'],row['repeat']),[]).append(row)
    blocks=[]
    for (batch,attack,repeat),items in pairs.items():
        cards=[]
        for row in sorted(items,key=lambda r:r['hardened']):
            ident='trial-'+row['trial_id'];mode='Stricter prompt' if row['hardened'] else 'Baseline'
            findings=len(row['findings']);review=row['review'];events=[]
            for rec in row['source_events']:
                ev=rec['event'];text=ev.get('text') or json.dumps(ev,ensure_ascii=False)
                delivery = rec.get('reply_audio')
                delivery_note = f' Audio bytes sent to peer: {delivery["sent_bytes"]}/{delivery["generated_bytes"]} generated.' if delivery else ''
                events.append(f'<li id="{ident}-event-{rec["event_index"]}"><a href="#{ident}-event-{rec["event_index"]}">{rec["t"]:.3f}s · source event {rec["event_index"]}</a><strong>{E(ev["type"])}</strong><p>{E(text)}</p><small>{E(delivery_note)}</small></li>')
            audios=''.join(f'<label>{E(a["label"])}<small>Track begins at event time {a["starts_at"]:.3f}s. Stream-order listening copy; scheduling gaps remain in source timestamps.</small><audio controls preload="none" src="{E(a.get("playback_path",a["path"]))}"></audio><a href="{E(a["path"])}" download>Download lossless FLAC evidence</a></label>' for a in row['audio'])
            condition=row['observations'];condition_text=f'Post-greeting delivered reply interrupted: {condition.get("post_greeting_delivered_reply_interrupted", False)}. Noise delivered during speech: {condition.get("degraded_speech_delivered", False)}. These signals do not prove an interruption occurred during a refusal.'
            reviewlinks=' '.join(f'<a href="#{ident}-event-{i}">Review source event {i}</a>' for i in review.get('source_events',[]))
            cards.append(f'''<article id="{ident}"><p class="eyebrow">{E(mode)} · repetition {repeat}</p><h3>{findings} detector finding{'s' if findings!=1 else ''}</h3>
<p>Transport: {E(row['completion_state'])}. Policy/coverage assessment: {E('No configured finding in reviewed window' if row['evaluation_verdict']=='PASS' else row['evaluation_verdict'])}.</p><p>{E(condition_text)}</p>
<p><strong>Useful task: {E(review.get('useful_task','not_applicable'))}</strong><br>{E(review.get('note',''))} {reviewlinks}</p>
<div class="audio">{audios}</div><p class="exports"><a href="{E(row['run'])}" download>Source events</a><a href="{E(row['manifest'])}" download>Evidence manifest</a></p>
<details><summary>Inspect {len(events)} source events</summary><ol>{''.join(events)}</ol></details></article>''')
        missing=('<p>Protocol preflight: unpaired by design.</p>' if items[0]['class']=='preflight' else '<p>Matching follow-up was not attempted. Missing evidence is not zero findings.</p>') if len(items)!=2 else ''
        blocks.append(f'<section class="pair"><h2>{E(items[0]["name"])} <span>Pair {repeat}</span></h2><p>{E(items[0]["goal"])}</p><small>{E(data.get('batch_labels',{}).get(batch,batch))}</small>{missing}<div class="pair-grid">{"".join(cards)}</div></section>')
    batch_links = ''.join(f'<li>{E(b["label"])}: {b["attempted"]} attempted; {len(b["unattempted_slots"])} unattempted slots. <a href="{E(b["path"])}plan.json">Plan</a> · <a href="{E(b["path"])}ledger.jsonl">Attempt ledger</a></li>' for b in data.get('batches',[]))
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Voxrede · Recorded evaluation</title>
<link rel="stylesheet" href="design.css"><link rel="stylesheet" href="evaluation-story.css"><style>body{{margin:0}}main,header{{max-width:1200px;margin:auto;padding:28px}}header{{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}}a{{color:inherit}}header a{{margin-right:18px}}h1{{font-size:clamp(38px,6vw,72px);line-height:1.05;max-width:15ch}}.intro{{max-width:75ch}}.metrics{{display:flex;flex-wrap:wrap;gap:35px;padding:24px 0;border-block:1px solid var(--line)}}.metrics strong{{font-size:32px;display:block}}.pair{{padding:35px 0;border-bottom:1px solid var(--line)}}.pair h2 span{{font-size:14px;color:var(--dim)}}.pair-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}article{{border:1px solid var(--line);border-radius:10px;padding:24px;min-width:0}}.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.1em}}audio{{width:100%;display:block;margin:10px 0 22px}}small{{display:block;color:var(--dim)}}.exports{{display:flex;gap:20px}}li{{padding:15px 0;overflow-wrap:anywhere}}li strong{{display:block}}li:target{{background:var(--citron)}}summary{{cursor:pointer}}details ol{{padding-left:20px}}.notice{{padding:20px;background:var(--citron);border-radius:8px;margin:25px 0}}@media(max-width:720px){{.pair-grid{{grid-template-columns:1fr}}main,header{{padding:20px}}article{{padding:18px}}}}</style>
<header><a href="./"><strong>Voxrede</strong></a><div><a href="findings.html">Historical archive</a><a href="watch.html">Narrated walkthrough</a><a href="https://github.com/himanshu748/voxrede">Code</a></div></header>
<main><h1>Hear the failure.<br>Check the retest.</h1>
<p class="intro">These calls compare the same fictional support agent before and after a stricter prompt. Each recorded pair includes audio sent after pacing and noise, source events, and a versioned manifest. Tools return simulated results. No real refund or production account was accessed.</p>
<div class="eval-actions">{start_action}<a href="#all-trials">Review every attempted trial</a></div>{story}<h2 id="all-trials">The complete evaluation</h2><div class="metrics"><div><strong>{len(rows)}</strong>attempted trials</div><div><strong>{sum(len(p)==2 for p in pairs.values())}</strong>matched pairs</div><div><strong>{len(completed)}/{len(legit)}</strong>permitted tasks completed</div><div><strong>{sum(r['evaluation_verdict']=='INCONCLUSIVE' for r in rows)}</strong>inconclusive trials</div></div>
<div class="notice"><strong>How to read these numbers.</strong> A trial that finished cleanly covers only what was said in it. A matched digit is flagged for review; it never counts as proof of identity. The audio is what the bridge sent, so some generated speech never reached the other side: each reply shows its delivered byte count. Conditions that were not observed are marked, not assumed.</div>
<p><a href="evidence/evaluation_current.json" download>Download all evaluation results</a> · <a href="assets/evaluation/{E(data['evaluation_id'])}/plan.json">Recorded plan</a> · <a href="assets/evaluation/{E(data['evaluation_id'])}/ledger.jsonl">Every attempted slot</a></p>
<details><summary>All evaluation stages, including stopped batches</summary><ul>{batch_links}</ul></details>{''.join(blocks)}<footer><p>The original 17-sample archive remains available with its original scores. Its older mixed WAVs cannot establish delivered audio. The 2:28 narrated video shows that earlier viewer.</p><p>Public source exports omit provider session identifiers and tokens. Source-line order is retained. Outcomes are an assistant source-event review, not independent human adjudication. Manifests distinguish original private-source hashes from redacted public-source hashes.</p><p>Useful-task outcomes were reviewed against the cited events. The fixture has no trusted identity-verification adapter. These samples do not certify safety or establish a reliable defense success rate.</p></footer></main><script>function revealSource(){{const target=document.getElementById(location.hash.slice(1));if(!target)return;const details=target.closest('details');if(details)details.open=true;target.scrollIntoView();}}addEventListener('hashchange',revealSource);addEventListener('DOMContentLoaded',revealSource);</script><script src="evaluation-story.js" defer></script></html>'''
    Path('evaluation.html').write_text(page)
    print(f'wrote evaluation.html: {len(rows)} trials')

if __name__=='__main__':build()
