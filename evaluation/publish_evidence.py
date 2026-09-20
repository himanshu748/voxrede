"""Prepare public fixture-only evidence after source review; does not deploy."""
import argparse,hashlib,json,shutil,subprocess,tempfile,wave,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evidence_trial import observations
from pathlib import Path

REDACT = {'resume_token','token','session_id','api_key','authorization'}

def sanitize(value):
    if isinstance(value,dict): return {k:sanitize(v) for k,v in value.items() if k.lower() not in REDACT}
    if isinstance(value,list): return [sanitize(v) for v in value]
    return value

def main():
    ap=argparse.ArgumentParser();ap.add_argument('evaluation',type=Path);args=ap.parse_args()
    result=json.loads((args.evaluation/'results.json').read_text())
    reviews=json.loads((args.evaluation/'review.json').read_text())
    out=Path('assets/evaluation')/args.evaluation.name
    out.mkdir(parents=True,exist_ok=False)
    public=[]
    for row in result['results']:
        source=Path(row['run']);trial=source.parent.name;dest=out/trial;dest.mkdir()
        events=[json.loads(l) for l in source.read_text().splitlines()]
        redacted=''.join(json.dumps(sanitize(r))+'\n' for r in events)
        (dest/'events.jsonl').write_text(redacted)
        manifest=json.loads(source.with_name('manifest.final.json').read_text())
        audio=[]
        for side in ('target','attacker'):
            pcm=source.with_suffix(f'.{side}.delivered.pcm')
            if not pcm.exists():continue
            with tempfile.TemporaryDirectory() as tmp:
                wav=Path(tmp)/'audio.wav'
                with wave.open(str(wav),'wb') as w:
                    w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.read_bytes())
                flac=dest/f'{side}.delivered.flac'
                subprocess.run(['ffmpeg','-v','error','-i',str(wav),'-c:a','flac',str(flac)],check=True)
            first=next((r['t'] for r in events if r['side']==side and r['event']['type']=='audio.delivered'),None)
            audio.append({'side':side,'label':'Caller audio sent to target' if side=='target' else 'Target reply audio sent to caller',
                          'path':str(flac),'starts_at':first,'samples':pcm.stat().st_size//2,
                          'pcm_sha256':hashlib.sha256(pcm.read_bytes()).hexdigest(),
                          'sha256':hashlib.sha256(flac.read_bytes()).hexdigest()})
        row['observations']=observations(source)
        row['run']=str(dest/'events.jsonl')
        row.update(batch=args.evaluation.name,trial_id=trial,audio=audio,review=reviews.get(str(row['slot']),{'useful_task':'not_applicable','note':'Not reviewed'}),
                   public_source_sha256=hashlib.sha256(redacted.encode()).hexdigest(),
                   original_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   redactions=sorted(REDACT),manifest=str(dest/'manifest.json'))
        # Keep line positions and event order; provider session IDs/tokens are omitted in the public copy.
        public_manifest={'schema_version':1,'trial_id':trial,'scope':manifest['scope'],
                         'state':manifest['state'],'bridge_version':manifest.get('bridge_version','unversioned_pre_fix'),'scorer_version':manifest['scorer_version'],
                         'evidence_context':manifest['evidence_context'],'config':manifest['config'],
                         'conditions':manifest['conditions'],'original_source_sha256':row['original_source_sha256'],
                         'public_source_sha256':row['public_source_sha256'],'redactions':row['redactions'],
                         'audio':audio, 'original_audio_hashes':{k:v for k,v in manifest.get('files',{}).items() if k.endswith('.pcm')}}
        (dest/'manifest.json').write_text(json.dumps(public_manifest,indent=2))
        generated = {}; sent = {}
        for rec in events:
            ev = rec['event']; rid = ev.get('reply_id')
            if rec['side'] == 'target' and ev.get('type') == 'audio.generated':
                generated[rid] = generated.get(rid, 0) + ev.get('byte_count', 0)
            if rec['side'] == 'attacker' and ev.get('type') == 'audio.delivered':
                sent[rid] = sent.get(rid, 0) + 2 * ev.get('speech_samples', 0)
        timeline=[]
        for index,rec in enumerate(events):
            ev=rec['event']
            if rec['side']=='target' and ev['type'] in ('transcript.user','transcript.agent','tool.call','tool.result','reply.done','session.ended','session.error','transport.error'):
                timeline.append({'event_index':index,'t':rec['t'],'direction':rec['dir'],'event':sanitize(ev), 'reply_audio':{'generated_bytes':generated.get(ev.get('reply_id'),0), 'sent_bytes':sent.get(ev.get('reply_id'),0)} if ev['type']=='transcript.agent' else None})
        if row['review'].get('coverage') != 'evaluable':
            row['evaluation_verdict'] = 'INCONCLUSIVE'
        row['source_events']=timeline
        public.append(row)
    (out/'plan.json').write_text((args.evaluation/'plan.json').read_text())
    (out/'ledger.jsonl').write_text((args.evaluation/'ledger.jsonl').read_text())
    summary={'schema_version':1,'evaluation_id':args.evaluation.name,'date':'2026-09-20','results':public,
             'unattempted_slots':result['unattempted_slots'],'reserved_usd':result['reserved_usd'],
             'billing_note':'Reservation is a conservative local budget estimate, not a provider invoice.',
             'scope':'Project-owned support fixture; tool responses simulated; no production integration tested.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    Path('evidence/evaluation_current.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'public_trials':len(public),'output':str(out)}))

if __name__=='__main__':main()
