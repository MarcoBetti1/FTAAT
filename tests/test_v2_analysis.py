import pytest
from scripts.analyze_v2 import paired_contrast,wilson,hit

def test_exact_paired_binomial_tail():
    a={i:i==0 for i in range(10)};b={i:i!=0 for i in range(10)}
    r=paired_contrast(a,b,10)
    assert (r['old_only'],r['new_only'])==(1,9)
    assert r['exact_two_sided_mcnemar_p']==22/1024

def test_concordant_and_unmatched_cases_do_not_change_discordant_tail():
    r=paired_contrast({1:False,2:False,3:True,4:False,9:True},{1:True,2:True,3:True,4:False,8:False})
    assert r['complete_pairs']==4 and r['both_correct']==r['both_wrong']==1
    assert r['exact_two_sided_mcnemar_p']==.5
    assert paired_contrast({1:True},{1:True})['exact_two_sided_mcnemar_p']==1

def test_wilson_extremes_retain_uncertainty():
    lo,hi=wilson(0,32);other_lo,other_hi=wilson(32,32)
    assert lo==0 and hi==pytest.approx(.1071791982550706)
    assert other_lo==pytest.approx(1-hi) and other_hi==1
    assert wilson(0,0) is None

def test_uncompleted_delivery_is_not_a_success():
    assert not hit({'grade':None},'exact')
    assert hit({'grade':{'exact':True}},'exact')
