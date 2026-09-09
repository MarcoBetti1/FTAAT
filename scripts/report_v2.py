"""Report, independent answer-key audit, and standalone scientific figures."""
from collections import defaultdict,Counter
from decimal import Decimal
import json
from pathlib import Path
import re
import subprocess
from contextfrontier.tasks import digest
from .analyze_v2 import ROOT,MODELS,NAMES,RUNS

OUT=ROOT/'docs/episodes/01-v2'

def audit_cases():
    unique={};metrics=defaultdict(list);provenance=[]
    for name in RUNS:
        p=ROOT/'results'/name
        manifest=json.loads((p/'manifest.json').read_text());rev=manifest['git_revision']
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'contextfrontier'],cwd=ROOT,text=True).splitlines()
        source={Path(path).name:subprocess.check_output(['git','show',rev+':'+path],cwd=ROOT,text=True) for path in paths if path.endswith('.py') and len(Path(path).parts)==2}
        case_ids=[json.loads(line)['id'] for line in (p/'cases.jsonl').read_text().splitlines()]
        identity=digest(dict(config=manifest['config'],case_ids=case_ids,live=manifest['live'],runner_version=manifest['code_version'],source_hash=digest(source)))
        assert identity==manifest['identity'],'Recorded experiment identity differs from its committed core source'
        provenance.append(dict(run=name,revision=rev,identity_matches_committed_core_source=True,git_dirty_at_start=manifest['git_dirty']))
        for line in (p/'cases.jsonl').read_text().splitlines():
            c=json.loads(line);unique[c['id']]=c
        ev=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
        results={r['request_key']:r for r in ev if r['event']=='result'}
        reserved={r['request_key'] for r in ev if r['event']=='reserved'}
        assert reserved==set(results),'Unsettled paid dispatch'
        for r in results.values():
            assert r['actual_input_tokens']==r['reply']['usage']['input_tokens']+r['reply']['usage'].get('cache_creation_input_tokens',0)+r['reply']['usage'].get('cache_read_input_tokens',0)
            assert r['actual_output_tokens']==r['reply']['usage']['output_tokens']
            metrics[r['model']].append(r)
    for c in unique.values():
        before,rest=c['prompt'].split('BEGIN RECORDS\n');body,question=rest.split('\nEND RECORDS\n\n');lines=body.splitlines();assert len(lines)==c['n']
        for e in c['evidence']:
            assert lines[e['line']]==e['text']==c['prompt'][e['char_start']:e['char_end']]
        if c['task'] in ('needle','two_hop'):
            pairs=dict(line.split(' => ') for line in lines);assert len(pairs)==c['n']
            if c['task']=='needle':key=re.search(r'What is the value for ([A-Z|]+)\?',question).group(1);answer=pairs.get(key,'UNKNOWN')
            else:key=re.search(r'Starting at ([A-Z|]+),',question).group(1);answer=pairs[pairs[key]]
        else:
            pairs=defaultdict(list)
            for line in lines:
                rev,key,value=re.fullmatch(r'revision (\d+): ([A-Z|]+) => ([A-Z|]+)',line).groups();pairs[key].append((int(rev),value))
            key=re.search(r'CURRENT value for ([A-Z|]+)\?',question).group(1);answer=max(pairs[key])[1]
        assert c['expected']==[answer],f'Independent answer-key mismatch {c["id"]}'
    out=dict(unique_cases_verified=len(unique),evidence_spans='all match prompt',answer_keys='all independently recomputed from prompt records',unsettled_dispatches=0,source_provenance=provenance,models={})
    for model,rr in metrics.items():
        out['models'][model]=dict(responses=len(rr),returned_models=dict(Counter(r['reply']['model'] for r in rr)),input_token_range=[min(r['actual_input_tokens'] for r in rr),max(r['actual_input_tokens'] for r in rr)],output_token_range=[min(r['actual_output_tokens'] for r in rr),max(r['actual_output_tokens'] for r in rr)],count_delta_range=[min(r['count_delta'] for r in rr),max(r['count_delta'] for r in rr)],status=dict(Counter(r['reply']['status'] for r in rr)),input_tokens=sum(r['actual_input_tokens'] for r in rr),output_tokens=sum(r['actual_output_tokens'] for r in rr))
    (OUT/'case-and-token-audit.json').write_text(json.dumps(out,indent=2)+'\n');return out

def figures(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    p=OUT/'figures';p.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':'#F6F1E5','axes.facecolor':'#F6F1E5','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,ax=plt.subplots(figsize=(10,4.7))
    for i,m in enumerate(MODELS[:3]):
        v=s['primary'][m];rate=v['exact']/v['n'];lo,hi=v['wilson95']
        ax.errorbar(rate*100,i,xerr=np.array([[(rate-lo)*100],[(hi-rate)*100]]),fmt='o',markersize=9,capsize=6,color=['#AD7825','#527F9A','#367F66'][i]);ax.annotate(f"{v['exact']}/{v['n']}",(rate*100,i),xytext=(0,14),textcoords='offset points',ha='center')
    ax.set(yticks=range(3),yticklabels=[NAMES[m] for m in MODELS[:3]],xlim=(-3,104),ylim=(2.55,-.6),xlabel='Exact correct delivery per dispatched request (%)',title='8,192 records, target at 90%: 32 shared fresh seeds')
    ax.grid(axis='x',alpha=.2);fig.text(.15,.01,'95% Wilson intervals; only GPT-4o Mini vs Luna is the prespecified inferential contrast.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(p/'primary.svg');fig.savefig(p/'primary.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,5),sharey=True)
    for ax,n in zip(axes,[128,4096,8192]):
        for i,m in enumerate(MODELS[:3]):
            cs=[next(c for c in s['cells'] if c['model']==m and c['task']=='needle' and c['n_records']==n and c['depth']==d and not c['absent']) for d in [.1,.5,.9]]
            ax.plot([10,50,90],[c['exact']/c['n']*100 for c in cs],marker='o',label=NAMES[m],color=['#AD7825','#527F9A','#367F66'][i]);ax.set(xticks=[10,50,90],ylim=(-3,103),title=f"{n:,} records · {cs[0]['n']} seeds",xlabel='Target position (% of records)');ax.grid(alpha=.2)
    axes[0].set_ylabel('Exact correct delivery (%)');axes[2].legend(loc='lower left');fig.suptitle('Descriptive length and placement results — shared seeds are correlated');fig.tight_layout();fig.savefig(p/'length-position.svg');fig.savefig(p/'length-position.png',dpi=180);plt.close(fig)

def main():
    s=json.loads((OUT/'summary.json').read_text());assert not s['partial'];audit=audit_cases();figures(s)
    contrast=s['contrast'];old=s['primary'][MODELS[0]];new=s['primary'][MODELS[2]]
    lines=['# AI vs the World’s Worst Filing Cabinet','', 'Second edition · GPT Learning / ContextFrontier · 2026-09-09','',
      f"In the prespecified 8,192-record, 90%-position comparison, GPT-4o Mini returned the exact correct answer in **{old['exact']}/32** requests and GPT-5.6 Luna in **{new['exact']}/32**. This is a comparison of configured systems on synthetic code retrieval, not a universal intelligence ranking.",'',
      'The other central result is a measurement distinction: Claude Haiku often returned the correct final-line answer while failing the instruction to return only that answer. The paired reminder experiment measures that distinction prospectively.','',
      '[Protocol frozen before the new observations](PROTOCOL.md) · [Machine-readable analysis](summary.json) · [Independent case/token audit](case-and-token-audit.json)','',
      '## Primary comparison','',
      '| Model | Exact / dispatched | 95% Wilson interval | Actual input-token range |','|---|---:|---:|---:|']
    for m in MODELS[:3]:
        v=s['primary'][m];lo,hi=v['wilson95'];lines.append(f"| {NAMES[m]} | {v['exact']}/{v['n']} | {lo:.1%}–{hi:.1%} | {v['input_tokens'][0]:,}–{v['input_tokens'][1]:,} |")
    lines+=['',f"The single prespecified paired contrast is GPT-4o Mini versus Luna: {contrast['complete_pairs']} complete pairs; old-only correct {contrast['old_only']}, Luna-only correct {contrast['new_only']}, both correct {contrast['both_correct']}, both incorrect {contrast['both_wrong']}. Exact two-sided McNemar p = {contrast['exact_two_sided_mcnemar_p']:.10g}. GPT-4.1 Mini is a descriptive comparator. No corrected significance claim is made for the other cells.",'','![Primary comparison](figures/primary.png)','',
      '## Length and placement','',
      'Increasing length keeps the target fact and adds distractors from the same deterministic pool. Moving the target preserves the record set. Seeds recur across conditions, so length/position cells are correlated and must not be pooled as independent trials. Depth is record position, not token position.','',
      '| Model | Records | Target position | Exact / dispatched | Correct final line |','|---|---:|---:|---:|---:|']
    for c in s['cells']:
        if c['task']=='needle' and not c['absent']:lines.append(f"| {NAMES[c['model']]} | {c['n_records']:,} | {c['depth']:.0%} | {c['exact']}/{c['n']} | {c['final_line_correct']}/{c['n']} |")
    lines+=['','![Length and position](figures/length-position.png)','',
      'Claude has four seeds per position at 128 and 8,192 records. It did not receive the 4,096-record panel. Direct comparisons using Claude’s shared seeds are available under `shared_claude` in the JSON summary; do not compare unequal overall panels as a league table.','',
      '## Paired formatting intervention','',
      'For each model and task, 16 baseline/reminder pairs share the same records, expected answer, system instruction, and model settings. The sole added final sentence asks for only the code, one line, no explanation, labels, or Markdown. Max output is 2,048 for both conditions. Evidence positions are fixed at nominal 25% and 75%.','',
      '| Model | Task | Exact baseline → reminder | Final-line baseline → reminder | Exact improved / worsened |','|---|---|---:|---:|---:|']
    for p in s['format_pairs']:
        a=p['measures']['exact'];b=p['measures']['final_line_correct'];lines.append(f"| {NAMES[p['model']]} | {p['task']} | {a['baseline']}/16 → {a['reminder']}/16 | {b['baseline']}/16 → {b['reminder']}/16 | {a['improved']} / {a['worsened']} |")
    lines+=['','The final-line extractor was defined before this run. It examines only the last nonempty line, permits a narrow pair of backticks or bold markers, and requires a valid code or UNKNOWN. It never receives the answer key. This is not a general semantic grader. Strict exact delivery and final-line correctness answer different questions.','',
      '## Absent-key controls','', '| Model | Records | Exact / dispatched | Correct final line |','|---|---:|---:|---:|']
    for c in s['cells']:
        if c['absent']:lines.append(f"| {NAMES[c['model']]} | {c['n_records']:,} | {c['exact']}/{c['n']} | {c['final_line_correct']}/{c['n']} |")
    lines+=['','## Completion and token accounting','',f"All {s['total']['n']} substantive dispatches are represented. Status counts: `{s['total']['status']}`. The independent audit recomputed all {audit['unique_cases_verified']} distinct answer keys directly from prompt records, checked every evidence span, and reconciled input/output counts with provider usage. Smoke checks are excluded from the scientific comparison.",'',
      '| Model | Responses | Input tokens | Output tokens | Preflight → actual count delta range |','|---|---:|---:|---:|---:|']
    for m,v in audit['models'].items():lines.append(f"| {NAMES[m]} | {v['responses']} | {v['input_tokens']:,} | {v['output_tokens']:,} | {v['count_delta_range']} |")
    lines+=['','OpenAI full-request counts use `/v1/responses/input_tokens`; Anthropic uses `/v1/messages/count_tokens`. Anthropic preflight is an estimate. The actual response usage is authoritative. Same text does not imply the same token count. K counts task symbols; it is never substituted for tokenizer units. The local legacy-inventory audit is a separate measurement, not a model-inference result.','',
      '## Planned and observed requests','', '| Stage | Planned | Observed | Skipped | Unobserved | Conservative cost bound |','|---|---:|---:|---:|---:|---:|']
    for r in s['runs']:lines.append(f"| {r['name']} | {r['planned']} | {r['observed']} | {r['skipped']} | {r['unobserved']} | ${Decimal(r['cost_upper_usd']):.6f} |")
    lines+=['','Costs conservatively charge all input at 1.25× ordinary uncached input price and actual output at the listed price. These are planning bounds, not invoices; cached-input discounts are not assumed. Speech and transcription reservations are reported separately in `production-audit.json`. Fresh total caps are $20 OpenAI, including production, and $5 Anthropic, using Haiku only. No uncertain request was automatically retried.','',
      '## Model profiles and sources','',
      '- GPT-4o Mini: `gpt-4o-mini-2024-07-18`, temperature 0; [official profile and pricing](https://developers.openai.com/api/docs/models/gpt-4o-mini).',
      '- GPT-4.1 Mini: `gpt-4.1-mini-2025-04-14`, temperature 0; [official profile and pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini).',
      '- GPT-5.6 Luna: `gpt-5.6-luna`, reasoning none, provider default sampling; [official profile and pricing](https://developers.openai.com/api/docs/models/gpt-5.6-luna).',
      '- Claude Haiku 4.5: `claude-haiku-4-5-20251001`, temperature 0; [official Claude model overview](https://platform.claude.com/docs/en/models/overview).',
      '- The film uses disclosed stock Cedar and Onyx voices; [official speech documentation](https://developers.openai.com/api/docs/guides/text-to-speech).','',
      'Sources checked on 2026-09-09. Full model parameters and configured prices are preserved in each run manifest. This edition did not increase tested-model reasoning settings. The user requested more thought and craft in the production.','',
      '## Limits and relation to edition one','',
      'This controlled nonsense-code workload is not representative of all natural documents. The experiments measure delivered task answers, not internal attention weights, intelligence, or a reliable universal context frontier. Configurations differ in sampling and may use model aliases; returned model IDs are preserved. No mechanistic or isolated model-age effect is claimed.','',
      'Edition-one data remain unchanged and are not pooled here. The new generator preserves target facts and distractor prefixes across lengths; it is a fresh test under a revised protocol. Its primary condition uses 32 fresh seeds, rather than the earlier exploratory eight-case check. Refusals, output limits, and uncertain transport outcomes must be disclosed separately if they occur; they must never be called proven memory failures.','',
      '## Reproduce','', '```sh','python -m scripts.analyze_v2','python -m scripts.report_v2','python -m video.v2.story','python -m video.v2.speech  # paid only for uncached clips','python -m video.v2.audio --clip-qa  # paid transcription only if uncached','python -m video.v2.render','python -m video.v2.verify','```','',
      'Use the evidence archive to populate the original `results/v2-*` directories. Rendering uses local cached audio, macOS fonts, Pillow, NumPy, and FFmpeg; see `video/v2/README.md`. Never rerun paid experiments solely to rebuild the film.','']
    (OUT/'report.md').write_text('\n'.join(lines));print(OUT/'report.md')

if __name__=='__main__':main()
