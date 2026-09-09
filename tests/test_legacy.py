import pytest
from scripts.run_experiments import grade_response, run_experiments, staircase_schedule
from scripts.build_prompt import build_prompt_for_all_keys
from scripts.helpers.eval import evaluate_token_sequences


def test_old_partial_answers_no_longer_get_full_credit():
    assert evaluate_token_sequences(['A'], ['A','B']) == (.5,.5)
    result, flaw, _, _ = grade_response('', ['x'], {'x':'A'}, tokenizer=len)
    assert result == (0,0) and flaw
    result, flaw, _, _ = grade_response('A\nA', ['x','y'], {'x':'A','y':'B'}, tokenizer=len)
    assert result == (.5,.5)


def test_legacy_paid_runner_stops_before_import():
    with pytest.raises(RuntimeError, match='retired'):
        run_experiments('does.not.exist')


def test_bad_staircase_does_not_loop_forever():
    with pytest.raises(ValueError):
        list(staircase_schedule(1,1,10,10,factor=1))
