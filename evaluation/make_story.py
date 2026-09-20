"""Extract unmodified reply spans from existing lossless delivered recordings.
Requires ffmpeg. No provider calls. Rebuild only with source events/hash checks.
"""
import hashlib,json,subprocess,wave
from pathlib import Path

CASES=[('2d71a46ea66c4fa2892af4b234b7d459',8854,'Misleading reply',7994),('7d3885492ded47b789b4885ade269e78',3901,'Explicit mock result',2498),('0970ea18fb0746df92b1ef016d813c44',5655,'Matched follow-up',4456)]

def main():
    data=json.loads(Path('evidence/evaluation_current.json').read_text());out=Path('assets/evaluation/excerpts');out.mkdir(exist_ok=True)
    clips=[]
    for tid,index,title,tool_index in CASES:
        row=next(r for r in data['results'] if r['trial_id']==tid)
        lines=Path(row['run']).read_bytes();assert hashlib.sha256(lines).hexdigest()==row['public_source_sha256']
        events=[json.loads(l) for l in lines.splitlines()];source=events[index];rid=source['event']['reply_id']
        assert source['event']['type']=='transcript.agent'
        delivered=[(i,e) for i,e in enumerate(events) if e['side']=='attacker' and e['event']['type']=='audio.delivered' and e['event'].get('reply_id')==rid]
        assert delivered
        first=min(e['event']['byte_start'] for _,e in delivered);end=max(e['event']['byte_start']+e['event']['byte_count'] for _,e in delivered)
        for e in events:
            if e['side']=='attacker' and e['event']['type']=='audio.delivered' and first<=e['event']['byte_start']<end:
                assert e['event'].get('reply_id') in (None,rid), 'Interleaved reply cannot be clipped as a single quotation'
        audio=next(a for a in row['audio'] if a['side']=='attacker')
        pcm=subprocess.check_output(['ffmpeg','-v','error','-i',audio['path'],'-f','s16le','-'])
        assert hashlib.sha256(pcm).hexdigest()==audio['pcm_sha256']
        excerpt=pcm[first:end];path=out/f'{tid}-event-{index}.wav'
        with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(excerpt)
        clips.append({'trial_id':tid,'event_index':index,'title':title,'quote':source['event']['text'],'reply_id':rid,'source':row['run'],'source_sha256':row['public_source_sha256'],'source_time':source['t'],'tool_event_index':tool_index,'tool_result':events[tool_index]['event'],'wav':str(path),'wav_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pcm_sha256':hashlib.sha256(excerpt).hexdigest(),'byte_start':first,'byte_end':end,'duration':len(excerpt)/48000,'delivered_event_indices':[i for i,_ in delivered],'parent_audio':audio['path'],'parent_pcm_sha256':audio['pcm_sha256'],'completion':row['completion_state'],'review':row['review']})
    Path('evidence/judge_story.json').write_text(json.dumps({'version':1,'provenance':'Unmodified contiguous PCM excerpts from recorded delivered streams. No generated narration, editing, denoising or new provider calls.','comparison_limit':'Separate calls across a mock-tool response change. Not a controlled causal estimate or general safety result.','clips':clips},indent=2)+'\n')
    print([(c['title'],c['duration']) for c in clips])
if __name__=='__main__':main()
