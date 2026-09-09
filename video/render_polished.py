"""Native 1080p motion pass. Uses frozen evidence and cached narration; no API calls."""
import argparse
import bisect
import json
import math
from pathlib import Path
import subprocess
import textwrap
import numpy as np
from PIL import Image
import render_episode as episode
import render_preview as film


def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)


def callout(d,lines,t,color=None):
    film.card(d,80,442,1110,93,'',color or film.PAPER)
    for i,line in enumerate(lines):film.text(d,(105,456+i*30),line,23,bold=i==0)
    film.pip(d,1092,457,t,.53)


def motion(base,s,t,index):
    d=film.canvas(base);kind=s['kind'];q=t/s['duration']
    # A visual sentence changes as the narrator develops the point.
    if kind=='case':
        if q>.23:
            d.rounded_rectangle((74,241,506,343),radius=12,outline=film.MINT,width=5)
        if q>.45:
            d.line((824,286,1145,286),fill=film.GOLD,width=6)
        if q>.67:
            film.card(d,580,417,580,72,'Right fact. Wrong envelope.',film.GOLD,26)
            film.pip(d,1100,472,t,.48)
    elif kind=='token':
        # Follow each actual tokenizer segment; the ruler itself does not change.
        widths=[160,58,110,58,155,58,140];xs=[140]
        for w in widths[:-1]:xs.append(xs[-1]+w+12)
        i=min(6,max(0,int((q-.18)*12)))
        if .18<q<.78:
            d.rounded_rectangle((xs[i]-4,266,xs[i]+widths[i]+4,382),radius=14,outline=film.INK,width=4)
    elif kind=='score':
        if q<.64:
            d.rectangle((90,394,1190,565),fill=film.PAPER)
            film.text(d,(640,433),'1 returned / 4 requested',46,bold=True,anchor='mm')
            film.text(d,(640,521),'A short answer must not shrink the denominator.',25,anchor='mm')
        else:
            radius=7+4*math.sin(t*2)
            d.rounded_rectangle((430-radius,390-radius,850+radius,484+radius),radius=12,outline=film.GOLD,width=4)
    elif kind=='needle':
        chosen=[5,30,54][min(2,int(t/3))];cx=100+(chosen%15)*71;cy=237+(chosen//15)*66
        r=29+4*math.sin(t*2)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=film.INK,width=3)
    elif kind=='hops':
        # A traveling dot links the two lookups; pause at each key.
        travel=(t%8)/8
        if travel<.5:x=390+110*ease(travel*2)
        else:x=765+110*ease((travel-.5)*2)
        d.ellipse((x-7,332,x+7,346),fill=film.GOLD,outline=film.INK,width=2)
    elif kind=='updates':
        if q>.36:
            d.rounded_rectangle((100,225,570,385),radius=14,outline=film.INK,width=4)
        if q>.68:
            film.text(d,(115,460),'9 > 2',39,bold=True)
    elif kind.startswith('results_'):
        notes={
          'results_needle':[("All four models: every small needle case passed.","That includes absent-key controls."),("16 and 128 records are the easy end of this test.","Next: a much longer prompt.")],
          'results_two_hop':[("Haiku: 18 shape flags in 18 strict failures.","Inspect the response before calling this forgotten information."),("A wrong code and an unwanted explanation are different failures.","The full response audit keeps both visible.")],
          'results_updates':[("Haiku + Luna: 18/18 exact in this pilot.","Revision rules add another demand beyond finding a record."),("GPT-4o Mini: all 9 strict failures had a shape flag.","Sometimes the clerk hands over the entire folder.")],
          'results_recall':[("Two GPT-4o Mini requests hit the output limit.","They are excluded from the completed-response denominator."),("GPT-4.1 Mini: 6/6. A useful result, still a small sample.","No permanent intelligence trophy awarded.")]
        }
        which=1 if q>.59 else 0
        callout(d,notes[kind][which],t,film.MINT if which==0 else film.GOLD)
        # Row spotlight tracks the named finding without altering bar values.
        highlight={'results_needle':None,'results_two_hop':0 if which==0 else 2,
                   'results_updates':None if which==0 else 2,'results_recall':2 if which==0 else 1}[kind]
        if highlight is not None:
            y=215+highlight*48
            d.rounded_rectangle((67,y-8,1204,y+36),radius=7,outline=film.INK,width=2)
    elif kind=='retrieval_case':
        if q>.38:
            d.rounded_rectangle((70,425,750,515),radius=14,outline=film.CORAL,width=4)
        if q>.67:
            film.text(d,(780,485),'Wrong answer. Fact present.',21,bold=True)
    elif kind=='confirmation':
        # One square per fresh seed, plus descriptive uncertainty intervals.
        for panel,(x,color) in enumerate([(90,film.GOLD),(715,film.MINT)]):
            count=min(8,max(0,int((q-.20)*30)))
            for i in range(8):
                xx=x+i*43
                d.rounded_rectangle((xx,490,xx+28,511),radius=4,fill=color if i<count else '#DFDDD4')
                if i<count:
                    if panel==0:d.line((xx+7,495,xx+21,506),fill=film.INK,width=2);d.line((xx+21,495,xx+7,506),fill=film.INK,width=2)
                    else:d.line([(xx+6,501),(xx+12,506),(xx+22,494)],fill=film.INK,width=2)
        if q>.72:
            d.rectangle((75,527,1200,573),fill=film.PAPER)
            film.text(d,(90,540),'95% Wilson interval: 0–32.4%',20,fill=film.GRAY)
            film.text(d,(715,540),'95% Wilson interval: 67.6–100%',20,fill=film.GRAY)
    elif kind=='totals':
        if q>.47:
            d.rectangle((697,382,1190,474),fill=film.PAPER)
            film.text(d,(705,390),'2 + 15',64,bold=True)
    elif kind=='panels':
        if q>.28:
            d.rounded_rectangle((75,240,1190,286),radius=7,outline=film.GOLD,width=3)
        if q>.66:
            d.line((83,525,1140,525),fill=film.GOLD,width=4)
    elif kind=='limits':
        row=min(3,int(q*4));y=225+row*78
        d.rounded_rectangle((86,y-10,1190,y+52),radius=8,outline=film.GOLD,width=3)
    elif kind=='end_results':
        film.text(d,(920,490),'FILED.',42,bold=True,fill=film.GRAY)
        if q>.5:d.line((912,545,1128,545),fill=film.GOLD,width=5)
    d.rectangle((1170,570,1260,596),fill=film.PAPER)
    film.text(d,(1225,577),f'{index+1:02} / 20',14,fill=film.GRAY,anchor='ra')
    # Remove rehearsal captions; the final pass burns in reviewed, timed captions.
    d.rectangle((0,597,1280,715),fill=film.INK)
    # Restrained entrance: the visual panel rises into place over 0.45 seconds.
    if t<.45:
        shift=round(24*(1-ease(t/.45))*film.RENDER_SCALE)
        panel=base.crop((0,round(176*film.RENDER_SCALE),base.width,round(589*film.RENDER_SCALE)))
        d.rectangle((0,176,1280,589),fill=film.PAPER)
        base.paste(panel.crop((0,0,panel.width,panel.height-shift)),(0,round(176*film.RENDER_SCALE)+shift))
    return base


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='artifacts/episode-01');p.add_argument('--stills-only',action='store_true');a=p.parse_args()
    root=Path(a.root).resolve();episode.configure('artifacts/episode-evidence/evidence.json');film.RENDER_SCALE=1.5
    timeline=json.loads((root/'timeline.json').read_text());assert len(timeline)==len(film.SCENES)
    for s,(_,_,text) in zip(timeline,film.SCENES):assert s['narration']==text,'Narration and frozen timeline differ'
    total=sum(s['duration'] for s in timeline);stilldir=root/'review-1080p';stilldir.mkdir(exist_ok=True)
    elapsed=0
    for i,s in enumerate(timeline):
        t=s['duration']*.72;im=motion(film.frame(s['kind'],s['title'],'',t,(elapsed+t)/total,i),s,t,i)
        im.save(stilldir/f'scene-{i:02}.png');elapsed+=s['duration']
    if a.stills_only:return
    final=root/'GPT-Learning-01.mp4'
    # Native-resolution frames and the reviewed soundtrack are encoded only once.
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-',
      '-i',str(root/'final-mix.wav'),'-vf','ass=final-captions.ass','-c:v','libx264','-preset','veryfast','-crf','16',
      '-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-shortest',str(final)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE,cwd=root);elapsed=0
    for i,s in enumerate(timeline):
        for frame in range(round(s['duration']*24)):
            t=frame/24;im=motion(film.frame(s['kind'],s['title'],'',t,(elapsed+t)/total,i),s,t,i)
            process.stdin.write(im.tobytes())
        elapsed+=s['duration'];print(f'Native 1080p: {i+1}/{len(timeline)}',flush=True)
    process.stdin.close()
    if process.wait()!=0:raise RuntimeError('Final encode failed')
    print(final)

if __name__=='__main__':main()
