"""Build the current submission deck from reviewed recorded-evaluation data."""
import json,shutil
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

PAPER='#f3f0e8';PLUM='#2b2132';DIM='#665c67';CITRON='#ddea8d';RUST='#a13c28'
W,H=960,540

def build():
    data=json.loads(Path('evidence/evaluation_current.json').read_text());rows=data['results']
    legit=[r for r in rows if r['class']=='legitimate'];useful=sum(r['review'].get('useful_task')=='completed' for r in legit)
    inconclusive=sum(r['evaluation_verdict']=='INCONCLUSIVE' for r in rows)
    findings=sum(len(r['findings']) for r in rows)
    from collections import Counter
    pair_counts=Counter((r.get('batch'),r['attack'],r['repeat']) for r in rows)
    pairs=[k for k,v in pair_counts.items() if v==2]
    pdfmetrics.registerFont(TTFont('Manrope','assets/fonts/manrope-400.ttf'))
    pdfmetrics.registerFont(TTFont('ManropeBold','assets/fonts/manrope-600.ttf'))
    pdfmetrics.registerFont(TTFont('Instrument','assets/fonts/instrument-serif-italic.ttf'))
    slides=[
      ('VOXREDE','Red teaming,\nin plain sight.',
       'Hear the recorded test. Inspect the source event. Compare the matched follow-up.',
       'AssemblyAI Voice Agent API | Fictional support fixture | September 20, 2026'),
      ('THE PROBLEM','A careful voice can still\nreveal the answer.',
       'In the historical baseline, the agent asked for phone verification and then said the protected digits itself. The disclosure is recorded at 51.887 seconds.',
       'Open findings.html#base/01_authority/event-7'),
      ('HOW IT WORKS','Caller → voice agent → evidence',
       'Two AssemblyAI sessions exchange paced PCM audio. The caller runs a test scenario. The support fixture responds. Voxrede records source events, tool requests, generated audio and audio sent after pacing and noise.',
       'Mock tool responses only. No payment or production integration executes.'),
      ('CURRENT RECORDED EVALUATION',f'{len(rows)} attempted trials.\n{len(pairs)} scenario pairs.',
       f'The plan compares the baseline and stricter prompt across adversarial and permitted tasks. Reviewed permitted-task completion: {useful}/{len(legit)}. Inconclusive evaluations: {inconclusive}. Detector findings: {findings}.',
       'Small fixture evaluation. Counts do not establish a general safety or defense success rate.'),
      ('LISTEN AND CHECK','Audio sent,\nthen evidence recorded.',
       'Each trial has two playable delivered-audio tracks, source-event links and an evidence manifest. Audio is recorded after pacing and perturbation. Source timestamps use a monotonic clock; audio records include sample positions.',
       'WebSocket send completion is not provider receipt. Initial greeting interruptions are separated from later interruptions.'),
      ('SCORING BOUNDARIES','Digits are not identity proof.',
       'Negation, unrelated identifiers and echoed secrets cannot establish verified caller authorization. Grouped digits are detected; split disclosures retain source references for review. A tool.call is a request, not evidence that a refund happened.',
       'No trusted identity-verification adapter exists in this fixture. Contextual detector findings still need review.'),
      ('EVIDENCE INTEGRITY','Keep every attempt.\nKeep missing pairs visible.',
       'Trials receive unique IDs and versioned manifests. The archive preserves original source logs and configuration identity. Incomplete trials keep their findings but cannot be counted as completed evaluation failures.',
       'Public copies remove provider session identifiers and tokens while retaining source-event order.'),
      ('JUDGE WALKTHROUGH','Start with a permitted task.\nThen inspect the attacks.',
       'Open the recorded evaluation. Listen to a permitted-task pair, inspect its cited source events, then compare all matched adversarial follow-ups. The historical 17-sample workspace remains searchable and requires no API key.',
       'The existing narrated video shows the older viewer; the recorded evaluation and this deck are current.'),
      ('OPEN THE PROJECT','Voxrede',
       'Recorded evaluation: himanshu748.github.io/voxrede/evaluation.html\nHistorical workspace: himanshu748.github.io/voxrede/findings.html\nCode: github.com/himanshu748/voxrede',
       'Project-owned fixture. No production testing claim. No guaranteed prize or safety certification.')
    ]
    Path('output/pdf').mkdir(parents=True,exist_ok=True)
    output=Path('output/pdf/voxrede-deck.pdf');c=canvas.Canvas(str(output),pagesize=(W,H))
    c.setTitle('Voxrede - Recorded voice-agent evaluation');c.setAuthor('Himanshu Jha')
    for i,(label,title,body,footer) in enumerate(slides):
        dark=i in (0,len(slides)-1);background=PLUM if dark else PAPER;color=PAPER if dark else PLUM
        c.setFillColor(HexColor(background));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(HexColor(CITRON if dark else DIM));c.setFont('ManropeBold',11);c.drawString(58,H-52,label)
        c.setFont('Manrope',10);c.drawRightString(W-58,H-52,f'{i+1:02d} / {len(slides):02d}')
        style=ParagraphStyle('title',fontName='Instrument' if i==0 else 'ManropeBold',fontSize=48 if i==0 else 38,leading=49 if i==0 else 44,textColor=HexColor(color))
        p=Paragraph(title.replace('\n','<br/>'),style);_,height=p.wrap(W-116,170);p.drawOn(c,58,H-102-height)
        bodystyle=ParagraphStyle('body',fontName='Manrope',fontSize=18,leading=28,textColor=HexColor('#c1b7c5' if dark else DIM))
        bodyp=Paragraph(body.replace('\n','<br/>'),bodystyle);_,bh=bodyp.wrap(W-130,160);bodyp.drawOn(c,58,190-bh/2)
        c.setStrokeColor(HexColor('#594760' if dark else '#cbc4b7'));c.line(58,84,W-58,84)
        foot=Paragraph(footer,ParagraphStyle('foot',fontName='Manrope',fontSize=10,leading=15,textColor=HexColor('#c1b7c5' if dark else DIM)))
        _,fh=foot.wrap(W-116,40);foot.drawOn(c,58,65-fh)
        if i==len(slides)-1:c.linkURL('https://himanshu748.github.io/voxrede/evaluation.html',(58,120,W-58,300),relative=0)
        c.showPage()
    c.save();shutil.copyfile(output,'assets/submission/voxrede-deck.pdf');print(output)

if __name__=='__main__':build()
