"""Original narrated screenplay. Result sentences are populated from audited data."""
import json
from pathlib import Path

def shot(id,kind,title,narration='',voice='cedar',tail=.65,**data):
    return dict(id=id,kind=kind,title=title,narration=narration,voice=voice,tail=tail,**data)

def opening():
    return [
      shot('01_open','office','One small job',
           "This is Pip. Today, Pip is opening an artificial intelligence filing office. The job is simple: read the files, find one fact, return one answer. How bad could it be?"),
      shot('02_avalanche','avalanche','The workload',
           "We gave the office eight thousand, one hundred and ninety-two files. The answer really was in there. Some models found it. Others handed us... nothing.",tail=1.0),
      shot('03_pip','pip_close','Pip considers his options',
           "I have updated my résumé.",voice='onyx',tail=.85,mood='annoyed'),
      shot('04_title','title','AI vs the filing cabinet',
           "So we tested older and newer GPT models, plus a small Claude. But the biggest plot twist wasn't just which model failed. It was what we were calling a failure."),
      shot('05_rules','record','The challenge',
           "Here is the game. A made-up code points to another made-up code. We ask for the value belonging to one key. No trivia. No internet. Every fact needed to answer is inside the prompt."),
      shot('06_cast','cast','Meet the applicants',
           "Our applicants: GPT four O Mini, GPT four point one Mini, GPT five point six Luna, and Claude Haiku four point five. These are API models with the settings shown here, not the ChatGPT and Claude apps."),
      shot('07_fair','nested','Same fact, more clutter',
           "As the filing cabinet grows, we keep the target fact and add distracting records. Move the target, keep the same files. Otherwise, a supposedly harder test could quietly become a completely different test."),
      shot('08_tokens','tokens','Fix the ruler first',
           "And first, we fixed our own ruler. Four symbols are not necessarily four tokens. In this local tokenizer check, four symbols and their separators take seven. For the real requests, we use each provider's counting endpoint, then save actual usage."),
      shot('09_pip_ruler','pip_close','An administrative incident',
           "The ruler has been referred to another department.",voice='onyx',tail=.7,mood='annoyed'),
    ]

def build(s):
    assert not s['partial'],'Never narrate an unfinished experiment as final.'
    models=list(s['models']);old,mid,new,claude=models
    primary=s['primary'];a=primary[old]['exact'];b=primary[new]['exact'];m=primary[mid]['exact']
    def cell(model,task='needle',n=8192,depth=.9,absent=False,style='baseline'):
        return next(c for c in s['cells'] if c['model']==model and c['task']==task and c['n_records']==n and c['depth']==depth and c['absent']==absent and c['query_style']==style)
    def fmt(model,task):return next(x for x in s['format_pairs'] if x['model']==model and x['task']==task)
    f=fmt(claude,'two_hop');q=f['measures'];up=fmt(old,'updates')['measures'];luna_up=fmt(new,'updates')['measures']
    # These editorial sentences deliberately make their data dependencies explicit.
    assert all(cell(x,n=128,depth=d)['exact']==cell(x,n=128,depth=d)['n'] for x in models for d in (.1,.5,.9)), 'Rewrite the warm-up if any observed cell fails.'
    assert all(primary[x]['n']==32 for x in models[:3]), 'Primary conditions must be complete.'
    assert b-a>16, 'Rewrite the editorial framing if there is no large observed gap.'
    assert 'two_hop' in s['examples'] and 'needle_failure' in s['examples']
    begin=[cell(old,depth=d)['exact'] for d in (.1,.5,.9)]
    ch=[cell(claude,depth=d)['exact'] for d in (.1,.5,.9)]
    reminder_sentence=("The reminder changed nothing in the strict two-hop score." if q['exact']['baseline']==q['exact']['reminder'] else "The reminder changed the strict two-hop score.")
    scenes=opening()+[
      shot('10_warmup','warmup','Employee of the first thirty seconds',
           "At a hundred and twenty-eight records, every model passed every present-key lookup we gave it. Excellent. Pip is employee of the first thirty seconds. Now let's see how long that certificate lasts."),
      shot('11_grow','grow','Eight thousand files later',
           "We step up to four thousand records, then eight thousand. The largest GPT prompts are around a hundred and eleven thousand input tokens. That's a lot of filing. It is still inside these models' advertised context windows."),
      shot('12_prediction','prediction','Where would you hide it?',
           "Before the results: where would you hide one fact to make it hardest to find? Near the beginning, in the middle, or near the end? Pick one. We tested all three.",tail=2.0),
      shot('13_primary','primary','The prespecified showdown',
           f"Here is the comparison we picked before this run: the fact near the end, thirty-two fresh random seeds. GPT four O Mini: {a} out of thirty-two. Luna: {b} out of thirty-two. Same prompts. Very different afternoons."),
      shot('14_evidence','failure','Inspect the failed delivery',
           "This is one real failure. The requested key is present. Its value is right there. Four O Mini returns UNKNOWN. That is an incorrect answer, not just an untidy envelope.",example=s['examples']['needle_failure']),
      shot('15_positions','positions','Location matters here',
           f"But move that fact. Four O Mini gets {begin[0]} of thirty-two near the beginning, {begin[1]} in the middle, and {begin[2]} near the end. Trouble in every location. Not exactly a reassuring floor plan."),
      shot('16_middle','middle','The model between them',
           f"GPT four point one Mini gets {m} of thirty-two in that same end-position comparison. These are specific model versions, settings, and synthetic files. We have measured a task failure, not filmed the inside of an attention mechanism."),
      shot('17_claude','claude','A smaller Claude panel',
           f"Claude Haiku gets {ch[0]} of four near the beginning, {ch[1]} of four in the middle, and {ch[2]} of four near the end. Four cases per position: a smaller budget, and a much blurrier picture. No grand league table from that."),
      shot('18_uncertainty','uncertainty','A score is not a law of nature',
           "Even a big gap is not a law of nature. These bars show uncertainty across our sampled seeds. And the same seeds reappear at different lengths and positions. You can't count every dot as a new independent witness."),
      shot('19_job','office','Another department',
           "Then we change the job. Instead of one lookup, follow two arrows. A points to B. B points to C. Return C. Pip calls this interdepartmental cooperation."),
      shot('20_hops','hops','Follow two arrows',
           "Here are the two records from a real Claude case. Follow the first arrow, then the second. The final code is the answer. Claude found it. And then Claude wrote us a small guided tour.",example=s['examples']['two_hop']),
      shot('21_printer','printer','The guided tour',
           "This is its actual response. First arrow. Second arrow. Correct final code. Our strict score says: failure. Why? Because we asked for only the code. The answer was right. The delivery was a lecture.",example=s['examples']['two_hop']),
      shot('22_pip_review','pip_close','Pip appeals',
           "I would like to appeal this performance review.",voice='onyx',tail=.85,mood='annoyed'),
      shot('23_two_scores','scores','Two different questions',
           f"Across sixteen two-hop cases, Haiku gets {q['exact']['baseline']} strict passes, but {q['final_line_correct']['baseline']} correct final-line answers. Both scores matter. A program may need exactly one code. A person may care whether the answer was found. One red stamp cannot explain both."),
      shot('24_reminder','reminder','The sticky-note intervention',
           "Can a sticky note fix the delivery? We repeat each case with one extra sentence at the end: return only the requested code, on one line, with no explanation, labels, or Markdown. Same files. Same model settings. Only that reminder changes."),
      shot('25_reminder_result','format_result','Read the sticky note',
           f"{reminder_sentence} Haiku goes from {q['exact']['baseline']} to {q['exact']['reminder']} strict passes out of sixteen. Its correct final-line score goes from {q['final_line_correct']['baseline']} to {q['final_line_correct']['reminder']}. A reasonable-sounding prompt tip still has to survive an experiment."),
      shot('26_pip_note','pip_close','Message received',
           "Your request for less paperwork has generated more paperwork.",voice='onyx',tail=.9,mood='neutral'),
      shot('27_revision','revision','The stale memo',
           "Our other small game is the stale memo. The higher revision wins, even when an older revision appears later in the file. Reading the last matching line is not enough. That is how you accidentally reinstate last year's sandwich policy."),
      shot('27b_luna','luna_stale','The star fails a tiny file',
           "Remember Luna, our long-file star? Here it returns the older value. Perfectly formatted. Wrong revision. This little file has only a hundred and twenty-eight records. Pip would like that employee-of-the-month certificate back.",example=s['examples']['luna_stale_revision']),
      shot('28_revision_result','revision_result','Check a second task',
           f"Across sixteen revision cases, Luna scores {luna_up['exact']['baseline']} exact, then {luna_up['exact']['reminder']} with the reminder. Four O Mini goes from {up['exact']['baseline']} to {up['exact']['reminder']}. So the reminder sometimes helps. But winning the giant filing game doesn't guarantee you'll survive a tiny stale memo."),
      shot('29_rules','rules','What the scores can say',
           "So: a correct code with extra words is a delivery problem. UNKNOWN when the fact is present is a wrong answer. An unfinished response is a separate outcome. Calling all three 'the model forgot' throws away the interesting part."),
      shot('30_method','method','Test the test',
           "We froze the new cases and the main comparison before running them. We saved full prompts, responses, actual token counts, and separate provider budgets. The report includes the other conditions too, including tests where the key is genuinely absent."),
      shot('31_limits','limits','What this does not prove',
           "These nonsense-code files are a controlled obstacle course, not a miniature version of every real document. A model that wins here can still fail elsewhere. A context window is room for text. It is not a promise that every task inside it will work."),
      shot('32_end','end','Check the filing before firing the clerk',
           "The lesson isn't to crown a permanent winner. Make the challenge clear. Check the ruler. Inspect the answer. Then decide what failed. The code and evidence are linked below. This is GPT Learning. Pip, any plans for our next experiment?"),
      shot('33_chess','chess','Next: an organizational challenge',
           "I have filed the chess knights under horses.",voice='onyx',tail=1.3,mood='happy'),
      shot('34_credits','credits','Made for GPT Learning',tail=4.5),
    ]
    return scenes

if __name__=='__main__':
    p=Path('artifacts/episode-01-v2');p.mkdir(parents=True,exist_ok=True)
    s=json.loads(Path('docs/episodes/01-v2/summary.json').read_text())
    scenes=build(s);(p/'screenplay.json').write_text(json.dumps(scenes,indent=2)+'\n')
    print(len(scenes),'shots;',sum(len(s['narration'].split()) for s in scenes),'words')
