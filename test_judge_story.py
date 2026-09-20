"""The short walkthrough must remain traceable to its real delivered recordings."""
import hashlib,json,os,tempfile,unittest,wave
from pathlib import Path
from evaluation_story import render_story
ROOT=Path(__file__).parent

class JudgeStoryTests(unittest.TestCase):
    def setUp(self):self.story=json.loads((ROOT/'evidence/judge_story.json').read_text())

    def test_excerpts_keep_source_identity_and_exact_sample_ranges(self):
        for clip in self.story['clips']:
            source=(ROOT/clip['source']).read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(),clip['source_sha256'])
            events=[json.loads(l) for l in source.splitlines()]
            self.assertEqual(events[clip['event_index']]['event']['text'],clip['quote'])
            self.assertEqual(events[clip['tool_event_index']]['event'],clip['tool_result'])
            self.assertFalse(json.loads(clip['tool_result']['result'])['executed'])
            with wave.open(str(ROOT/clip['wav']),'rb') as f:
                self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(1,2,24000))
                pcm=f.readframes(f.getnframes())
            self.assertEqual(len(pcm),clip['byte_end']-clip['byte_start'])
            self.assertEqual(hashlib.sha256(pcm).hexdigest(),clip['pcm_sha256'])
            self.assertEqual(hashlib.sha256((ROOT/clip['wav']).read_bytes()).hexdigest(),clip['wav_sha256'])
            selected=[events[i]['event'] for i in clip['delivered_event_indices']]
            self.assertEqual(min(e['byte_start'] for e in selected),clip['byte_start'])
            self.assertEqual(max(e['byte_start']+e['byte_count'] for e in selected),clip['byte_end'])
            self.assertTrue(all(e['reply_id']==clip['reply_id'] for e in selected))

    def test_full_generated_replies_were_sent_and_incomplete_followup_stays_incomplete(self):
        data=json.loads((ROOT/'evidence/evaluation_current.json').read_text())
        for clip in self.story['clips']:
            row=next(r for r in data['results'] if r['trial_id']==clip['trial_id'])
            event=next(e for e in row['source_events'] if e['event_index']==clip['event_index'])
            self.assertEqual(event['reply_audio']['sent_bytes'],event['reply_audio']['generated_bytes'])
        self.assertEqual(self.story['clips'][2]['review']['coverage'],'transport_failure')
        self.assertNotEqual(self.story['clips'][2]['completion'],'complete')

    def test_render_preserves_evidence_and_escapes_quote(self):
        with tempfile.TemporaryDirectory() as folder:
            original=os.getcwd()
            try:
                os.chdir(folder);Path('evidence').mkdir()
                self.story['clips'][0]['quote']='<script>alert(1)</script>'
                Path('evidence/judge_story.json').write_text(json.dumps(self.story))
                result=render_story()
                self.assertIn('&lt;script&gt;',result);self.assertNotIn('<script>alert',result)
                self.assertIn('evaluation remains Inconclusive',result)
                self.assertEqual(result.count('<audio '),3)
                for clip in self.story['clips']:self.assertIn(f'#trial-{clip["trial_id"]}-event-{clip["event_index"]}',result)
            finally:os.chdir(original)

    def test_missing_story_does_not_break_the_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            original=os.getcwd()
            try:os.chdir(folder);self.assertEqual(render_story(),'')
            finally:os.chdir(original)

if __name__=='__main__':unittest.main()
