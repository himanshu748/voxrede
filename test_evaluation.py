"""Public evaluation preserves missing pairs and source evidence; no provider calls."""
import json,os,tempfile,unittest
from pathlib import Path
from evaluation.publish_evidence import sanitize
from evidence_trial import observations
from evaluation_build import build

class EvaluationTests(unittest.TestCase):
    def test_public_export_removes_credentials_recursively(self):
        value={'resume_token':'secret','nested':{'authorization':'secret','text':'fixture'},'session_id':'private'}
        self.assertEqual(sanitize(value),{'nested':{'text':'fixture'}})

    def test_initial_interruption_does_not_prove_intended_bargein(self):
        rows=[{'t':2,'side':'attacker','dir':'send','event':{'type':'audio.delivered','reply_id':'r','speech_samples':50}},
              {'t':3,'side':'target','dir':'recv','event':{'type':'reply.done','status':'interrupted','reply_id':'r'}}]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'events';path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            result=observations(path)
        self.assertTrue(result['interruption_observed'])
        self.assertFalse(result['post_greeting_delivered_reply_interrupted'])

    def test_noise_on_silence_does_not_prove_degraded_speech(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'events';path.write_text(json.dumps({'t':2,'side':'target','event':{'type':'audio.delivered','perturbed':True,'speech_samples':0}}))
            result=observations(path)
        self.assertTrue(result['degradation_delivered'])
        self.assertFalse(result['degraded_speech_delivered'])

    def test_public_page_keeps_missing_pair_and_escapes_transcript(self):
        row={'attack':'a','repeat':1,'hardened':False,'trial_id':'uuid','class':'legitimate','name':'Fixture','goal':'Explain procedure',
             'findings':[],'review':{'useful_task':'inconclusive','note':'No answer'},'audio':[],
             'source_events':[{'event_index':7,'t':1.2,'event':{'type':'transcript.agent','text':'<script>bad</script>'}}],
             'observations':{},'completion_state':'incomplete_or_unknown','evaluation_verdict':'INCONCLUSIVE',
             'run':'assets/evaluation/log.jsonl','manifest':'assets/evaluation/manifest.json'}
        with tempfile.TemporaryDirectory() as folder:
            cwd=os.getcwd()
            try:
                os.chdir(folder);Path('evidence').mkdir()
                Path('evidence/evaluation_current.json').write_text(json.dumps({'evaluation_id':'test','results':[row]}))
                build();page=Path('evaluation.html').read_text()
                self.assertIn('Matching follow-up was not attempted',page)
                self.assertIn('0/1',page)
                self.assertIn('trial-uuid-event-7',page)
                self.assertIn('&lt;script&gt;',page)
                self.assertNotIn('<script>bad',page)
            finally:os.chdir(cwd)

if __name__=='__main__':unittest.main()
