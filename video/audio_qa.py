"""Transcribe the produced narration for spoken-number review and timed captions.
One bounded Whisper request; total production transcription allowance $0.20.
Cumulative requested duration is limited to 2,000 seconds at $0.006/minute.
"""
import json
import math
import os
from pathlib import Path
import subprocess
import httpx
from dotenv import load_dotenv

root=Path('artifacts/episode-01').resolve(); out=root/'audio-qa-v3';out.mkdir(exist_ok=True)
parts=[]
for i,p in enumerate(sorted(root.glob('voice-*.wav'))):
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
    duration=math.ceil((duration+.65)*24)/24
    q=out/f'part-{i:02}.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(p),'-af','apad','-t',str(duration),'-ar','24000','-ac','1',str(q)],check=True)
    parts.append(q)
listing=out/'parts.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in parts))
audio=out/'narration.mp3'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-b:a','64k',str(audio)],check=True)
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(audio)]))
prior_seconds=sum(json.loads(p.read_text())['duration'] for p in root.glob('audio-qa*/request.json') if p.parent != out)
if duration>900 or prior_seconds+duration>2000:
    raise RuntimeError('Narration exceeds the cumulative QA budget duration')
transcript=out/'transcript.json';receipt=out/'request.json'
if not transcript.exists():
    if receipt.exists():raise RuntimeError('Prior request uncertain; no automatic retry')
    receipt.write_text(json.dumps(dict(model='whisper-1',reserved_allowance_usd=duration*.006/60,duration=duration,status='reserved')))
    load_dotenv(Path.cwd()/'.env')
    with audio.open('rb') as f, httpx.Client(timeout=120) as client:
        r=client.post('https://api.openai.com/v1/audio/transcriptions',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},
                      data={'model':'whisper-1','response_format':'verbose_json','timestamp_granularities[]':'word','language':'en'},
                      files={'file':('narration.mp3',f,'audio/mpeg')})
    if r.status_code!=200:raise RuntimeError(f'Transcription HTTP {r.status_code}')
    transcript.write_text(json.dumps(r.json(),indent=2)+'\n')
    receipt.write_text(json.dumps(dict(model='whisper-1',reserved_allowance_usd=duration*.006/60,duration=duration,status='received',request_id=r.headers.get('x-request-id'))))
d=json.loads(transcript.read_text());(out/'transcript.txt').write_text(d['text'])
print(json.dumps({'duration':duration,'words':len(d.get('words',[])),'transcript':str(transcript)}))
