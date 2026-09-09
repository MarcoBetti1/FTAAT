"""Align the reviewed script to ASR word times, export subtitles and a final MP4.
Words always come from the reviewed script. ASR supplies timing, not model names or
result values. Changed spans use interpolation between neighboring timed words.
"""
import argparse
import difflib
import json
from pathlib import Path
import re
import subprocess
import textwrap


def clock(sec, ass=False):
    ms=round(max(0,sec)*1000)
    if ass:return f'{ms//3600000}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000//10:02}'
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def display_script(text):
    for a,b in [('GPT four O Mini','GPT-4o Mini'),('GPT four point one Mini','GPT-4.1 Mini'),('GPT five point six Luna','GPT-5.6 Luna')]:
        text=text.replace(a,b)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('--captions-only',action='store_true');p.add_argument('--root',default='artifacts/episode-01');p.add_argument('--transcript',default='audio-qa-v3/transcript.json');a=p.parse_args()
    root=Path(a.root).resolve();timeline=json.loads((root/'timeline.json').read_text())
    transcript=json.loads((root/a.transcript).read_text());words=transcript['words']
    expected=' '.join(display_script(s['narration']) for s in timeline).split()
    norm=lambda x:re.sub(r'[^a-z0-9]','',x.lower())
    matcher=difflib.SequenceMatcher(None,[norm(w['word']) for w in words],[norm(x) for x in expected],autojunk=False)
    timed=[]
    for kind,i,j,k,l in matcher.get_opcodes():
        if kind=='equal':
            timed.extend(dict(text=expected[b],start=words[t]['start'],end=words[t]['end']) for t,b in zip(range(i,j),range(k,l)))
        elif kind in ('replace','insert'):
            start=words[i]['start'] if i<len(words) else words[-1]['end']
            end=words[j-1]['end'] if j>i else start+.12*(l-k)
            timed.extend(dict(text=expected[b],start=start+(b-k)*(end-start)/(l-k),end=start+(b-k+1)*(end-start)/(l-k)) for b in range(k,l))
    cues=[];group=[]
    for w in timed:
        if group and (len(' '.join(x['text'] for x in group))+len(w['text'])>104 or w['end']-group[0]['start']>5.8):
            cues.append(group);group=[]
        group.append(w)
        if w['text'].endswith(('.','?','!')) and len(group)>=5:
            cues.append(group);group=[]
    if group:cues.append(group)
    srt=[];ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','WrapStyle: 0','',
        '[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
        'Style: Default,Arial,34,&H00E7F1F5,&H00E7F1F5,&H00362B17,&H00362B17,0,0,0,0,100,100,0,0,1,0,0,2,140,140,48,1','',
        '[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    for n,g in enumerate(cues):
        start=g[0]['start'];end=max(start+.3,g[-1]['end']+.12)
        if n+1<len(cues):end=min(end,cues[n+1][0]['start'])
        if end<=start:continue
        lines=textwrap.wrap(' '.join(w['text'] for w in g),width=68,break_long_words=False)
        caption='\n'.join(lines)
        srt.append(f'{n+1}\n{clock(start)} --> {clock(end)}\n{caption}\n')
        ass.append(f'Dialogue: 0,{clock(start,True)},{clock(end,True)},Default,,0,0,0,,'+caption.replace('\n',r'\N'))
    (root/'GPT-Learning-01.en.srt').write_text('\n'.join(srt))
    (root/'final-captions.ass').write_text('\n'.join(ass)+'\n')
    script=['# GPT Learning — Episode 01','', 'AI-generated narration using OpenAI stock voice Cedar. Original procedural graphics.','']
    elapsed=0
    for s in timeline:
        script.extend([f"## {clock(elapsed)} — {s['title']}",'',display_script(s['narration']),'']);elapsed+=s['duration']
    (root/'script.md').write_text('\n'.join(script))
    (root/'caption-alignment.json').write_text(json.dumps(dict(source='reviewed script',timing='Whisper word timestamps with interpolated edited spans',cues=len(cues),duration=elapsed,transcript=a.transcript),indent=2)+'\n')
    if a.captions_only:return
    final=root/'GPT-Learning-01.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(root/'picture.mp4'),'-i',str(root/'narration.wav'),
       '-vf','scale=1920:1080:flags=lanczos,drawbox=x=0:y=895:w=1920:h=178:color=0x172B36:t=fill,ass=final-captions.ass',
       '-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart',str(final)],cwd=root,check=True)
    print(final)

if __name__=='__main__':main()
