import json
from pathlib import Path
import pytest
from contextfrontier.providers import Reply, ProviderError
from contextfrontier.runner import run, read_rows
from contextfrontier.report import report


def config():
    return dict(comparison='same_text', suite=dict(tasks=['needle'],record_counts=[4],seeds=[1],depths=[.5],absent_controls=False),
                models=[dict(provider='openai',model='test',context_window=10000,max_output_tokens=100,
                             input_usd_per_million=1,output_usd_per_million=2,pricing_source='test fixture',pricing_checked='2026-09-09')])

class Fake:
    calls = 0
    counts = 0
    def __init__(self, spec): self.spec = spec
    def count(self, case):
        Fake.counts += 1
        return dict(input_tokens=100,source='fixture',model=self.spec['model'])
    def generate(self, case):
        Fake.calls += 1
        return Reply('\n'.join(case.expected), 'completed','test',dict(input_tokens=100,output_tokens=10),1,'fixture',{})
    def close(self): pass


def test_dry_run_is_network_free(tmp_path):
    def fail(_): raise AssertionError('network')
    result = run(config(),tmp_path,1,provider_factory=fail)
    assert result['status'] == 'dry_run'
    assert result['input_tokens'] is None
    assert report(tmp_path)['groups'] == []


def test_budget_and_resume(tmp_path):
    Fake.calls = Fake.counts = 0
    assert run(config(),tmp_path,.00001,live=True,provider_factory=Fake)['status'] == 'budget_stop'
    assert Fake.calls == 0
    assert run(config(),tmp_path,1,live=True,provider_factory=Fake)['status'] == 'completed'
    assert Fake.calls == 1
    assert run(config(),tmp_path,1,live=True,provider_factory=Fake)['status'] == 'completed'
    assert Fake.calls == Fake.counts == 1
    assert report(tmp_path)['groups'][0]['exact_rate'] == 1


def test_uncertain_requests_never_retried(tmp_path):
    class Broken(Fake):
        def generate(self, case): raise ProviderError('timeout')
    assert run(config(),tmp_path,1,live=True,provider_factory=Broken)['status'] == 'uncertain_billing'
    assert run(config(),tmp_path,1,live=True,provider_factory=Fake)['status'] == 'uncertain_billing'
    assert report(tmp_path)['unsettled_requests'] == 1


def test_incomplete_not_memory_failure(tmp_path):
    class Short(Fake):
        def generate(self, case):
            r = super().generate(case)
            r.status = 'incomplete'
            return r
    run(config(),tmp_path,1,live=True,provider_factory=Short)
    g = report(tmp_path)['groups'][0]
    assert g['completed'] == 0 and g['other_outcomes'] == 1 and g['exact_rate'] is None


def test_config_changes_fail_closed(tmp_path):
    c = config()
    run(c,tmp_path,1)
    c['suite']['seeds'] = [2]
    with pytest.raises(ValueError, match='changed'):
        run(c,tmp_path,1)

@pytest.mark.parametrize('field,value', [('max_output_tokens',0),('input_usd_per_million',-1),('input_usd_per_million',float('nan'))])
def test_bad_model_specs(tmp_path, field, value):
    c = config()
    c['models'][0][field] = value
    with pytest.raises(ValueError): run(c,tmp_path,1)


def test_context_and_output_caps_are_separate_skips(tmp_path):
    c = config()
    c['models'][0]['context_window'] = 110
    run(c,tmp_path,1,live=True,provider_factory=Fake)
    assert read_rows(tmp_path/'events.jsonl')[-1]['reason'] == 'context_limit'
    c = config()
    c['models'][0]['max_output_tokens'] = 1
    run(c,tmp_path/'other',1,live=True,provider_factory=Fake)
    assert read_rows(tmp_path/'other/events.jsonl')[-1]['reason'] == 'output_cap_too_small'
