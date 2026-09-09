"""Directed shots with internal beats, physical props, and evidence-bound charts."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw
from .art import *

NAMES=['GPT-4o Mini','GPT-4.1 Mini','GPT-5.6 Luna','Claude Haiku 4.5']
MODELS=['gpt-4o-mini-2024-07-18','gpt-4.1-mini-2025-04-14','gpt-5.6-luna','claude-haiku-4-5-20251001']
COLORS=[GOLD,BLUE,MINT,RED]

def scoretiles(d,x,y,values,t,start=.6,size=34,columns=16):
    seen=max(0,int((t-start)*13))
    for i,ok in enumerate(values):
        xx=x+(i%columns)*(size+9);yy=y+(i//columns)*(size+9)
        color=(MINT if ok else RED) if i<seen else '#D7D9CE'
        rr(d,(xx,yy,xx+size,yy+size),color,5)
        if i<seen:
            if ok:d.line([(xx+7,yy+size/2),(xx+size*.43,yy+size-8),(xx+size-6,yy+7)],fill=INK,width=3)
            else:d.line((xx+9,yy+9,xx+size-9,yy+size-9),fill=INK,width=3)

def subtitle_note(d,s,dark=False,y=831):text(d,(100,y),s,25,MINT if dark else MUTED)

def render(s,t,summary=None):
    kind=s['kind'];q=min(1,t/s['duration']);dark=kind in ('avalanche','title','grow','primary','uncertainty','end','credits')
    im=backdrop('office' if kind=='office' else 'dark' if dark else 'paper').copy();d=ImageDraw.Draw(im)
    if kind!='office':signature(d,dark)
    if kind=='office':
        if s['id'].startswith('19'):
            rr(d,(650,360,1320,520),WHITE,8,INK,3);text(d,(985,440),'DEPARTMENT OF TWO ARROWS',29,INK,'bold','mm')
            pip(im,830,430,t,350,'neutral','shrug')
            folder(d,420,590,280,175,title='MORE PAPERWORK')
        else:
            folder(d,490,550,320,210,title='ONE SMALL JOB')
            pip(im,830,330,t,450,'happy','point')
            if t>6:stamp(im,(795,747),'OPEN FOR BUSINESS',-4,INK,.72)
            if t<5:text(d,(100,1012),'Original animation • AI-generated stock voices',22,MUTED)
    elif kind=='avalanche':
        text(d,(110,75),'8,192 files.',112,WHITE,'serif');text(d,(117,235),'One increasingly nervous clerk.',42,MINT,'italic')
        amount=int(lerp(3,105,out(t/4)))
        for i in range(amount):
            col=i%21;row=i//21
            xx=45+col*91;yy=lerp(-150,475+row*73,out(max(0,t-i*.022)/.8))
            folder(d,xx,yy,83,65,color=[GOLD,MINT,BLUE][i%3])
        pip(im,1380,330,t,430,'panic','panic')
        if t>6:label(d,(125,353),'THE ANSWER IS ACTUALLY IN HERE',MINT,INK,26)
    elif kind=='pip_close':
        # An editorial punch-in, with room to hold the deadpan reaction after speech.
        pip(im,580,130,t,630,s.get('mood','annoyed'),'shrug',.15<t<s.get('speech_duration',s['duration']-.7)+.15)
        label(d,(115,136),'PIP / TEMPORARY PERMANENT STAFF',GOLD,INK,23)
        if s['id'].startswith('26'):folder(d,1360,630,290,180,title='RE: LESS PAPER')
        elif s['id'].startswith('09'):text(d,(1320,550),'4 ≠ 7',70,RED,'serif')
    elif kind=='title':
        label(d,(112,105),'AN EXPERIMENT IN LOST & FOUND',MINT,INK,25)
        text(d,(100,260),'AI vs the',118,WHITE,'serif');text(d,(100,405),'filing cabinet.',118,WHITE,'serif')
        text(d,(110,645),'A very small office. A very large prompt.',38,MINT,'italic')
        cabinet(d,1430,280,.9,'#6C9788');pip(im,1230,425,t,360,'annoyed','point')
        text(d,(110,805),'GPT LEARNING  /  CONTEXTFRONTIER',24,WHITE,'bold')
    elif kind=='record':
        heading(d,'THE JOB','Find one fact.','Synthetic records • the answer must come from this prompt')
        record(d,120,375,'BSFV|DPEY','KBJI|EVEB',tag='ONE KEY → ONE VALUE')
        x=lerp(1750,1040,out(t/1.2));folder(d,x,400,610,250,MINT,title='QUERY: BSFV|DPEY')
        if q>.45:
            label(d,(1170,697),'RETURN: KBJI|EVEB',INK,WHITE,32)
            arrow(d,(670,610),(1170,690),RED,5)
        subtitle_note(d,'If the key is absent, the requested answer is UNKNOWN.')
    elif kind=='cast':
        heading(d,'THE APPLICANTS','Four configured systems.','A mix of older and newer API models')
        details=[('2024-07-18','temperature 0'),('2025-04-14','temperature 0'),('gpt-5.6-luna','reasoning none'),('2025-10-01','temperature 0')]
        for i,(name,color,(date,setting)) in enumerate(zip(NAMES,COLORS,details)):
            x=95+i*445;y=350+round(45*(1-out((t-i*.18)/.6)))
            rr(d,(x,y,x+415,y+395),WHITE,15,LINE,2);rr(d,(x,y,x+415,y+18),color,5)
            text(d,(x+28,y+47),name,33,INK,'bold');text(d,(x+28,y+108),date,26,MUTED,'mono')
            folder(d,x+115,y+177,178,113,color)
            text(d,(x+28,y+327),setting,25,INK,'mono')
        subtitle_note(d,'Sampling differs by configured model; this is not an isolated test of model age.')
    elif kind=='nested':
        heading(d,'FAIRER FILES','Same fact. More clutter.','Increasing length preserves the target and the distractor pool prefix.')
        for j,(n,amt) in enumerate([(128,8),(4096,17),(8192,25)]):
            y=376+j*143;text(d,(103,y+22),f'{n:,}',43,INK,'bold')
            seen=min(amt,max(0,int((t-j*.5)*10)))
            for i in range(amt):
                x=410+i*52;rr(d,(x,y,x+44,y+78),MINT if i==4 else GOLD if i<seen else LINE,4)
                if i==4:text(d,(x+22,y+38),'★',25,INK,'sans','mm')
            d.line((400,y+90,1745,y+90),fill=INK,width=3)
        subtitle_note(d,'Moving the target changes placement, while preserving all records.')
    elif kind=='tokens':
        heading(d,'FIRST: AUDIT THE TOOL','Four symbols. Seven tokens.','Local example from the legacy inventory • o200k_base tokenizer')
        pieces=['pson','|','lp','|','ourt','|','pell'];widths=[230,95,170,95,230,95,230];x=150
        for i,(piece,ww) in enumerate(zip(pieces,widths)):
            color=GOLD if piece=='|' else MINT
            yy=410+round(25*(1-out((t-i*.12)/.5)))
            rr(d,(x,yy,x+ww,yy+142),color,10,INK,2);text(d,(x+ww/2,yy+69),piece,53,INK,'mono','mm')
            if t>2.3:text(d,(x+ww/2,yy+190),i+1,35,INK,'bold','mm')
            x+=ww+19
        if q>.52:label(d,(200,738),'MODEL-SPECIFIC REQUEST COUNT → ACTUAL USAGE',INK,WHITE,31)
        subtitle_note(d,'The legacy example is not the four-letter code inventory used in the new games.')
    elif kind=='warmup':
        heading(d,'ROUND ONE','A very brief moment of confidence.','128 records • present-key lookup at 10%, 50%, and 90%')
        for i,name in enumerate(NAMES):
            y=354+i*94;text(d,(112,y),name,37,INK,'bold')
            label(d,(650,y),'24 / 24' if i<3 else '12 / 12',MINT,INK,31)
        pip(im,1210,350,t,395,'happy','point')
        if q>.45:stamp(im,(1090,716),'EMPLOYEE OF THE MOMENT',-7,INK,.5)
        subtitle_note(d,'Different panel sizes are shown explicitly. These are the easy conditions.')
    elif kind=='grow':
        n=128 if q<.2 else 4096 if q<.52 else 8192
        text(d,(105,110),'The cabinet gets bigger.',79,WHITE,'serif')
        for row in range(8):
            for col in range(27):
                x=70+col*66;y=340+row*52
                fill=MINT if (row,col)==(5,23) else '#36555A'
                rr(d,(x,y,x+57,y+43),fill,3)
        rr(d,(110,357,960,686),INK,12)
        text(d,(145,378),f'{n:,}',134,WHITE,'bold');text(d,(153,558),'records in one request',38,MINT)
        if q>.52:text(d,(1060,555),'≈111,000',76,GOLD,'bold');text(d,(1065,662),'GPT input tokens',34,WHITE)
        subtitle_note(d,'Same text across models; different tokenizers produce different counts.',True)
    elif kind=='prediction':
        heading(d,'YOUR TURN','Where would you hide the fact?','Take a guess before the reveal.')
        d.line((220,525,1700,525),fill=INK,width=6)
        for i,(name,pos) in enumerate([('BEGINNING','10%'),('MIDDLE','50%'),('END','90%')]):
            x=210+i*625;folder(d,x-95,425,270,165,[GOLD,BLUE,MINT][i],title=pos)
            text(d,(x+35,680),name,31,INK,'bold','mm')
            if s['duration']-t<2.7:
                d.ellipse((x+11,355,x+61,405),outline=INK,width=3);text(d,(x+36,381),'?',32,INK,'bold','mm')
        subtitle_note(d,'Percentages describe record position, not token position.')
    elif kind=='primary':
        heading(d,'PRESPECIFIED COMPARISON','Same prompts. Different afternoons.','8,192 records • target at 90% • 32 fresh seeds',True)
        for j,model in enumerate([MODELS[0],MODELS[2]]):
            p=summary['primary'][model];x=110+j*910
            text(d,(x,363),NAMES[0 if j==0 else 2],46,WHITE,'bold')
            scoretiles(d,x,462,p['exact_by_seed'],t,.8,39,16)
            if t>3.5:text(d,(x,610),f"{p['exact']} / {p['n']}",115,GOLD if j==0 else MINT,'bold')
        subtitle_note(d,'One square per seed • exact correct delivery per dispatched request',True)
    elif kind=='failure':
        e=s['example'];key,val=e['evidence'][0]['text'].split(' => ')
        heading(d,'EXHIBIT A','The missing answer was present.',f"Actual GPT-4o Mini response • seed {e['seed']} • {e['input_tokens']:,} input tokens")
        record(d,108,355,key,val,tag=f"RECORD {e['evidence'][0]['line']+1:,} OF 8,192")
        rr(d,(1040,386,1760,630),WHITE,12,INK,3)
        text(d,(1400,441),'RETURNED',26,MUTED,'bold','mm');text(d,(1400,538),e['response'],76,RED,'mono','mm')
        arrow(d,(815,473),(986,473),RED,6)
        if q>.55:stamp(im,(1050,666),'WRONG ANSWER',-6,RED,.85)
        subtitle_note(d,'The request completed normally; UNKNOWN is syntactically valid but incorrect here.')
    elif kind=='positions':
        heading(d,'MOVE THE SAME FACT','Three positions. One model.','GPT-4o Mini • 8,192 records • 32 seeds at each position')
        for i,depth in enumerate([.1,.5,.9]):
            c=next(c for c in summary['cells'] if c['model']==MODELS[0] and c['task']=='needle' and c['n_records']==8192 and c['depth']==depth and not c['absent'])
            x=210+i*570;yy=700;hh=315*c['exact']/32*ease((t-i*.3)/1.3)
            rr(d,(x,yy-315,x+240,yy),LINE,8)
            if hh>0:rr(d,(x,yy-hh,x+240,yy),GOLD,8)
            text(d,(x+120,335),f"{c['exact']} / 32",60,INK,'bold','mm');text(d,(x+120,757),['10% / beginning','50% / middle','90% / end'][i],29,INK,'sans','mm')
        subtitle_note(d,'Descriptive secondary result. Shared seeds make these conditions correlated.')
    elif kind=='middle':
        p=summary['primary'][MODELS[1]];heading(d,'THE MODEL BETWEEN THEM','GPT-4.1 Mini','The same 8,192-record, 90%-position comparison')
        scoretiles(d,115,400,p['exact_by_seed'],t,.4,52,16)
        text(d,(117,605),f"{p['exact']} / 32",111,INK,'bold');pip(im,1320,375,t,360,'neutral','point')
        subtitle_note(d,'Specific versions and settings; not a causal estimate of model age or architecture.')
    elif kind=='claude':
        heading(d,'A SMALLER CLAUDE PANEL','Four cases per position.','Claude Haiku 4.5 • 8,192 records • seeds 4101–4104')
        for i,depth in enumerate([.1,.5,.9]):
            c=next(c for c in summary['shared_claude'] if c['model']==MODELS[3] and c['n_records']==8192 and c['depth']==depth)
            x=150+i*590;text(d,(x,365),['Beginning','Middle','End'][i],44,INK,'bold')
            # Count tiles, deliberately not assigned to specific seeds here.
            for j in range(4):rr(d,(x+j*94,468,x+j*94+77,545),MINT if j<c['exact'] else RED,9)
            text(d,(x,598),f"{c['exact']} / 4",98,INK,'bold')
        subtitle_note(d,'Count tiles, not seed order. Small n; the report includes comparisons on shared cases.')
    elif kind=='uncertainty':
        heading(d,'LEAVE ROOM FOR DOUBT','A score is not a law of nature.','95% Wilson intervals across the 32 fresh seeds',True)
        for x,label_text in [(590,'0%'),(1155,'50%'),(1720,'100%')]:text(d,(x,329),label_text,25,MINT,'mono','mm')
        for j,model in enumerate([MODELS[0],MODELS[2]]):
            p=summary['primary'][model];lo,hi=p['wilson95'];y=447+j*214
            text(d,(105,y-69),NAMES[0 if j==0 else 2],38,WHITE,'bold')
            d.line((590,y,1720,y),fill='#53706E',width=3)
            xx=590+1130*lo;xe=590+1130*hi
            d.line((xx,y,xe,y),fill=GOLD if j==0 else MINT,width=16)
            for x in (xx,xe):d.line((x,y-22,x,y+22),fill=WHITE,width=3)
            text(d,(590,y+44),f"{lo*100:.1f}%–{hi*100:.1f}%",36,WHITE,'mono')
        subtitle_note(d,'Intervals describe seed sampling in this synthetic condition, not all possible uses.',True)
    elif kind=='hops':
        e=s['example'];a,b=e['evidence'][0]['text'].split(' => ');_,c=e['evidence'][1]['text'].split(' => ')
        heading(d,'NEW JOB: TWO HOPS','A → B → C. Return C.','Actual records from the Claude response shown next')
        for i,(code,col,tag) in enumerate([(a,GOLD,'START'),(b,BLUE,'INTERMEDIATE'),(c,MINT,'ANSWER')]):
            x=100+i*625;rr(d,(x,409,x+470,645),col,12,INK,3);text(d,(x+235,457),tag,24,INK,'bold','mm');text(d,(x+235,552),code,39,INK,'mono','mm')
            if i<2:arrow(d,(x+490,525),(x+602,525),INK,6)
        x=lerp(300,1600,min(1,max(0,(t-1)/4)));d.ellipse((x-13,715,x+13,741),fill=RED)
        subtitle_note(d,'128 records • two evidence records at nominal 25% and 75% positions')
    elif kind=='printer':
        e=s['example'];heading(d,'THE PERFORMANCE REVIEW','Correct answer. Unwanted guided tour.','Actual Claude Haiku response; line wrapping adapted for the screen')
        # Paper unroll is a reveal of the original response, not fabricated model dialogue.
        lines=[]
        for line in e['response'].splitlines():lines.extend(wrap(line,1030,24,'mono') if line else [''])
        nlines=len(lines);lead=min(29,440/max(1,nlines));full=round(lead*nlines+58)
        sheet=Image.new('RGB',(1120,full),WHITE);sd=ImageDraw.Draw(sheet)
        for i,line in enumerate(lines):text(sd,(34,20+i*lead),line,24,INK,'mono')
        reveal=min(full,max(28,round(full*out(t/3))));im.paste(sheet.crop((0,0,1120,reveal)),(100,342))
        rr(d,(90,310,1230,349),INK,9)
        text(d,(1290,381),'LAST LINE',25,MUTED,'bold')
        text(d,(1290,438),e['expected'][0],43,INK,'mono')
        if t>3.2:label(d,(1290,541),'CORRECT',MINT,INK,27)
        if q>.48:stamp(im,(1230,657),'EXTRA WORDS',-9,RED,.7)
    elif kind=='scores':
        f=next(x for x in summary['format_pairs'] if x['model']==MODELS[3] and x['task']=='two_hop');m=f['measures']
        heading(d,'TWO MEASUREMENTS','One red stamp cannot explain both.','Claude Haiku • baseline wording • 16 two-hop cases')
        for i,(title,key,col,desc) in enumerate([('EXACT DELIVERY','exact',RED,'Only the requested code'),('FINAL-LINE ANSWER','final_line_correct',MINT,'Standalone last code is correct')]):
            x=110+i*915;rr(d,(x,355,x+860,785),WHITE,13,LINE)
            text(d,(x+40,392),title,31,INK,'bold');text(d,(x+40,463),f"{m[key]['baseline']} / 16",108,col,'bold')
            text(d,(x+40,677),desc,31,INK)
        subtitle_note(d,'The final-line parser was defined before this run and does not see the answer key.')
    elif kind=='reminder':
        heading(d,'ONE CONTROLLED CHANGE','Enter: the sticky note.','Baseline and reminder share the same records and expected answer.')
        rr(d,(195,366,1715,768),GOLD,4)
        block(d,(265,408),'Return only the requested code, on one line, with no explanation, labels, or Markdown.',1320,53,INK,'bold',1.38)
        d.polygon([(1654,707),(1715,707),(1654,768)],fill='#E8A83B')
        subtitle_note(d,'This changes the prompt wording. It does not change the tested model’s reasoning setting.')
    elif kind in ('format_result','revision_result'):
        task='two_hop' if kind=='format_result' else 'updates'
        heading(d,'PAIRED PROMPT EXPERIMENT','Did the reminder help?','16 pairs per model • baseline → reminder • counts of correct deliveries')
        text(d,(655,343),'EXACT DELIVERY',27,INK,'bold');text(d,(1212,343),'FINAL-LINE ANSWER',27,INK,'bold')
        for i,(model,name) in enumerate(zip(MODELS,NAMES)):
            f=next(x for x in summary['format_pairs'] if x['model']==model and x['task']==task);y=412+i*95
            rr(d,(95,y-8,1790,y+73),WHITE,8)
            text(d,(120,y+11),name,32,INK,'bold')
            for j,key in enumerate(['exact','final_line_correct']):
                v=f['measures'][key];x=667+j*562
                text(d,(x,y+3),f"{v['baseline']} → {v['reminder']}",43,INK,'mono')
                text(d,(x+288,y+15),'/ 16',26,MUTED)
            spotlight=(i==3 if task=='two_hop' else i==2)
            if spotlight:rr(d,(93,y-10,1792,y+75),None,8,GOLD,4)
        subtitle_note(d,('Two-hop lookup' if task=='two_hop' else 'Highest-revision selection')+' • secondary descriptive results; no universal prompt-tip claim')
    elif kind=='revision':
        heading(d,'NEW JOB: THE STALE MEMO','The highest revision wins.','Illustration of the rule used in the revision task')
        for i,(rev,col,txt) in enumerate([(9,MINT,'CURRENT ANSWER'),(2,GOLD,'OLDER ANSWER')]):
            x=115+i*935;rr(d,(x,369,x+825,701),col,12,INK,2)
            text(d,(x+37,408),f'REVISION {rev}',57,INK,'bold');text(d,(x+37,532),txt,38,INK,'mono')
            text(d,(x+37,626),'earlier in the file' if i==0 else 'later in the file',27,INK,'italic')
        if q>.4:stamp(im,(1050,706),'STALE SANDWICH POLICY',-4,RED,.52)
        subtitle_note(d,'The numerical revision, not the last matching record, determines the answer.')
    elif kind=='luna_stale':
        e=s['example'];heading(d,'THE STAR RETURNS TO THE OFFICE','A tiny file. An actual wrong answer.',f"GPT-5.6 Luna • 128 records • baseline wording • seed {e['seed']}")
        for i,(ev,col) in enumerate(zip(e['evidence'],[MINT,GOLD])):
            x=110+i*910;rev=ev['text'].split(':')[0].upper();value=ev['text'].split(' => ')[1]
            rr(d,(x,362,x+855,626),col,12,INK,2)
            text(d,(x+35,396),rev,43,INK,'bold');text(d,(x+35,488),value,56,INK,'mono')
            text(d,(x+35,569),'current / expected' if i==0 else 'stale / returned by Luna',27,INK,'bold')
        if q>.35:stamp(im,(1110,675),'CERTIFICATE REVOKED',-5,RED,.7)
        subtitle_note(d,'The actual output is exactly the stale value. This is not an extra-words failure.')
    elif kind=='rules':
        heading(d,'NAME THE FAILURE','Three different problems.','Inspect the response before inventing a story about memory.')
        for i,(title,sub,col) in enumerate([('RIGHT CODE + EXTRA WORDS','Delivery / format failure',GOLD),('UNKNOWN, BUT FACT PRESENT','Incorrect answer',RED),('OUTPUT DID NOT FINISH','Separate completion outcome',BLUE)]):
            y=357+i*151;rr(d,(104,y,1785,y+121),WHITE,12,LINE)
            rr(d,(104,y,124,y+121),col,4);text(d,(160,y+24),title,35,INK,'bold');text(d,(1020,y+32),sub,31,INK)
    elif kind=='method':
        heading(d,'MAKE IT CHECKABLE','Test the test. Keep the receipts.','ContextFrontier / FTAAT • second-edition experiment')
        for i,(a,b) in enumerate([('BEFORE','Protocol + fixed fresh seeds'),('DURING','Full prompts + unedited responses'),('AFTER','Counts + outcomes + provider budgets')]):
            y=365+i*149;label(d,(113,y+15),a,[GOLD,BLUE,MINT][i],INK,31);text(d,(440,y+21),b,43,INK,'bold')
        subtitle_note(d,f"{summary['total']['n']} substantive responses • smoke checks are separate • complete evidence in the report")
    elif kind=='limits':
        heading(d,'THE LIMIT OF THIS VIDEO','An obstacle course, not the whole world.','Synthetic codes test a particular kind of retrieval and rule-following.')
        rr(d,(112,370,1090,700),WHITE,12,INK,3)
        text(d,(155,410),'CONTEXT WINDOW',44,INK,'bold');text(d,(155,499),'Room for the text',53,INK,'serif')
        text(d,(155,601),'≠ a guarantee of task success',38,RED,'bold')
        cabinet(d,1340,346,.7);pip(im,1130,513,t,250,'annoyed','shrug')
        subtitle_note(d,'Results concern these model versions, sampling settings, prompts, and cases.')
    elif kind=='end':
        text(d,(112,125),'Check the filing',94,WHITE,'serif');text(d,(112,253),'before firing the clerk.',94,WHITE,'serif')
        for i,(word,col) in enumerate([('CHALLENGE',GOLD),('RULER',BLUE),('ANSWER',MINT)]):label(d,(120+i*518,466),word,col,INK,35)
        text(d,(120,695),'Code, protocol, and full evidence below.',37,WHITE)
        text(d,(120,799),'GPT LEARNING',30,MINT,'bold')
    elif kind=='chess':
        pip(im,350,256,t,510,'happy','point',.15<t<s.get('speech_duration',s['duration']-.7)+.15)
        folder(d,1170,419,530,324,GOLD,title='HORSES')
        text(d,(1435,283),'♞',180,INK,'sans','mm')
        label(d,(1065,779),'PIP HAS A SYSTEM',MINT,INK,28)
    elif kind=='credits':
        text(d,(960,196),'GPT LEARNING',67,WHITE,'bold','mm')
        text(d,(960,321),'AI vs the World’s Worst Filing Cabinet',46,MINT,'serif','mm')
        for i,line in enumerate(['Original procedural animation, character, script, and sound design.','AI-generated stock voices: Cedar (narrator), Onyx (Pip).','ContextFrontier / FTAAT • Protocol, model settings, and evidence linked below.','Experimental results are specific to the tested configurations.']):
            text(d,(960,479+i*78),line,29,WHITE,'sans','mm')
    else:raise ValueError(kind)
    # Fast cut with a tiny paper-colored fade only at the beginning of each shot.
    if t<.13:
        im=Image.blend(Image.new('RGB',(W,H),INK if dark else PAPER),im,out(t/.13))
    return im
