"""Native 1080p/30 rendering, cached per shot, then lossless video concatenation."""
import argparse
import bisect
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
from .art import captions,wrap
from .motion import render
from .speech import ROOT

def clip(args):
    s,cues,summary,preview,source=args
    settings=dict(shot=s,cues=cues,summary=summary if s['kind'] in ('primary','positions','middle','claude','uncertainty','scores','format_result','revision_result','method') else None,source=source,preview=preview)
    identity=hashlib.sha256(json.dumps(settings,sort_keys=True).encode()).hexdigest();cache=ROOT/'clips';cache.mkdir(exist_ok=True);out=cache/(s['id']+'-'+identity[:14]+'.mp4')
    if out.exists():return str(out)
    temporary=out.with_suffix('.partial.mp4');frames=round(s['duration']*30)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(temporary)]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
        for f in range(frames):
            t=f/30;im=render(s,t,summary);now=s['start']+t
            current=next((c['lines'] for c in cues if c['start']<=now<c['end']),[])
            if preview and s['narration']:
                words=s['narration'].split();a=min(max(0,int(t/max(1,s['speech_duration'])*len(words))//11*11),max(0,len(words)-1));current=wrap(' '.join(words[a:a+11]),1590,37) if t<s['speech_duration']+.2 else []
            captions(im,current);proc.stdin.write(im.tobytes())
        proc.stdin.close();code=proc.wait()
        if code:raise RuntimeError(f'Render failed: {s["id"]}')
    temporary.rename(out);return str(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opening',action='store_true');ap.add_argument('--stills',action='store_true');ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args()
    timeline=json.loads((ROOT/('opening-timeline.json' if a.opening else 'timeline.json')).read_text())
    summary=json.loads(Path('docs/episodes/01-v2/summary.json').read_text()) if not a.opening else None
    cues=json.loads((ROOT/'captions.json').read_text()) if not a.opening else []
    if a.stills:
        p=ROOT/'storyboard';p.mkdir(exist_ok=True)
        for s in timeline:
            for q in [.25,.75]:
                t=s['duration']*q;im=render(s,t,summary);captions(im,next((c['lines'] for c in cues if c['start']<=s['start']+t<c['end']),[]));im.save(p/(s['id']+f'-{q}.png'))
        print(p);return
    source=hashlib.sha256(b''.join((Path(__file__).parent/p).read_bytes() for p in ('render.py','motion.py','art.py'))).hexdigest()
    args=[(s,[c for c in cues if c['shot']==s['id']],summary,a.opening,source) for s in timeline]
    with ProcessPoolExecutor(max_workers=a.jobs) as pool:
        clips=[]
        for s,p in zip(timeline,pool.map(clip,args)):
            clips.append(p);print('Rendered',s['id'],flush=True)
    listing=ROOT/('opening-clips.txt' if a.opening else 'final-clips.txt');listing.write_text(''.join("file '"+p+"'\n" for p in clips))
    final=ROOT/('opening-preview.mp4' if a.opening else 'GPT-Learning-01-v2.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(ROOT/('opening-mix.wav' if a.opening else 'mix.wav')),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(final)],check=True)
    print(final,flush=True)

if __name__=='__main__':main()
