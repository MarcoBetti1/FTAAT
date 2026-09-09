"""Build a descriptive, traceable editorial evidence bundle from real event ledgers."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contextfrontier.runner import read_rows
from contextfrontier.scoring import grade, VERSION


def build(directories, output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    groups=defaultdict(list); records=[]
    for directory in directories:
        root=Path(directory)
        manifest=json.loads((root/'manifest.json').read_text())
        if not manifest['live']: raise ValueError('Cannot use dry run as episode results')
        cases={c['id']:c for c in read_rows(root/'cases.jsonl')}
        for row in read_rows(root/'events.jsonl'):
            if row['event']!='result': continue
            case=cases[row['case_id']]
            row['stored_grade']=row['grade']
            if row['reply']['status']=='completed':
                row['grade']=grade(row['reply']['text'],case['expected'],symbols_per_answer=case['k'])
            row['analysis_scoring_version']=VERSION
            item=dict(run=root.name,case=case,result=row)
            # Post-hoc editorial diagnostic, NOT a replacement for the prespecified score.
            # Merely mentioning an expected string does not guarantee it is the chosen answer.
            expected=case['expected']
            item['expected_string_mentioned']=len(expected)==1 and bool(re.search(
                r'(?<![A-Z|])'+re.escape(expected[0])+r'(?![A-Z|])',row['reply']['text']))
            records.append(item)
            groups[(root.name,row['model'],case['task'],case['n'])].append(item)
    summary=[]
    for (run_name,model,task,n),items in sorted(groups.items()):
        done=[i for i in items if i['result']['grade'] is not None]
        exact=sum(i['result']['grade']['exact'] for i in done)
        formats=sum(not i['result']['grade']['format_ok'] for i in done)
        mentioned=sum(i['expected_string_mentioned'] and not i['result']['grade']['exact'] for i in done)
        summary.append(dict(run=run_name,model=model,task=task,n=n,completed=len(done),exact=exact,
                            format_failures=formats,expected_mentioned_but_not_exact=mentioned,
                            other_outcomes=len(items)-len(done),
                            refusals=sum(i['result']['reply']['status']=='refusal' for i in items),
                            incomplete=sum(i['result']['reply']['status']=='incomplete' for i in items)))
    bundle=dict(scoring_version=VERSION,kind='observed_live_results',aggregation='Descriptive pooled counts, not independent-trial inference',
                diagnostic='Expected-string mention is post-hoc, not semantic correctness',summary=summary,records=records)
    (output/'evidence.json').write_text(json.dumps(bundle,indent=2)+'\n')
    lines=['# Episode evidence ledger','','Only observed live results. Strict score and post-hoc diagnostics are distinct.','',
           '| Run / Model | Game | N | Exact / completed | Format failures | Expected mentioned despite strict failure | Other (refusal / incomplete) |',
           '|---|---|---:|---:|---:|---:|---:|']
    for g in summary:
        lines.append(f"| {g['run']} / {g['model']} | {g['task']} | {g['n']} | {g['exact']}/{g['completed']} | {g['format_failures']} | {g['expected_mentioned_but_not_exact']} | {g['other_outcomes']} ({g['refusals']} / {g['incomplete']}) |")
    lines += ['', 'Counts pool depths for editorial overview only. Reused seeds make those requests correlated; see per-cell reports for intervals.','',
              '## Complete non-exact response audit','']
    for item in records:
        r=item['result']; c=item['case']
        if r['grade'] is not None and r['grade']['exact']: continue
        lines += [f"### {r['model']} / {c['task']} / N={c['n']} / seed={c['seed']} / depth={c['depth']}",
                  f"Run: `{item['run']}`; case: `{c['id']}`; request: `{r['request_key']}`.",
                  f"API status: `{r['reply']['status']}`. Post-hoc expected-string mention: {item['expected_string_mentioned']}.",
                  'Expected:', '```text','\n'.join(c['expected']),'```','Response:','```text',r['reply']['text'],'```','']
    (output/'audit.md').write_text('\n'.join(lines))
    return bundle


def plot(bundle, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    rows=bundle['summary']; models=sorted({x['run']+' / '+x['model'] for x in rows})
    cols=sorted({(x['task'],x['n']) for x in rows})
    data=np.full((len(models),len(cols)),np.nan)
    labels={}
    for r in rows:
        i=models.index(r['run']+' / '+r['model']); j=cols.index((r['task'],r['n']))
        if r['completed']: data[i,j]=r['exact']/r['completed']
        labels[i,j]=f"{r['exact']}/{r['completed']}\nformat: {r['format_failures']}"
    fig,ax=plt.subplots(figsize=(max(12,len(cols)*1.35),max(4,len(models)*.9)),layout='constrained')
    fig.patch.set_facecolor('#F5F1E7'); ax.set_facecolor('#E5E2D9')
    ax.imshow(data,vmin=0,vmax=1,cmap='YlGn',aspect='auto')
    for (i,j),label in labels.items(): ax.text(j,i,label,ha='center',va='center',fontsize=10,color='#172B36')
    ax.set_xticks(range(len(cols)),[f'{task}\nN={n}' for task,n in cols]); ax.set_yticks(range(len(models)),models)
    ax.set_title('Exact requested output — not a general memory score',loc='left',fontsize=17,pad=22)
    fig.supxlabel('Live API observations • descriptive pooled counts • format = malformed output count • seeds/depths are correlated',fontsize=10)
    fig.savefig(Path(output)/'strict-results.png',dpi=160)
    plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('directories',nargs='+'); p.add_argument('--output',required=True)
    args=p.parse_args(); b=build(args.directories,args.output); plot(b,args.output)
    print(json.dumps({'groups':len(b['summary']),'responses':len(b['records'])}))
