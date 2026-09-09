"""Original synthesized sound cues, consistent dialogue, bounded transcription QA."""
import argparse
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import wave
import httpx
import numpy as np
from dotenv import load_dotenv
from .art import wrap
from .speech import ROOT

RATE=48000

def writewav(p,data):
    with wave.open(str(p),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE)
        if data.ndim==1:data=np.column_stack([data,data])
        w.writeframes((np.clip(data,-.999,.999)*32767).astype('<i2').tobytes())

def cue(kind,seconds=.45,freq=650):
    t=np.arange(round(seconds*RATE))/RATE;rng=np.random.default_rng(51)
    if kind=='paper':return .05*rng.normal(size=len(t))*np.exp(-t*14)*(1+.4*np.sin(2*np.pi*70*t))
    if kind=='stamp':return .12*np.sin(2*np.pi*95*t)*np.exp(-t*30)+.025*rng.normal(size=len(t))*np.exp(-t*60)
    if kind=='bell':return .085*(np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*freq*2.4*t))*np.exp(-t*6)
    if kind=='plop':return .09*np.sin(2*np.pi*(420*t-240*t*t))*np.exp(-t*9)
    return np.zeros_like(t)

def produce(timeline,stem=''):
    total=sum(s['duration'] for s in timeline);n=round(total*RATE);dialogue=np.zeros(n,dtype=np.float32);fx=np.zeros(n,dtype=np.float32)
    events=[]
    def add(kind,at,seconds=.45,freq=650):
        a=cue(kind,seconds,freq);i=round(at*RATE);end=min(n,i+len(a))
        if i<0 or i>=n:return
        fx[i:end]+=a[:end-i];events.append(dict(kind=kind,at=at,duration=seconds))
    for s in timeline:
        start=s['start'];path=ROOT/(s['id']+'.wav')
        if s['narration']:
            raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-af','loudnorm=I=-18:TP=-3:LRA=7','-ar',str(RATE),'-ac','1','-f','f32le','-'])
            a=np.frombuffer(raw,dtype='<f4');i=round((start+s['voice_offset'])*RATE);end=min(n,i+len(a));dialogue[i:end]+=a[:end-i]
        add('paper',start+.05,.22)
        if s['kind']=='avalanche':
            for j in range(22):add('paper',start+.25+j*.13,.35)
        if s['kind']=='warmup':add('bell',start+7,.8,880)
        if s['kind']=='printer':
            for j in range(10):add('paper',start+.3+j*.22,.16)
            add('stamp',start+s['duration']*.5,.3)
        if s['kind']=='primary':add('stamp',start+3.5,.3)
        if s['voice']=='onyx':add('plop',start+s['voice_offset']+s['speech_duration']+.12,.6)
        if s['kind'] in ('title','end','credits'):
            # Four original pizzicato-like notes; no copyrighted melody or samples.
            for j,f in enumerate([392,523.251,493.883,329.628]):add('bell',start+.15+j*.32,.75,f)
    writewav(ROOT/(stem+'dialogue.wav'),dialogue)
    # Slight stereo space on effects only; dialogue remains centered.
    mix=np.column_stack([dialogue+fx,dialogue+np.roll(fx,round(.012*RATE))])
    writewav(ROOT/(stem+'premix.wav'),mix)
    measured=subprocess.run(['ffmpeg','-hide_banner','-i',str(ROOT/(stem+'premix.wav')),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
    stats=json.JSONDecoder().raw_decode(measured[measured.rfind('{'):])[0];flt='loudnorm=I=-16:TP=-1.5:LRA=9:linear=true:'+':'.join(f'{a}={stats[b]}' for a,b in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/(stem+'premix.wav')),'-af',flt,'-ar',str(RATE),'-ac','2',str(ROOT/(stem+'mix.wav'))],check=True)
    (ROOT/(stem+'sound-cues.json')).write_text(json.dumps(dict(original_synthesis=True,events=events,pre_normalization=stats),indent=2)+'\n')
    return total

def transcribe(total):
    out=ROOT/'audio-qa';out.mkdir(exist_ok=True);audio=out/'dialogue.mp3';transcript=out/'transcript.json';receipt=out/'request.json'
    if transcript.exists():return json.loads(transcript.read_text())
    if receipt.exists():raise RuntimeError('Prior transcription uncertain; do not automatically retry')
    # $0.30 maximum QA reservation at Whisper's $0.006/minute planning price.
    if total>900:raise RuntimeError('Unexpectedly long film')
    prior=sum(json.loads(p.read_text())['reserved_allowance_usd'] for p in ROOT.glob('audio-qa*/**/request.json'))
    if prior+total*.006/60>.30:raise RuntimeError('QA allowance exceeded')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'dialogue.wav'),'-b:a','64k',str(audio)],check=True)
    rec=dict(model='whisper-1',duration=total,reserved_allowance_usd=total*.006/60,status='reserved');receipt.write_text(json.dumps(rec,indent=2)+'\n')
    load_dotenv(Path.cwd()/'.env')
    with audio.open('rb') as f,httpx.Client(timeout=150) as client:
        r=client.post('https://api.openai.com/v1/audio/transcriptions',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},data={'model':'whisper-1','response_format':'verbose_json','timestamp_granularities[]':'word','language':'en'},files={'file':('dialogue.mp3',f,'audio/mpeg')})
    if r.status_code!=200:raise RuntimeError(f'Whisper HTTP {r.status_code}; reservation retained')
    transcript.write_text(json.dumps(r.json(),indent=2)+'\n');rec.update(status='received',request_id=r.headers.get('x-request-id'));receipt.write_text(json.dumps(rec,indent=2)+'\n')
    (out/'transcript.txt').write_text(r.json()['text']+'\n');return r.json()

def transcribe_clips(timeline):
    """Clip-specific timing resolves ASR word spill across editorial cuts."""
    load_dotenv(Path.cwd()/'.env');merged=[]
    for s in sorted(timeline,key=lambda s:(s['id']!='19_job',s['start'])):
        if not s['narration']:continue
        wav=ROOT/(s['id']+'.wav');ident=hashlib.sha256(wav.read_bytes()).hexdigest()[:16]
        out=ROOT/'audio-qa-clips'/(s['id']+'-'+ident);out.mkdir(parents=True,exist_ok=True);receipt=out/'request.json';transcript=out/'transcript.json'
        if not transcript.exists():
            if receipt.exists():raise RuntimeError('Uncertain prior clip transcription; inspect before retrying')
            prior=sum(json.loads(p.read_text())['reserved_allowance_usd'] for p in ROOT.glob('audio-qa*/**/request.json'))
            # Reserve a full minute per short clip as a conservative planning allowance.
            if prior+.006>.300001:raise RuntimeError('Cumulative QA planning cap reached')
            rec=dict(model='whisper-1',duration=s['speech_duration'],reserved_allowance_usd=.006,status='reserved',audio_sha256=ident,shot=s['id']);receipt.write_text(json.dumps(rec,indent=2)+'\n')
            with wav.open('rb') as f,httpx.Client(timeout=100) as client:
                r=client.post('https://api.openai.com/v1/audio/transcriptions',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},data={'model':'whisper-1','response_format':'verbose_json','timestamp_granularities[]':'word','language':'en'},files={'file':(wav.name,f,'audio/wav')})
            if r.status_code!=200:raise RuntimeError(f'Clip transcription HTTP {r.status_code}; reservation retained')
            transcript.write_text(json.dumps(r.json(),indent=2)+'\n');rec.update(status='received',request_id=r.headers.get('x-request-id'));receipt.write_text(json.dumps(rec,indent=2)+'\n')
        data=json.loads(transcript.read_text());offset=s['start']+s['voice_offset']
        for w in data['words']:merged.append(dict(word=w['word'],start=offset+w['start'],end=min(offset+w['end'],s['start']+s['duration']-.02)))
        print('Aligned',s['id'],data['text'],flush=True)
    merged.sort(key=lambda w:w['start']);result=dict(words=merged,text=' '.join(w['word'] for w in merged),source='Per-clip Whisper timestamps, offset into the final editorial timeline')
    (ROOT/'audio-qa-clips/transcript.json').write_text(json.dumps(result,indent=2)+'\n');return result

def clock(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def display_script(s):
    for a,b in [('GPT four O Mini','GPT-4o Mini'),('Four O Mini','GPT-4o Mini'),('GPT four point one Mini','GPT-4.1 Mini'),('GPT five point six Luna','GPT-5.6 Luna'),('Claude Haiku four point five','Claude Haiku 4.5')]:s=s.replace(a,b)
    return s

def align(timeline,transcript):
    allcues=[];review=[];norm=lambda x:re.sub(r'[^a-z0-9]','',x.lower())
    for s in timeline:
        if not s['narration']:continue
        words=[w for w in transcript['words'] if s['start']-.05<=w['start']<s['start']+s['duration']-.05]
        expected=display_script(s['narration']).split();matcher=difflib.SequenceMatcher(None,[norm(w['word']) for w in words],[norm(x) for x in expected],autojunk=False);timed=[];changes=[]
        for kind,i,j,k,l in matcher.get_opcodes():
            if kind=='equal':timed.extend(dict(text=expected[b],start=words[a]['start'],end=words[a]['end']) for a,b in zip(range(i,j),range(k,l)))
            elif kind in ('replace','insert'):
                start=words[i]['start'] if i<len(words) else s['start']+s['voice_offset']+s['speech_duration']-.2
                end=words[j-1]['end'] if j>i else min(start+.12*(l-k),s['start']+s['duration']-.1)
                timed.extend(dict(text=expected[b],start=start+(b-k)*(end-start)/(l-k),end=start+(b-k+1)*(end-start)/(l-k)) for b in range(k,l))
                changes.append(dict(asr=' '.join(w['word'] for w in words[i:j]),script=' '.join(expected[k:l])))
            elif kind=='delete':changes.append(dict(asr=' '.join(w['word'] for w in words[i:j]),script=''))
        group=[];groups=[]
        for w in timed:
            if group and (len(' '.join(x['text'] for x in group))+len(w['text'])>92 or w['end']-group[0]['start']>4.8):groups.append(group);group=[]
            group.append(w)
            if w['text'].endswith(('.','?','!')) and len(group)>=4:groups.append(group);group=[]
        if group:groups.append(group)
        for g in groups:
            start=g[0]['start'];end=max(start+.25,g[-1]['end']+.12);lines=wrap(' '.join(w['text'] for w in g),1590,37)
            assert len(lines)<=2
            allcues.append(dict(start=start,end=min(end,s['start']+s['duration']-.02),lines=lines,shot=s['id']))
        review.append(dict(shot=s['id'],script=s['narration'],asr=' '.join(w['word'] for w in words),alignment_changes=changes))
    for a,b in zip(allcues,allcues[1:]):a['end']=min(a['end'],b['start'])
    assert all(c['start']<c['end'] for c in allcues)
    (ROOT/'captions.json').write_text(json.dumps(allcues,indent=2)+'\n')
    (ROOT/'spoken-review.json').write_text(json.dumps(review,indent=2)+'\n')
    (ROOT/'GPT-Learning-01-v2.en.srt').write_text('\n'.join(f"{i+1}\n{clock(c['start'])} --> {clock(c['end'])}\n"+'\n'.join(c['lines'])+'\n' for i,c in enumerate(allcues)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opening',action='store_true');ap.add_argument('--align-only',action='store_true');ap.add_argument('--clip-qa',action='store_true');a=ap.parse_args()
    timeline=json.loads((ROOT/('opening-timeline.json' if a.opening else 'timeline.json')).read_text())
    total=sum(s['duration'] for s in timeline) if a.align_only else produce(timeline,'opening-' if a.opening else '')
    if not a.opening:align(timeline,transcribe_clips(timeline) if a.clip_qa else transcribe(total))
    print('Audio ready:',total,'seconds',flush=True)

if __name__=='__main__':main()
