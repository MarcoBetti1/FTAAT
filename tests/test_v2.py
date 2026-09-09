from dataclasses import replace
import pytest
from contextfrontier.tasks_v2 import make_case,make_suite
from contextfrontier.scoring_v2 import grade,final_line_answer
from contextfrontier.runner import run
from contextfrontier.report import report
from test_runner import config,Fake


def lines(c):return c.prompt.split('BEGIN RECORDS\n')[1].split('\nEND RECORDS')[0].splitlines()

def test_nested_facts_and_target_survive_length_and_position_changes():
    cases=[make_case('needle',seed=43,n=n,depth=d) for n in [16,128,512] for d in [.1,.5,.9]]
    assert len({tuple(c.expected) for c in cases})==1
    assert len({c.nested_family for c in cases})==1
    for a,b in zip(cases[::3],cases[3::3]):assert set(lines(a))<set(lines(b))
    for c in cases:
        assert len(lines(c))==c.n
        for e in c.evidence:assert c.prompt[e['char_start']:e['char_end']]==e['text']==lines(c)[e['line']]

@pytest.mark.parametrize('task',['two_hop','updates'])
def test_paired_wording_changes_no_records_or_answers(task):
    a=make_case(task,seed=8,n=128);b=make_case(task,seed=8,n=128,query_style='reminder')
    assert lines(a)==lines(b) and a.expected==b.expected and a.evidence==b.evidence
    assert b.prompt.startswith(a.prompt+'\n\nFinal answer format:')
    assert [e['line'] for e in a.evidence]==[32,95]
    if task=='two_hop':
        m=dict(x.split(' => ') for x in lines(a));q=a.prompt.split('Starting at ')[1].split(',')[0]
        assert m[m[q]]==a.expected[0]
    else:
        revisions={}
        for x in lines(a):
            prefix,kv=x.split(': ');k,v=kv.split(' => ');rev=int(prefix.split()[1])
            if rev>revisions.get(k,(-1,None))[0]:revisions[k]=(rev,v)
        q=a.prompt.rsplit('for ',1)[1].rstrip('?');assert revisions[q][1]==a.expected[0]

def test_absence_control_has_no_matching_key():
    c=make_case('needle',seed=41,n=128,absent=True)
    q=c.prompt.rsplit('for ',1)[1].rstrip('?')
    assert q not in dict(x.split(' => ') for x in lines(c))
    assert c.expected==['UNKNOWN'] and c.evidence==[]

@pytest.mark.parametrize('text,answer',[
    ('explanation\n\nABCD|EFGH','ABCD|EFGH'),('**ABCD|EFGH**','ABCD|EFGH'),
    ('`ABCD|EFGH`','ABCD|EFGH'),('The answer is ABCD|EFGH',None),
    ('ABCD|EFGH\nI am not sure',None),('ABCD|EFGH\nIJKL|MNOP','IJKL|MNOP'),
    ('ABC|EFGH',None),('UNKNOWN','UNKNOWN'),('',None),
])
def test_final_answer_parser_is_independent_of_expected_answer(text,answer):
    assert final_line_answer(text,2)==answer

def test_two_scores_do_not_conflate_answer_and_contract():
    r=grade('Here is my explanation.\nABCD|EFGH',['ABCD|EFGH'],symbols_per_answer=2)
    assert not r['exact'] and r['final_line_correct']
    r=grade('ABCD|EFGH\nIJKL|MNOP',['ABCD|EFGH'],symbols_per_answer=2)
    assert not r['exact'] and not r['final_line_correct']

def test_runner_and_report_keep_wording_conditions_separate(tmp_path):
    c=config();c['suite']=dict(version='games-v2',blocks=[dict(task='two_hop',n=16,seeds=[1,2],query_styles=['baseline','reminder'])])
    result=run(c,tmp_path,1,live=True,provider_factory=Fake)
    assert result['status']=='completed'
    data=report(tmp_path)
    assert data['scoring_version']=='score-v2' and len(data['groups'])==2
    assert all(g['dispatched']==2 and g['exact_per_dispatched']==1 and g['final_line_correct']==2 for g in data['groups'])
