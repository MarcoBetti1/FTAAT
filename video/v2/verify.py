"""Verify the final encoded film and reconcile this edition's provider budgets."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from decimal import Decimal
from .speech import ROOT
from .art import font

def main():
    video=ROOT/'GPT-Learning-01-v2.mp4';timeline=json.loads((ROOT/'timeline.json').read_text());duration=sum(s['duration'] for s in timeline)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'])==(1920,1080,'30/1','h264')
    assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
    assert abs(float(probe['format']['duration'])-duration)<.1
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
    summary=loudness.rsplit('Summary:',1)[-1];(ROOT/'loudness.txt').write_text(summary)
    integrated=float(re.search(r'I:\s*([-\d.]+) LUFS',summary).group(1));peak=float(re.search(r'Peak:\s*([-\d.]+) dBFS',summary).group(1))
    assert -17<integrated<-15 and peak<-.5,(integrated,peak)
    cues=json.loads((ROOT/'captions.json').read_text());last=0
    for c in cues:
        assert last-.01<=c['start']<c['end']<=duration+.02
        assert len(c['lines'])<=2 and all(font(37).getlength(line)<=1591 for line in c['lines']);last=c['end']
    review=ROOT/'export-review';review.mkdir(exist_ok=True)
    for s in timeline:
        at=s['start']+.7*s['duration'];subprocess.run(['ffmpeg','-y','-v','error','-ss',str(at),'-i',str(video),'-frames:v','1',str(review/(s['id']+'.png'))],check=True)
    costs={};runs=[]
    for p in sorted(Path('results').glob('v2-*/events.jsonl')):
        rows=[json.loads(l) for l in p.read_text().splitlines()];result={r['request_key']:r for r in rows if r['event']=='result'};reserved={r['request_key']:r for r in rows if r['event']=='reserved'}
        assert set(result)==set(reserved),'Unsettled request budget'
        for r in result.values():costs[r['provider']]=costs.get(r['provider'],Decimal(0))+Decimal(r['cost_upper_usd'])
        runs.append(dict(name=p.parent.name,responses=len(result),cost_upper_usd=str(sum((Decimal(r['cost_upper_usd']) for r in result.values()),Decimal(0)))))
    speech=sum((Decimal(str(json.loads(p.read_text())['reserved_allowance_usd'])) for p in (ROOT/'speech-cache').glob('*.json')),Decimal(0))
    qa=sum((Decimal(str(json.loads(p.read_text())['reserved_allowance_usd'])) for p in ROOT.glob('audio-qa*/**/request.json')),Decimal(0))
    assert costs['openai']+speech+qa<=20 and costs['anthropic']<=5
    result=dict(status='passed',width=1920,height=1080,fps=30,duration_seconds=duration,bytes=video.stat().st_size,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),full_decode='passed',caption_cues=len(cues),integrated_lufs=integrated,true_peak_dbfs=peak,audio='AAC stereo 48 kHz',runs=runs,openai_experiment_cost_upper_usd=str(costs['openai']),anthropic_experiment_cost_upper_usd=str(costs['anthropic']),speech_reserved_usd=str(speech),qa_reserved_usd=str(qa),openai_total_bound_including_production_reservations=str(costs['openai']+speech+qa),provider_caps={'openai':20,'anthropic':5},cost_note='Experiment bounds and production reservations are not provider invoices.',visual_review='Exported frames are generated for separate human/model inspection.',spoken_review='ASR alignment and spoken numbers are reviewed separately; see spoken-review.json.')
    (ROOT/'production-audit.json').write_text(json.dumps(result,indent=2)+'\n');Path('docs/episodes/01-v2/production-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
