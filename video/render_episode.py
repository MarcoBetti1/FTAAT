"""Render the results episode from the audited live evidence bundle.
No generated examples are allowed to stand in for observed model responses.
Narration can use a local scratch voice or a disclosed stock OpenAI voice.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_preview as film


def model_label(name):
    return {'gpt-4o-mini-2024-07-18':'GPT-4o Mini','gpt-4.1-mini-2025-04-14':'GPT-4.1 Mini',
            'gpt-5.6-luna':'GPT-5.6 Luna','gpt-6-astra':'GPT-6 Astra',
            'claude-haiku-4-5-20251001':'Claude Haiku 4.5','claude-sonnet-5':'Claude Sonnet 5',
            'claude-opus-5':'Claude Opus 5'}.get(name,name)


def configure(bundle_path):
    bundle=json.loads(Path(bundle_path).read_text())
    if bundle['kind']!='observed_live_results': raise ValueError('Live evidence required')
    records=bundle['records']
    # Show the first actual format failure that contains the expected string.
    # Selection rule is explicit and leaves every outcome in the accompanying audit.
    selected=next((r for r in records if r['result']['grade'] and not r['result']['grade']['exact']
                   and r['expected_string_mentioned']),None)
    if selected is None: raise ValueError('No observed example supports this editorial treatment; rewrite before rendering')
    example=selected['result']; case=selected['case']
    retrieval=next((r for r in records if r['case']['task']=='needle' and not r['case']['absent'] and r['case']['n']>=4096 and r['result']['grade'] and r['result']['grade']['format_ok'] and not r['result']['grade']['exact'] and not r['expected_string_mentioned']),None)
    counts={}
    for row in records:
        r=row['result']; counts[r['model']]=counts.get(r['model'],0)+1
    completed=[r for r in records if r['result']['grade'] is not None]
    exact=sum(r['result']['grade']['exact'] for r in completed)
    malformed=sum(not r['result']['grade']['format_ok'] for r in completed)
    incomplete=sum(r['result']['reply']['status']=='incomplete' for r in records)
    refusals=sum(r['result']['reply']['status']=='refusal' for r in records)
    mentioned=sum(r['expected_string_mentioned'] and not r['result']['grade']['exact'] for r in completed)
    price=sum(float(r['result']['cost_upper_usd']) for r in records)
    models=len(counts)
    old_frame=film.frame
    game_names={'needle':'The missing file','two_hop':'Follow the paperwork','updates':'The stale memo','recall':'The entire inventory'}
    scenes=[]
    def add(kind,title,voice): scenes.append((kind,title,voice))
    add('case','The model found it. The score said zero.',
        f"Here is a real response from {model_label(example['model'])}. The correct answer is in the response. Our strict score still says zero. "
        "That sounds like a bad memory result. It is actually a warning about how easy it is to tell the wrong story with a benchmark.")
    add('desk','We gave AI more paperwork.',
        "Welcome to GPT Learning, our independent experiment notebook. Meet Pip, clerk at the Bureau of Misplaced Facts. "
        "Today we compare language models using deliberately artificial games. The full record list stays in the prompt while they answer. "
        "Memory is our visual shorthand. We are not measuring a hidden memory module or the model's internal attention weights.")
    add('token','Before testing AI, test the ruler.',
        "The project began as a fixed token attention test. But look at these four symbols. Each is one token in this tokenizer. "
        "Once we join them, the three separators count as well. The complete sequence has seven tokens. Four symbols and four model tokens are different measurements.")
    add('audit','Our first discovery was in our own code.',
        "We checked one thousand seeded four-symbol sequences from the original inventory, using the tokenizer mapped to GPT four O Mini. "
        "All one thousand used seven tokens. This is a local tokenizer measurement, not an inference result. "
        "Our old output allowance used the symbol count, so a long answer could run out of space for a reason we caused.")
    add('score','A perfect prefix is not a perfect answer.',
        "There was another problem. The old scoring helper could divide by the number of answers returned, instead of the number requested. "
        "Return one correct line and omit three, and a perfect prefix could look perfect. We fixed that. "
        "One out of four is twenty five percent. The missing lines still belong in the denominator.")
    add('fair','Same text. Model-specific token counts.',
        f"For the new experiment we used identical seeded records and deterministic answer keys. "
        f"This evidence bundle contains {len(records)} observed responses from {models} models. "
        "We counted each full request against the actual model using its official API, then saved the returned usage separately. "
        "We tested API models, not the ChatGPT and Claude websites. Settings and system prompts can make those products behave differently.")
    for game in ['needle','two_hop','updates','recall']:
        base_kind={'needle':'needle','two_hop':'hops','updates':'updates','recall':'recall'}[game]
        description={
            'needle':"Hide a random key and value among other records. Move that fact through the list. The negative control asks for a key that is absent and expects UNKNOWN. This tests literal retrieval. It does not prove the model can understand every kind of document.",
            'two_hop':"Now the first record points to a second key, and that second key points to the answer. Both clues are in the prompt. The task combines retrieval with following a short chain. We cannot attribute every failure to context length alone.",
            'updates':"Two records disagree. The higher revision number wins, even when the stale record appears later in the text. This adds a rule the model must apply. A wrong answer could reflect rule following, interference, or retrieval. The score by itself does not tell us which.",
            'recall':"Finally we request every value in shuffled order. More records also mean a longer answer. That changes two things at once. If generation hits the output limit, we mark it separately. Hitting the output cap is not evidence that the input was forgotten."
        }[game]
        add(base_kind,game_names[game],description)
        rows=[r for r in bundle['summary'] if r['task']==game and 'pilot-' in r['run']]
        n=sum(r['completed'] for r in rows); x=sum(r['exact'] for r in rows); f=sum(r['format_failures'] for r in rows)
        extra={
            'needle': "Every model passed every needle case in this small pilot, including the missing-key controls. Pip has briefly become insufferable. But these prompts had only sixteen or one hundred twenty eight records. Passing this version does not establish reliability at a hundred thousand tokens.",
            'two_hop': "Haiku has no strict passes here, but all eighteen of its responses have a formatting problem. That is a giant sign saying: read the answers. GPT four O Mini also makes errors in correctly shaped outputs. Those are different behaviors, even when the score paints both of them red.",
            'updates': "Haiku and Luna follow the requested contract throughout this pilot. GPT four O Mini has nine strict failures, all flagged for formatting. The filing cabinet is sometimes finding the paperwork and delivering the entire folder when we asked for one label. The response audit keeps that distinction visible.",
            'recall': "Two GPT four O Mini requests hit the output limit, and are shown as other outcomes rather than memory failures. GPT four point one Mini passes its six trials. Six is a small number. These games are useful for finding questions to investigate, not for awarding a permanent intelligence trophy."
        }[game]
        add('results_'+game,'Observed results / '+game_names[game],
            f"In the matched four-model pilot for this game, {x} of {n} completed responses matched the requested output exactly. " + extra)
        if game=='needle' and retrieval:
            rr=retrieval['result']; cc=retrieval['case']
            if (cc['n'],rr['actual_input_tokens']) != (8192,111513):
                raise ValueError('Rewrite the spoken numbers for the newly selected observed case')
            add('retrieval_case','A fact that really was in the prompt.',
                f"Here is a different kind of result. In this {model_label(rr['model'])} trial, the model returned {rr['reply']['text']}. "
                "The target record was present among eight thousand, one hundred and ninety two records, "
                "with one hundred and eleven thousand, five hundred and thirteen actual input tokens. "
                "The API completed normally. This is a wrong answer on this specific test, not just extra formatting. "
                "It is one observation, not an estimated failure rate. The full prompt and evidence location are saved so it can be checked.")

    confirmations=[r for r in records if 'confirm-' in r['run']]
    confirmation_stats={}
    for item in confirmations:
        r=item['result']; group=confirmation_stats.setdefault(r['model'],[0,0])
        if r['grade'] is not None:
            group[0]+=r['grade']['exact'];group[1]+=1
    old=confirmation_stats.get('gpt-4o-mini-2024-07-18',[0,0])
    new=confirmation_stats.get('gpt-5.6-luna',[0,0])
    add('confirmation','Fresh records. A reproducible contrast.',
        f"We checked that long-context needle condition with fresh seeds. GPT four O Mini answered {old[0]} of {old[1]} correctly. "
        f"GPT five point six Luna answered {new[0]} of {new[1]} correctly. "
        "Both got identical text: eight thousand one hundred ninety two records, with the target near the end. "
        "All these API responses completed normally. The samples are small, and this condition was chosen after exploration. "
        "This supports a specific reproducible contrast. It does not mean one model has a universal memory limit or never makes mistakes.")
    add('totals','What this run actually supports.',
        f"The full bundle has {exact} exact successes out of {len(completed)} completed responses. "
        f"{malformed} completed responses have formatting problems. {incomplete} responses hit an output limit, and {refusals} were refusals. "
        f"In {mentioned} strict failures on single-answer tasks, the expected string still appears somewhere in the output. "
        "That is why a single red square is not enough evidence for the headline that a model forgot.")
    current_records=[r for r in records if 'current-' in r['run']]
    current_refusals=sum(r['result']['reply']['status']=='refusal' for r in current_records)
    long_records=[r for r in records if 'long-' in r['run']]
    peak=max((r['result']['actual_input_tokens'] for r in long_records),default=0)
    add('panels','The newer models got their own panel.',
        f"We also collected {len(current_records)} responses in a separate small current-model panel. "
        f"{current_refusals} were refusals, not scored memory failures. "
        f"The separate long-context exploration reached {peak} actual input tokens. "
        "That exploration stopped at its allocated budget, so not every planned comparison is complete. "
        "We do not combine these different panels into a fair-looking seven-model leaderboard.")
    add('limits','A small experiment, not an intelligence ranking.',
        "The random codes are intentionally arbitrary. Tokenization differs, reasoning settings differ, and our smallest cells have only a few seeds. "
        "Latency is affected by caching and provider load. Older does not always mean cheaper. "
        "The report keeps per-condition counts and uncertainty intervals, while these overview bars are only descriptive. "
        "Our fresh-seed check is a start. A stronger follow-up would use more seeds, more positions, and meaningful documents as well as random codes.")
    add('end_results','Publish the paperwork. Keep asking better questions.',
        f"The conservative token-cost estimate for these responses is {price:.2f} dollars. "
        "The code, prompts, scoring rules, and complete response audit accompany the report. "
        "This first experiment taught us to check both the model and the measuring instrument. "
        "Sometimes the most interesting result is not that artificial intelligence failed. It is that our explanation was too simple. Pip would like that entered into the record.")
    film.SCENES=scenes
    def draw(kind,title,subtitle,t,progress,index):
        base=old_frame(kind if not kind.startswith('results_') else 'fair',title,subtitle,t,progress,index)
        d=film.canvas(base)
        # Results rough cut label replaces the rehearsal label.
        d.rectangle((855,20,1240,66),fill=film.PAPER)
        film.text(d,(1225,40),'OBSERVED DATA / AI-GENERATED NARRATION',13,fill=film.GRAY,anchor='ra')
        if kind=='case':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            film.text(d,(75,192),model_label(example['model'])+'  /  '+case['task']+f"  /  N = {case['n']}",20,fill=film.GRAY)
            film.card(d,75,242,430,100,'EXPECTED: '+case['expected'][0],film.MINT,24)
            film.text(d,(75,382),'Strict output: FAIL',28,bold=True)
            film.text(d,(75,433),'Expected string: PRESENT',24,bold=True)
            response=example['reply']['text']
            import textwrap
            shown=textwrap.wrap(response.replace('\n','  '),47)[:8]
            film.card(d,555,237,645,295,'',film.PAPER)
            for i,line in enumerate(shown):film.text(d,(580,258+i*29),line,21)
            film.text(d,(75,554),'Case '+case['id'][:16]+'  |  full response in the audit',16,fill=film.GRAY)
        elif kind=='retrieval_case' and retrieval:
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            rr=retrieval['result']; cc=retrieval['case']
            film.text(d,(75,196),model_label(rr['model'])+f" / {rr['actual_input_tokens']:,} input tokens",24,fill=film.GRAY)
            film.card(d,75,257,1100,90,cc['evidence'][0]['text'],film.MINT,34)
            film.text(d,(75,371),f"PRESENT at record {cc['evidence'][0]['line']+1:,} of {cc['n']:,}",23)
            film.card(d,75,430,670,80,'MODEL ANSWER: '+rr['reply']['text'],film.GOLD,25)
            film.text(d,(780,447),'Completed API response',21)
            film.text(d,(75,550),'One observed case: '+cc['id'][:16]+' / no failure-rate claim',17,fill=film.GRAY)
        elif kind.startswith('results_'):
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            task=kind[len('results_'):]
            rows=[r for r in bundle['summary'] if r['task']==task and 'pilot-' in r['run']]
            by={}
            for r in rows:
                b=by.setdefault(r['model'],[0,0,0,0]); b[0]+=r['exact'];b[1]+=r['completed'];b[2]+=r['format_failures'];b[3]+=r['other_outcomes']
            h=min(48,320/max(1,len(by)))
            for i,(model,(x,n,f,other)) in enumerate(sorted(by.items())):
                y=215+i*h
                film.text(d,(75,y),model_label(model),22)
                d.rounded_rectangle((360,y,930,y+27),radius=5,fill='#DFDDD4')
                length=570*(x/n if n else 0)*min(1,t/1.5)
                if length>0:d.rounded_rectangle((360,y,360+length,y+27),radius=5,fill=film.MINT)
                film.text(d,(956,y),(f'{x}/{n} | fmt {f} | other {other}' if n else f'NO SCORED ANSWER | other {other}'),16)
            film.text(d,(75,556),'Matched pilot only / same cases per model / other = unscored API outcome',19,fill=film.GRAY)
        elif kind=='confirmation':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            film.text(d,(80,202),'8,192 records / target near the end / fresh seeds / identical text',23,fill=film.GRAY)
            for i,(name,stat) in enumerate([('GPT-4o Mini',old),('GPT-5.6 Luna',new)]):
                x=90+i*625
                film.text(d,(x,265),name,34,bold=True)
                film.text(d,(x,328),f'{stat[0]} / {stat[1]}',91,bold=True)
                film.text(d,(x,454),'exact requested answers',25)
            film.text(d,(80,535),'Small selected-condition check. Not a universal failure-rate estimate.',21,fill=film.GRAY)
        elif kind=='totals':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            labels=[(str(len(records)),'observed responses'),(str(exact),'strict exact successes'),(str(malformed),'format failures'),(str(incomplete+refusals),'output-limited or refused')]
            for i,(v,label) in enumerate(labels):
                x=95+(i%2)*610;y=212+(i//2)*175
                film.text(d,(x,y),v,74,bold=True);film.text(d,(x,y+90),label,25)
        elif kind=='panels':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            film.text(d,(85,205),'CURRENT PANEL',20,fill=film.GRAY,bold=True)
            names=sorted({r['result']['model'] for r in current_records})
            for i,name in enumerate(names):
                subset=[r['result'] for r in current_records if r['result']['model']==name]
                nr=sum(r['reply']['status']=='refusal' for r in subset)
                done=[r for r in subset if r['grade'] is not None]
                nx=sum(r['grade']['exact'] for r in done)
                film.text(d,(85,250+i*60),model_label(name),28,bold=True)
                film.text(d,(470,252+i*60),(f'{nx}/{len(done)} exact | {nr} refusals' if done else f'No scored answers | {nr} refusals'),25)
            film.text(d,(85,486),f'Long-context exploration: up to {peak:,} actual input tokens',26,bold=True)
            film.text(d,(85,545),'Separate conditions. Budget-stopped exploration. No combined ranking.',20,fill=film.GRAY)
        elif kind=='limits':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            for i,line in enumerate(['Synthetic codes are not real documents.','A few seeds give wide uncertainty.','Output format is a separate behavior.','API models are not the consumer apps.']):
                film.text(d,(100,225+i*78),line,31,bold=True)
        elif kind=='end_results':
            d.rectangle((55,180,1220,580),fill=film.PAPER)
            film.text(d,(90,218),f'${price:.2f}',94,bold=True)
            film.text(d,(90,333),'conservative token-cost estimate',26)
            film.text(d,(90,418),'Code + method + complete response audit',28,bold=True)
            film.text(d,(90,493),'github.com/MarcoBetti1/FTAAT',24)
            film.pip(d,1060,260,t,1.1)
        return base
    film.frame=draw
    return dict(responses=len(records),models=models,exact=exact,format_failures=malformed,selected_case=case['id'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence',required=True);p.add_argument('--output',default='artifacts/episode-01');p.add_argument('--skip-mux',action='store_true');p.add_argument('--stills-only',action='store_true');p.add_argument('--voice-engine',choices=['local','openai'],default='local');a=p.parse_args()
    info=configure(a.evidence)
    sys.argv=[sys.argv[0],'--output',a.output,'--voice-engine',a.voice_engine]+(['--stills-only'] if a.stills_only else [])+(['--skip-mux'] if a.skip_mux else [])
    film.main()
    out=Path(a.output)
    if not a.stills_only and not a.skip_mux:
        (out/'GPT-Learning-method-preview.mp4').rename(out/'GPT-Learning-01-results-rough-cut.mp4')
    (out/'editorial-selection.json').write_text(json.dumps(info,indent=2)+'\n')
