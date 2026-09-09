"""Create a quiet original motif and paper-like transition cues, then mix narration.
No sampled music, external recordings, or copyrighted composition is used.
"""
from pathlib import Path
import json
import math
import subprocess
import wave
import numpy as np
root=Path('artifacts/episode-01').resolve();timeline=json.loads((root/'timeline.json').read_text())
sr=48000;total=sum(s['duration'] for s in timeline);track=np.zeros((math.ceil(total*sr),2),np.float32)
rng=np.random.default_rng(1701)

def add_sound(start,signal,pan=0):
 i=round(start*sr);n=min(len(signal),len(track)-i)
 if n<=0:return
 track[i:i+n,0]+=signal[:n]*math.sqrt((1-pan)/2)
 track[i:i+n,1]+=signal[:n]*math.sqrt((1+pan)/2)

def note(start,freq,duration=1.4,amp=.025,pan=0):
 t=np.arange(round(duration*sr))/sr
 env=(1-np.exp(-t*90))*np.exp(-t*3.4)*(np.minimum(1,(duration-t)/.14))
 signal=amp*env*(np.sin(2*np.pi*freq*t)+.18*np.sin(2*np.pi*freq*2*t)+.07*np.sin(2*np.pi*freq*3*t))
 add_sound(start,signal,pan)

# A sparse five-note identity; silence is part of the soundtrack.
for offset in [0,total-8]:
 for j,f in enumerate([293.665,349.228,440,391.995,293.665]):note(offset+.28+j*.62,f,amp=.024 if offset else .018,pan=(j-2)*.12)
elapsed=0
for i,s in enumerate(timeline):
 if i:
  # Soft, filtered noise resembles a page settling; no loud swoosh over speech.
  t=np.arange(round(.20*sr))/sr;n=rng.normal(0,1,len(t));n=np.convolve(n,np.ones(24)/24,mode='same')
  add_sound(elapsed,n*np.sin(np.pi*t/.20)**2*.018,pan=.12 if i%2 else -.12)
 if s['kind'] in ['needle','hops','updates','recall','confirmation']:
  for j,f in enumerate([293.665,440,523.251]):note(elapsed+.1+j*.22,f,duration=.9,amp=.012,pan=(j-1)*.15)
 elapsed+=s['duration']
path=root/'original-sound-design.wav'
with wave.open(str(path),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(track,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(root/'narration.wav'),'-i',str(path),
 '-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11',
 '-ar','48000','-ac','2',str(root/'final-mix.wav')],check=True)
(root/'sound-design.json').write_text(json.dumps(dict(kind='original procedural synthesis',seed=1701,sample_rate=sr,description='Sparse five-note identity and quiet filtered-noise page transitions; no continuous music under numerical explanations.'),indent=2)+'\n')
print(root/'final-mix.wav')
