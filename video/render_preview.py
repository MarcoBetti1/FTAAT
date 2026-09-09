"""Original procedural animation. Local macOS scratch voice; no model results invented.
Run: python video/render_preview.py --output artifacts/video-preview
Requires ffmpeg/ffprobe, macOS say, Pillow, numpy. Replaces only its own generated files.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
INK = '#172B36'
PAPER = '#F5F1E7'
MINT = '#A4D8C4'
GOLD = '#E7B446'
CORAL = '#D7745D'
GRAY = '#73818A'
FONT_ROOT = Path('/System/Library/Fonts/Supplemental')
FONT = FONT_ROOT / 'Arial.ttf'
BOLD = FONT_ROOT / 'Arial Bold.ttf'
MONO = Path('/System/Library/Fonts/Menlo.ttc')
FONTS = {}


def font(size, bold=False, mono=False):
    key = (size,bold,mono)
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype(str(MONO if mono else BOLD if bold else FONT),size)
    return FONTS[key]


def text(d, xy, value, size=30, fill=INK, bold=False, anchor=None, mono=False):
    d.text(xy,value,font=font(size,bold,mono),fill=fill,anchor=anchor)


def card(d, x,y,w,h,label,color=PAPER,size=28):
    d.rounded_rectangle((x+4,y+5,x+w+4,y+h+5),radius=12,fill='#D9D6CD')
    d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=color,outline=INK,width=2)
    text(d,(x+w/2,y+h/2),label,size,anchor='mm',bold=True)


def arrow(d, a,b,color=INK):
    d.line([a,b],fill=color,width=4)
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    pts=[b,(b[0]-15*math.cos(angle-.5),b[1]-15*math.sin(angle-.5)),(b[0]-15*math.cos(angle+.5),b[1]-15*math.sin(angle+.5))]
    d.polygon(pts,fill=color)


def pip(d,x,y,t,scale=1):
    # An original paper clerk; dotted strip, tiny arms, eyebrows and a bow tie.
    w,h=100*scale,120*scale
    d.line((x-25*scale,y+70*scale,x,y+55*scale),fill=INK,width=3)
    d.line((x+w,y+55*scale,x+w+25*scale,y+(60+12*math.sin(t*2))*scale),fill=INK,width=3)
    d.rounded_rectangle((x,y,x+w,y+h),radius=8,fill=MINT,outline=INK,width=3)
    for yy in range(12,110,14):
        d.ellipse((x+7*scale,y+yy*scale,x+10*scale,y+(yy+3)*scale),fill=INK)
    blink = (t%4)<.12
    for xx in (37,68):
        d.ellipse((x+(xx-4)*scale,y+40*scale,x+(xx+4)*scale,y+(42 if blink else 52)*scale),fill=INK)
    d.arc((x+38*scale,y+47*scale,x+69*scale,y+78*scale),0,180,fill=INK,width=2)
    d.polygon([(x+34*scale,y+92*scale),(x+53*scale,y+102*scale),(x+34*scale,y+110*scale)],fill=INK)
    d.polygon([(x+72*scale,y+92*scale),(x+53*scale,y+102*scale),(x+72*scale,y+110*scale)],fill=INK)


SCENES = [
('desk','A bigger desk. A better memory?',
 "Meet Pip, clerk at the Bureau of Misplaced Facts. We are giving language models more paperwork, then asking very small questions. A bigger desk holds more files. Does it make the clerk better at finding one?"),
('token','First, check the ruler.',
 "Before we test the models, we have to test our ruler. In the old experiment, these four symbols were treated as four tokens. But the separators count too. This actual GPT four O Mini tokenization contains seven tokens."),
('audit','4 symbols. 7 tokens.',
 "We checked one thousand seeded four-symbol sequences from the old inventory. All one thousand used seven tokens when joined. That is a tokenizer measurement, not a model failure. Our old answer allowance could run out before the answer did."),
('needle','01 / The missing file',
 "First game: hide one random fact in a growing pile of records. Move the same fact from the beginning, to the middle, to the end. Can the model still find it? We will also ask for a fact that is not there."),
('hops','02 / Follow the paperwork',
 "Second game: follow two arrows. The first record points to another key. The second gives the answer. Neither step is difficult by itself. The interesting question is what happens when the clues are far apart."),
('updates','03 / The stale memo',
 "Third game: the paperwork disagrees with itself. Revision nine is current, even if revision two appears later on the page. This tests whether the model applies the rule, rather than simply repeating the last thing it saw."),
('recall','04 / The entire inventory',
 "Then we ask for every value in shuffled order. Now the answer grows too. If the output limit cuts it off, that is a different failure. An empty printer tray does not prove the clerk forgot the files."),
('score','A perfect prefix is not a perfect answer.',
 "The old scorer could also reward a perfect prefix while ignoring missing answers. One correct answer out of four is twenty five percent, not one hundred. We now count all expected answers, and keep errors separate."),
('fair','Same paperwork. Different rulers.',
 "Both providers get the same seeded text. Each model gets its own official token count. We save the actual usage, settings, prompts and responses. Small samples get wide uncertainty intervals. There is no universal memory score hiding in these games."),
('end','The experiment is ready. The results are not.',
 "This is our production rehearsal. The comparison runs come next, with older and newer models, and a small budget. If they all succeed, that is the story. The goal is to learn something real. Preferably before Pip resigns.")
]


def frame(kind,title,subtitle,t,progress,index):
    im=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(im)
    # quiet registration marks and a consistent episode identity
    for x in range(32,W,32): d.point((x,36),fill='#D0CEC5')
    text(d,(55,40),'GPT LEARNING  /  BUREAU OF MISPLACED FACTS',15,bold=True)
    text(d,(1225,40),'METHOD + STYLE PREVIEW',14,fill=GRAY,anchor='ra')
    text(d,(55,88),title,43,bold=True)
    d.line((55,157,1225,157),fill=INK,width=2)
    if kind=='desk':
        d.rounded_rectangle((210,345,1060,490),radius=15,fill=INK)
        text(d,(635,455),'CONTEXT WINDOW',23,fill=PAPER,anchor='mm')
        for i in range(min(16,int(t*1.8)+1)):
            x=250+(i%8)*94; y=250-(i//8)*35+8*math.sin(t+i)
            card(d,x,y,76,94,f'{i+1:02}',GOLD if i==7 else PAPER,22)
        pip(d,1060,355,t)
        text(d,(220,527),'Capacity is not the same thing as successful retrieval.',25)
    elif kind=='token':
        parts=['pson','|','lp','|','ourt','|','pell']
        widths=[160,58,110,58,155,58,140]
        x=140
        for i,(part,ww) in enumerate(zip(parts,widths)):
            y=270+(0 if t>i*.3 else 30)
            card(d,x,y,ww,108,part,GOLD if part=='|' else MINT,35)
            text(d,(x+ww/2,410),str(i+1),22,fill=GRAY,anchor='mm')
            x+=ww+12
        text(d,(640,475),'4 SYMBOLS  +  3 SEPARATORS  =  7 TOKENS',27,bold=True,anchor='mm')
        text(d,(640,520),'Measured: o200k_base / GPT-4o Mini (2024-07-18)',20,fill=GRAY,anchor='mm')
    elif kind=='audit':
        text(d,(80,208),'LOCAL TOKENIZER MEASUREMENT',18,fill=GRAY,bold=True)
        text(d,(80,250),'1,000',112,bold=True)
        text(d,(85,390),'seeded sequences tested',25)
        text(d,(740,250),'7',112,bold=True)
        text(d,(740,390),'tokens each',25)
        for i in range(25):
            x=550+(i%5)*24; y=250+(i//5)*24
            d.rounded_rectangle((x,y,x+16,y+16),radius=3,fill=MINT if t>i*.05 else '#D9D6CD')
        card(d,80,466,1020,60,'K = symbols; count the complete rendered text.',GOLD,24)
    elif kind=='needle':
        for i in range(60):
            x=70+(i%15)*71; y=213+(i//15)*66
            chosen=[5,30,54][min(2,int(t/3))]
            color=GOLD if i==chosen else '#E5E2D9'
            card(d,x,y,60,47,'?' if i==chosen else '',color,25)
        text(d,(80,517),'Same fact. Different position. More distractors.',26,bold=True)
        pip(d,1160,368,t,.6)
    elif kind=='hops':
        for i,(label,color) in enumerate([('KEY A',PAPER),('KEY B',GOLD),('VALUE',MINT)]):
            card(d,120+i*375,272,270,132,label,color,35)
        for i in range(2):
            arrow(d,(403+i*375,339),(481+i*375,339),INK if t>2*i else GRAY)
        text(d,(245,453),'first clue',24,anchor='mm')
        text(d,(620,453),'second clue',24,anchor='mm')
        text(d,(1000,453),'answer',24,anchor='mm')
        text(d,(640,526),'Follow exactly TWO arrows.',25,bold=True,anchor='mm')
    elif kind=='updates':
        card(d,105,230,460,150,'REVISION 9  /  MINT',MINT,29)
        card(d,715,330,460,150,'REVISION 2  /  GOLD',GOLD,29)
        text(d,(110,413),'CURRENT',24,bold=True)
        text(d,(720,253),'Appears later in the text...',24)
        if t>3:
            d.line((750,425,1130,425),fill=CORAL,width=7)
        text(d,(640,548),'Highest revision wins. Last line does not.',25,bold=True,anchor='mm')
    elif kind=='recall':
        card(d,85,250,360,180,'ALL THE FILES',MINT,29)
        arrow(d,(470,340),(665,340))
        card(d,700,218,450,280,'',PAPER)
        for i in range(min(7,int(t)+1)):
            text(d,(735,250+i*30),f'{i+1:02}  ABCD | EFGH',22,mono=True)
        d.line((680,443,1170,443),fill=CORAL,width=4)
        text(d,(680,520),'OUTPUT CAP ≠ RETRIEVAL FAILURE',22,bold=True)
    elif kind=='score':
        for i in range(4):
            card(d,120+i*270,245,220,125,'CORRECT' if i==0 else 'MISSING',MINT if i==0 else '#E5E2D9',22)
        text(d,(640,444),'1 / 4 = 25%',67,bold=True,anchor='mm')
        text(d,(640,529),'The denominator includes the missing answers.',26,anchor='mm')
    elif kind=='fair':
        card(d,435,205,410,86,'IDENTICAL SEEDED TEXT',PAPER,25)
        arrow(d,(515,310),(300,365)); arrow(d,(765,310),(980,365))
        card(d,95,385,410,100,'OPENAI MODEL COUNT',MINT,25)
        card(d,775,385,410,100,'CLAUDE MODEL COUNT',GOLD,25)
        text(d,(640,535),'Save actual usage, not just a guess from character length.',24,anchor='mm')
    else:
        text(d,(90,220),'NEXT: REAL MODEL RUNS',24,fill=GRAY,bold=True)
        for i,label in enumerate(['Older + newer models','Small, recorded budgets','Publish successes too']):
            text(d,(95,284+i*68),label,36,bold=True)
        pip(d,1000,260,t,1.5)
        text(d,(1015,485),'Pip is cautiously optimistic.',18,anchor='mm')
    # Subtitles are baked in for the preview and also supplied as an SRT.
    d.rectangle((0,597,W,H),fill=INK)
    lines=textwrap.wrap(subtitle,91)
    for i,line in enumerate(lines[:3]):
        text(d,(640,625+i*27),line,22,fill=PAPER,anchor='mm')
    d.rectangle((0,H-5,int(W*progress),H),fill=GOLD)
    text(d,(1218,575),f'{index+1:02} / {len(SCENES):02}',14,fill=GRAY,anchor='ra')
    return im


def timestamp(sec):
    ms=round(sec*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',default='artifacts/video-preview')
    parser.add_argument('--stills-only',action='store_true'); args=parser.parse_args()
    out=Path(args.output).resolve(); out.mkdir(parents=True,exist_ok=True)
    for i,(kind,title,narration) in enumerate(SCENES):
        frame(kind,title,narration.split('. ')[0]+'.',5,.5,i).save(out/f'scene-{i:02}.png')
    if args.stills_only: return
    timeline=[]
    for i,(kind,title,narration) in enumerate(SCENES):
        txt=out/f'voice-{i:02}.txt'; audio=out/f'voice-{i:02}.aiff'
        txt.write_text(narration)
        subprocess.run(['say','-v','Daniel','-r','164','-f',str(txt),'-o',str(audio)],check=True)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(audio)]))+.65
        timeline.append(dict(kind=kind,title=title,narration=narration,duration=duration,audio=str(audio)))
    total=sum(s['duration'] for s in timeline)
    video=out/'picture.mp4'
    proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                           '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
    elapsed=0; srt=[]; cue=1
    for index,s in enumerate(timeline):
        sentences=textwrap.wrap(s['narration'],160,break_long_words=False,break_on_hyphens=False)
        nframes=math.ceil(s['duration']*FPS)
        actual_duration=nframes/FPS
        for i,line in enumerate(sentences):
            a=elapsed+i*actual_duration/len(sentences); b=elapsed+(i+1)*actual_duration/len(sentences)
            srt.append(f'{cue}\n{timestamp(a)} --> {timestamp(b)}\n{line}\n'); cue+=1
        for f in range(nframes):
            t=f/FPS; sub=sentences[min(len(sentences)-1,int(t/actual_duration*len(sentences)))]
            im=frame(s['kind'],s['title'],sub,t,(elapsed+t)/total,index)
            proc.stdin.write(im.tobytes())
        s['duration']=actual_duration
        elapsed+=actual_duration
        print(f'Rendered {index+1}/{len(timeline)}: {s["title"]}',flush=True)
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('ffmpeg picture render failed')
    audio_parts=[]
    for i,s in enumerate(timeline):
        part=out/f'audio-{i:02}.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-i',s['audio'],'-af','apad','-t',str(s['duration']),'-ar','48000','-ac','2',str(part)],check=True)
        audio_parts.append(part)
    concat=out/'audio-list.txt'; concat.write_text(''.join("file '"+str(p)+"'\n" for p in audio_parts))
    audio=out/'narration.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-af','loudnorm=I=-16:TP=-1.5:LRA=11',str(audio)],check=True)
    final=out/'GPT-Learning-method-preview.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(audio),'-vf','scale=1920:1080:flags=lanczos',
                    '-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-movflags','+faststart','-shortest',str(final)],check=True)
    (out/'captions.srt').write_text('\n'.join(srt))
    (out/'timeline.json').write_text(json.dumps(timeline,indent=2))
    print(final)

if __name__=='__main__': main()
