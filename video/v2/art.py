"""Original procedural art. Native 1920×1080; no stock art or external assets."""
from functools import lru_cache
import math
import random
from PIL import Image, ImageDraw, ImageFont

W,H=1920,1080
INK='#172D35'; PAPER='#F6F1E5'; WHITE='#FFFCF3'; MINT='#82BFA5'
GOLD='#F5BD57'; RED='#DA705D'; MUTED='#72817E'; LINE='#D6D5C8'; BLUE='#8DB7CF'

@lru_cache(None)
def font(size=40,style='sans'):
    if style=='symbols':return ImageFont.truetype('/System/Library/Fonts/Apple Symbols.ttf',size)
    if style=='serif': return ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf',size)
    if style=='italic': return ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Italic.ttf',size)
    if style=='mono': return ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',size)
    return ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc',size,index=0 if style=='bold' else 5)

def text(d,xy,s,size=40,fill=INK,style='sans',anchor=None):
    s=str(s)
    # These symbols are missing from Avenir's font file (Pillow has no OS fallback).
    if any(c in s for c in '→★♞≠'):
        f=font(size,style);parts=[(c,font(size,'symbols') if c in '→★♞≠' else f) for c in s]
        total=sum(ff.getlength(c) for c,ff in parts);x,y=xy
        if anchor and anchor[0]=='m':x-=total/2
        if anchor and anchor[0]=='r':x-=total
        vert=anchor[1] if anchor else 'a'
        for c,ff in parts:
            d.text((x,y),c,font=ff,fill=fill,anchor='l'+vert);x+=ff.getlength(c)
    else:d.text(xy,s,font=font(size,style),fill=fill,anchor=anchor,stroke_width=0)

def wrap(s,width,size=40,style='sans'):
    words=s.split();lines=[];line=''
    for word in words:
        nxt=(line+' '+word).strip()
        if font(size,style).getlength(nxt)>width and line:lines.append(line);line=word
        else:line=nxt
    if line:lines.append(line)
    return lines

def block(d,xy,s,width,size=40,fill=INK,style='sans',leading=1.3):
    x,y=xy
    for i,line in enumerate(wrap(s,width,size,style)):text(d,(x,y+i*size*leading),line,size,fill,style)

def rr(d,box,fill=WHITE,r=20,outline=None,width=2):
    d.rounded_rectangle(tuple(round(v) for v in box),radius=r,fill=fill,outline=outline,width=width)

def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def out(x):return 1-(1-max(0,min(1,x)))**3
def lerp(a,b,x):return a+(b-a)*x

def label(d,xy,s,fill=INK,color=WHITE,size=25):
    x,y=xy;w=font(size,'bold').getlength(s)+36
    rr(d,(x,y,x+w,y+size+24),fill,8);text(d,(x+18,y+8),s,size,color,'bold')

def arrow(d,a,b,color=INK,width=5):
    d.line([a,b],fill=color,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);L=17
    d.polygon([b,(b[0]-L*math.cos(ang-.5),b[1]-L*math.sin(ang-.5)),(b[0]-L*math.cos(ang+.5),b[1]-L*math.sin(ang+.5))],fill=color)

@lru_cache(24)
def backdrop(kind='paper'):
    im=Image.new('RGB',(W,H),PAPER if kind!='dark' else INK);d=ImageDraw.Draw(im)
    if kind in ('office','warehouse'):
        d.rectangle((0,0,W,130),fill=INK)
        text(d,(85,32),'LOST & FOUND',46,WHITE,'bold')
        text(d,(W-85,59),'Everything is here. Probably.',28,MINT,'italic','rm')
        d.rectangle((0,790,W,H),fill='#E2DDCF')
        d.line((0,790,W,790),fill='#C4C4B8',width=4)
        for x in range(30,W,190):
            d.line((x,790,x-250,H),fill='#D0CCBF',width=2)
        if kind=='office':
            cabinet(d,135,233,.9);cabinet(d,1450,233,.9)
            rr(d,(725,166,1195,287),WHITE,4,LINE)
            text(d,(960,225),'PLEASE TAKE A NUMBER',25,INK,'bold','mm')
            text(d,(960,261),'The number is also missing.',22,MUTED,'italic','mm')
    elif kind=='paper':
        for x in range(25,W,44):
            for y in range(24,900,44): d.point((x,y),fill='#DCDCCF')
    elif kind=='dark':
        for x in range(0,W,100):d.line((x,0,x,H),fill='#1B343C')
        for y in range(0,H,100):d.line((0,y,W,y),fill='#1B343C')
    return im

def cabinet(d,x,y,s=1,fill='#B6C5BA'):
    ww=320*s;hh=520*s
    rr(d,(x+12*s,y+12*s,x+ww+12*s,y+hh+12*s),'#D0CEC0',9)
    rr(d,(x,y,x+ww,y+hh),fill,9,INK,3)
    for i in range(4):
        yy=y+(14+i*126)*s
        rr(d,(x+13*s,yy,x+ww-13*s,yy+112*s),fill,4,INK,2)
        rr(d,(x+112*s,yy+21*s,x+208*s,yy+49*s),WHITE,3,INK,2)
        d.line((x+113*s,yy+74*s,x+207*s,yy+74*s),fill=INK,width=max(2,round(5*s)))

@lru_cache(256)
def pip_sprite(height=390,mood='neutral',pose='rest',phase=0,speaking=False,dark=False):
    # Paper body, three binder holes, bow tie, independent arms and feet.
    s=height/390;im=Image.new('RGBA',(round(430*s),round(450*s)),(0,0,0,0));d=ImageDraw.Draw(im)
    def P(p):return tuple(round(v*s) for v in p)
    def ln(points,fill=INK,w=7):d.line([P(p) for p in points],fill=fill,width=max(1,round(w*s)),joint='curve')
    wave=math.sin(phase*math.pi/6)
    left=[(113,230),(67,255),(35,236)]
    right=[(305,230),(351,260),(380,242)]
    if pose=='panic':left=[(114,228),(59,161),(37,112+wave*15)];right=[(302,229),(355,160),(387,110-wave*15)]
    if pose=='point':right=[(303,230),(351,207),(401,183+wave*5)]
    if pose=='shrug':left=[(113,230),(65,214),(30,192)];right=[(305,230),(355,214),(397,192)]
    limb=MINT if dark else INK
    ln(left,fill=limb);ln(right,fill=limb)
    for p in (left[-1],right[-1]):d.ellipse(P((p[0]-10,p[1]-10,p[0]+10,p[1]+10)),fill=limb)
    ln([(171,355),(159,410),(133,410)],fill=limb,w=9);ln([(248,355),(258,410),(288,410)],fill=limb,w=9)
    body=[(111,62),(262,62),(308,108),(308,358),(111,358)]
    d.polygon([P(p) for p in body],fill=WHITE,outline=INK,width=max(1,round(4*s)))
    d.polygon([P(p) for p in [(262,62),(262,108),(308,108)]],fill=GOLD,outline=INK,width=max(1,round(3*s)))
    for yy in (128,211,305):d.ellipse(P((123,yy,136,yy+13)),fill='#C6D2C7',outline=INK,width=max(1,round(s)))
    blink=phase==11
    for xx in (185,257):
        if blink:ln([(xx-7,171),(xx+7,171)],w=5)
        else:d.ellipse(P((xx-6,162,xx+6,179)),fill=INK)
    if mood=='panic':
        ln([(172,146),(192,140)],w=4);ln([(247,140),(267,146)],w=4)
        d.ellipse(P((206,206,236,243)),fill=INK)
        d.polygon([P(p) for p in [(326,139),(315,161),(337,161)]],fill=BLUE)
    elif mood=='annoyed':
        ln([(172,151),(195,159)],w=5);ln([(245,158),(268,151)],w=5);ln([(204,225),(238,225)],w=4)
    elif mood=='happy': d.arc(P((196,191,244,229)),0,180,fill=INK,width=max(1,round(4*s)))
    else:ln([(204,220),(235,220)],w=4)
    if speaking and phase%3!=0:
        d.rectangle(P((200,206,241,239)),fill=WHITE)
        d.ellipse(P((208,207,236,235)),fill=INK)
    d.polygon([P(p) for p in [(220,279),(193,266),(193,295)]],fill=RED,outline=INK,width=max(1,round(2*s)))
    d.polygon([P(p) for p in [(220,279),(248,266),(248,295)]],fill=RED,outline=INK,width=max(1,round(2*s)))
    d.ellipse(P((212,272,227,287)),fill=GOLD,outline=INK,width=max(1,round(2*s)))
    return im

def pip(im,x,y,t=0,height=390,mood='neutral',pose='rest',talk=False):
    dark=im.getpixel((1,1))[0]<50
    phase=int(t*(9 if talk else 3))%12;sprite=pip_sprite(height,mood,pose,phase,talk,dark)
    bob=math.sin(t*2.1)*3 if talk else 0
    d=ImageDraw.Draw(im);s=height/390
    shadow='#10262D' if im.getpixel((1,1))[0]<50 else '#BBBCAE'
    d.ellipse((x+102*s,y+404*s,x+312*s,y+428*s),fill=shadow)
    im.paste(sprite,(round(x),round(y+bob)),sprite)

def folder(d,x,y,w=260,h=160,color=GOLD,title='',small=False):
    rr(d,(x,y,x+w*.43,y+30),color,8,INK,2)
    rr(d,(x,y+20,x+w,y+h),color,8,INK,2)
    if title:text(d,(x+w/2,y+h*.6),title,20 if small else 28,INK,'mono','mm')

def record(d,x,y,key='QZRX|MPLN',value='VTFK|WDJB',w=680,tag='FILE 7373'):
    rr(d,(x+10,y+12,x+w+10,y+212),'#D7D5C8',12)
    rr(d,(x,y,x+w,y+200),WHITE,12,INK,3)
    label(d,(x+26,y+20),tag,fill=MINT,color=INK,size=20)
    text(d,(x+30,y+103),key,32,INK,'mono')
    arrow(d,(x+300,y+130),(x+365,y+130))
    text(d,(x+390,y+103),value,32,INK,'mono')

def stamp(im,xy,s,angle=-8,color=RED,scale=1):
    fs=round(48*scale);ww=round(font(fs,'bold').getlength(s)+64*scale);hh=round(96*scale)
    z=Image.new('RGBA',(ww+30,hh+30),(0,0,0,0));d=ImageDraw.Draw(z)
    rr(d,(15,15,ww,hh),(0,0,0,0),8,color,round(5*scale));text(d,((ww+15)/2,(hh+15)/2),s,fs,color,'bold','mm')
    z=z.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True);im.paste(z,(round(xy[0]),round(xy[1])),z)

def captions(im,lines):
    if not lines:return
    d=ImageDraw.Draw(im);fs=37
    width=max(font(fs).getlength(x) for x in lines)+70;hh=62+50*(len(lines)-1)
    x=(W-width)/2;y=H-52-hh
    rr(d,(x,y,x+width,y+hh),INK,12)
    for i,line in enumerate(lines):text(d,(W/2,y+12+i*50),line,fs,WHITE,'sans','mt')

def signature(d,dark=False):
    text(d,(W-52,28),'GPT LEARNING',20,MINT if dark else MUTED,'bold','ra')

def heading(d,kicker,title,sub=None,dark=False):
    color=WHITE if dark else INK
    label(d,(100,82),kicker,MINT,INK,23)
    text(d,(100,163),title,68,color,'serif')
    if sub:text(d,(103,262),sub,29,MINT if dark else MUTED)

def proof():
    from pathlib import Path
    p=Path('artifacts/episode-01-v2/proofs');p.mkdir(parents=True,exist_ok=True)
    im=backdrop('office').copy();d=ImageDraw.Draw(im)
    folder(d,490,550,320,210,title='ONE SMALL JOB')
    pip(im,830,330,1,450,'happy','point');stamp(im,(790,740),'OPEN FOR BUSINESS',-5,INK,.7)
    im.save(p/'office.png')
    im=backdrop('dark').copy();d=ImageDraw.Draw(im)
    text(d,(110,95),'8,192 files.',112,WHITE,'serif');text(d,(116,245),'One increasingly nervous clerk.',45,MINT,'italic')
    for i in range(45):
        x=80+(i%15)*115;y=455+(i//15)*113
        folder(d,x,y,100,80,color=[GOLD,MINT,BLUE][i%3])
    pip(im,1370,320,1,420,'panic','panic');im.save(p/'avalanche.png')
    im=backdrop().copy();d=ImageDraw.Draw(im)
    heading(d,'THE PERFORMANCE REVIEW','The answer was in the envelope.','Illustrative layout — final shot uses the actual response.')
    record(d,130,390);pip(im,1190,330,2,450,'annoyed','shrug');stamp(im,(490,610),'EXTRA WORDS')
    im.save(p/'review.png')

if __name__=='__main__':proof()
