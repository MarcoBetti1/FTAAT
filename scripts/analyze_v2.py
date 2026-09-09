"""Deterministic, prespecified analysis of edition-two immutable event ledgers."""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
from contextfrontier.scoring_v2 import grade

ROOT=Path(__file__).resolve().parents[1]
MODELS=['gpt-4o-mini-2024-07-18','gpt-4.1-mini-2025-04-14','gpt-5.6-luna','claude-haiku-4-5-20251001']
NAMES=dict(zip(MODELS,['GPT-4o Mini','GPT-4.1 Mini','GPT-5.6 Luna','Claude Haiku 4.5']))
RUNS=['v2-openai-main','v2-claude-main','v2-openai-format','v2-claude-format']

def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,mid-half),min(1,mid+half)]

def hit(row,key):return bool((row['grade'] or {}).get(key,False))

def paired_contrast(aa,bb,expected_pairs=32):
    shared=sorted(set(aa)&set(bb));b=sum(aa[s] and not bb[s] for s in shared);c=sum(bb[s] and not aa[s] for s in shared);m=b+c
    pval=min(1,2*sum(math.comb(m,i) for i in range(min(b,c)+1))/2**m) if m else 1.
    return dict(complete_pairs=len(shared),expected_pairs=expected_pairs,old_only=b,new_only=c,
                both_correct=sum(aa[s] and bb[s] for s in shared),both_wrong=sum(not aa[s] and not bb[s] for s in shared),exact_two_sided_mcnemar_p=pval)

def tally(rows):
    n=len(rows);k=sum(hit(r,'exact') for r in rows)
    return dict(n=n,exact=k,final_line_correct=sum(hit(r,'final_line_correct') for r in rows),
                wilson95=wilson(k,n),status=dict(Counter(r['reply']['status'] for r in rows)),
                input_tokens=[min((r['actual_input_tokens'] for r in rows),default=0),max((r['actual_input_tokens'] for r in rows),default=0)])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--partial',action='store_true');a=ap.parse_args()
    cases={};rows=[];runs=[]
    for name in RUNS:
        p=ROOT/'results'/name
        if not (p/'manifest.json').exists():
            if a.partial:continue
            raise RuntimeError(f'Missing {name}')
        manifest=json.loads((p/'manifest.json').read_text());cc=[json.loads(l) for l in (p/'cases.jsonl').read_text().splitlines()]
        for c in cc:
            if c['id'] in cases:assert c==cases[c['id']]
            cases[c['id']]=c
        ev=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
        rr=[r for r in ev if r['event']=='result'];keys=[r['request_key'] for r in rr];assert len(set(keys))==len(keys)
        planned=len(cc)*len(manifest['config']['models']);errors=[r for r in ev if 'error' in r['event']];skips=[r for r in ev if r['event']=='skipped']
        planned_pairs={(c['id'],m['model']) for c in cc for m in manifest['config']['models']}
        observed_pairs={(r['case_id'],r['model']) for r in rr}
        assert observed_pairs<=planned_pairs and len(observed_pairs)==len(rr)
        if not a.partial:assert observed_pairs==planned_pairs,'Observed requests do not match the planned case/model grid'
        # Cross-check stored scores independently of the reporting aggregator.
        for r in rr:
            c=cases[r['case_id']];g=grade(r['reply']['text'],c['expected'],symbols_per_answer=c['k']) if r['reply']['status']=='completed' else None
            assert g==r['grade'],f"Score mismatch {r['request_key']}"
            r['run']=name
        item=dict(name=name,planned=planned,observed=len(rr),skipped=len(skips),error_events=len(errors),
                  unobserved=planned-len(rr)-len(skips),cost_upper_usd=str(sum((Decimal(r['cost_upper_usd']) for r in rr),Decimal(0))),
                  manifest_identity=manifest['identity'],source_revision=manifest['git_revision'],models=manifest['config']['models'],
                  ledger_sha256=hashlib.sha256((p/'events.jsonl').read_bytes()).hexdigest())
        if not a.partial and (item['unobserved'] or errors):raise RuntimeError(f'Incomplete stage requires explicit audit: {item}')
        rows+=rr;runs.append(item)
    groups=defaultdict(list)
    for r in rows:
        c=cases[r['case_id']]
        key=(r['model'],c['task'],c['n'],c['depth'],c['absent'],c['conditions']['query_style'])
        groups[key].append(r)
    cells=[]
    for key,rr in sorted(groups.items()):
        cells.append(dict(zip(['model','task','n_records','depth','absent','query_style'],key))|tally(rr))
    primary={}
    for model in MODELS[:3]:
        rr=[r for r in rows if r['model']==model and (c:=cases[r['case_id']])['task']=='needle' and c['n']==8192 and c['depth']==.9 and not c['absent']]
        rr.sort(key=lambda r:cases[r['case_id']]['seed'])
        primary[model]=tally(rr)|dict(seeds=[cases[r['case_id']]['seed'] for r in rr],exact_by_seed=[hit(r,'exact') for r in rr])
    paired=[]
    aa=dict(zip(primary[MODELS[0]]['seeds'],primary[MODELS[0]]['exact_by_seed']));bb=dict(zip(primary[MODELS[2]]['seeds'],primary[MODELS[2]]['exact_by_seed']))
    contrast=dict(models=[MODELS[0],MODELS[2]])|paired_contrast(aa,bb)
    for model in MODELS:
        for task in ('two_hop','updates'):
            rr=[r for r in rows if r['model']==model and cases[r['case_id']]['task']==task]
            pairmap=defaultdict(dict)
            for r in rr:
                c=cases[r['case_id']];pairmap[c['seed']][c['conditions']['query_style']]=r
            pp=[x for x in pairmap.values() if set(x)=={'baseline','reminder'}]
            counts={}
            for measure in ('exact','final_line_correct'):
                counts[measure]=dict(baseline=sum(hit(x['baseline'],measure) for x in pp),reminder=sum(hit(x['reminder'],measure) for x in pp),
                                    improved=sum(not hit(x['baseline'],measure) and hit(x['reminder'],measure) for x in pp),
                                    worsened=sum(hit(x['baseline'],measure) and not hit(x['reminder'],measure) for x in pp))
            paired.append(dict(model=model,task=task,pairs=len(pp),expected_pairs=16,measures=counts))
    shared_claude=[]
    for n in (128,8192):
        for depth in (.1,.5,.9):
            for model in MODELS:
                rr=[r for r in rows if r['model']==model and (c:=cases[r['case_id']])['task']=='needle' and c['n']==n and c['depth']==depth and not c['absent'] and 4101<=c['seed']<=4104]
                shared_claude.append(dict(model=model,n_records=n,depth=depth,seed_range=[4101,4104])|tally(rr))
    examples={}
    for task in ('two_hop','updates'):
        eligible=[r for r in rows if r['model']==MODELS[3] and (c:=cases[r['case_id']])['task']==task and c['conditions']['query_style']=='baseline' and not hit(r,'exact') and hit(r,'final_line_correct')]
        if eligible:
            r=min(eligible,key=lambda r:cases[r['case_id']]['seed']);c=cases[r['case_id']]
            match=next((q for q in rows if q['model']==r['model'] and (qc:=cases[q['case_id']])['task']==task and qc['seed']==c['seed'] and qc['conditions']['query_style']=='reminder'),None)
            examples[task]=dict(seed=c['seed'],case_id=c['id'],expected=c['expected'],evidence=c['evidence'],response=r['reply']['text'],grade=r['grade'],reminder_response=match['reply']['text'] if match else None,reminder_grade=match['grade'] if match else None)
    wrong=[r for r in rows if r['model']==MODELS[0] and (c:=cases[r['case_id']])['task']=='needle' and c['n']==8192 and c['depth']==.9 and not c['absent'] and not hit(r,'exact')]
    if wrong:
        r=min(wrong,key=lambda r:cases[r['case_id']]['seed']);c=cases[r['case_id']]
        examples['needle_failure']=dict(seed=c['seed'],case_id=c['id'],expected=c['expected'],evidence=c['evidence'],response=r['reply']['text'],grade=r['grade'],input_tokens=r['actual_input_tokens'])
    stale=[r for r in rows if r['model']==MODELS[2] and (c:=cases[r['case_id']])['task']=='updates' and c['conditions']['query_style']=='baseline' and not hit(r,'exact') and r['reply']['text'].strip()==c['evidence'][1]['text'].split(' => ')[1]]
    if stale:
        r=min(stale,key=lambda r:cases[r['case_id']]['seed']);c=cases[r['case_id']]
        examples['luna_stale_revision']=dict(seed=c['seed'],case_id=c['id'],expected=c['expected'],evidence=c['evidence'],response=r['reply']['text'],grade=r['grade'],input_tokens=r['actual_input_tokens'],selection='Lowest-seed baseline Luna response that returns the stale value; illustrative post-result selection, no new inferential contrast.')
    result=dict(protocol='docs/episodes/01-v2/PROTOCOL.md',partial=a.partial,models=NAMES,runs=runs,total=tally(rows),cells=cells,primary=primary,contrast=contrast,format_pairs=paired,shared_claude=shared_claude,examples=examples)
    out=ROOT/'docs/episodes/01-v2'/('partial-summary.json' if a.partial else 'summary.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(runs=[{k:v for k,v in r.items() if k not in ('models','manifest_identity','ledger_sha256')} for r in runs],primary=primary,format_pairs=paired),indent=2))

if __name__=='__main__':main()
