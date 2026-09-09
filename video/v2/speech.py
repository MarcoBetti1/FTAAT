"""Bounded, cached stock-voice production. No uncertain automatic retries."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import httpx
from dotenv import load_dotenv
from .story import opening

ROOT=Path('artifacts/episode-01-v2').resolve()
MODEL='gpt-4o-mini-tts-2025-12-15'
BASE=('Read only the supplied original script, in clear American English. Do not imitate any real person. '
      'A polished animated science documentary with a dry sense of humor. No music, no sound effects. ')
DIRECTIONS={
 'cedar':BASE+'Warm, curious narrator. Conversational and lightly mischievous, never a sales pitch. Brisk but clear, around 170 words per minute. Let the joke land with a small pause. Deliver result numbers distinctly. Pronounce GPT as separate letters.',
 'onyx':BASE+'You voice Pip, a weary but dignified paper clerk. Deadpan, understated, matter-of-fact office comedy. A little slower than the narrator. Do not laugh at the joke. Read the sentence naturally with quiet resignation.'}

def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))

def render(s):
    cache=ROOT/'speech-cache';cache.mkdir(parents=True,exist_ok=True)
    payload=dict(model=MODEL,voice=s['voice'],input=s['narration'],instructions=DIRECTIONS[s['voice']],response_format='wav')
    ident=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest();wav=cache/(ident+'.wav');receipt=cache/(ident+'.json')
    if not wav.exists():
        if receipt.exists():raise RuntimeError('Uncertain prior speech request; inspect receipt before any new attempt')
        # At most $2.20 in speech reservations + $0.30 QA, within $2.50 production allocation.
        reserved=sum(json.loads(p.read_text())['reserved_allowance_usd'] for p in cache.glob('*.json'))
        if reserved+.05>2.200001:raise RuntimeError('Speech planning cap reached')
        if len(s['narration'])>1100:raise ValueError('Split narration into shorter shots')
        record=dict(status='reserved',reserved_allowance_usd=.05,identity=ident,**payload)
        receipt.write_text(json.dumps(record,indent=2)+'\n');load_dotenv(Path.cwd()/'.env')
        with httpx.Client(timeout=120) as client:
            r=client.post('https://api.openai.com/v1/audio/speech',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},json=payload)
        if r.status_code!=200:raise RuntimeError(f'Speech HTTP {r.status_code}; reservation retained')
        wav.write_bytes(r.content);record.update(status='received',bytes=len(r.content),request_id=r.headers.get('x-request-id'),usage=None)
        receipt.write_text(json.dumps(record,indent=2)+'\n')
    target=ROOT/(s['id']+'.wav');target.write_bytes(wav.read_bytes())
    return target

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opening',action='store_true');a=ap.parse_args()
    scenes=opening() if a.opening else json.loads((ROOT/'screenplay.json').read_text())
    elapsed=0;timeline=[]
    for s in scenes:
        if s['narration']:
            path=render(s);speech_duration=duration(path)
        else:speech_duration=0
        length=math.ceil((speech_duration+s['tail']+.15)*30)/30
        timeline.append(s|dict(start=elapsed,duration=length,speech_duration=speech_duration,voice_offset=.15))
        elapsed+=length;print(s['id'],round(length,2),'seconds',flush=True)
    (ROOT/('opening-timeline.json' if a.opening else 'timeline.json')).write_text(json.dumps(timeline,indent=2)+'\n')
    print('Total',elapsed,flush=True)

if __name__=='__main__':main()
