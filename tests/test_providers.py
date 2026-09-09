import httpx
import pytest
from contextfrontier.providers import APIProvider, ProviderError, usage_counts, local_text_tokens
from contextfrontier.tasks import make_case

@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_actual_model_count_and_generation_payload(provider):
    requests = []
    def handler(request):
        import json
        body = json.loads(request.content)
        requests.append((request.url.path, body))
        assert body['model'] == 'exact-model-id'
        if 'tokens' in request.url.path:
            return httpx.Response(200, json={'input_tokens': 123})
        if provider == 'openai':
            assert body['truncation'] == 'disabled'
            assert body['store'] is False
            raw = dict(model='returned-snapshot', status='completed', output=[{'type':'message','content':[{'type':'output_text','text':'ABCD'}]}])
        else:
            raw = dict(model='returned-snapshot', stop_reason='end_turn', content=[{'type':'text','text':'ABCD'}])
        return httpx.Response(200, json={**raw, 'usage':{'input_tokens':125,'output_tokens':2}}, headers={'request-id':'req_123'})
    client = httpx.Client(base_url='https://test/v1/', transport=httpx.MockTransport(handler))
    p = APIProvider({'provider':provider,'model':'exact-model-id','max_output_tokens':100}, client)
    case = make_case('needle')
    assert p.count(case)['input_tokens'] == 123
    reply = p.generate(case)
    assert reply.text == 'ABCD'
    assert reply.model == 'returned-snapshot'
    assert reply.request_id == 'req_123'
    assert requests[0][1].get('instructions', requests[0][1].get('system')) == case.system
    assert requests[0][1].get('input', requests[0][1].get('messages')) == requests[1][1].get('input', requests[1][1].get('messages'))


def test_anthropic_cache_usage_is_not_dropped():
    assert usage_counts('anthropic', dict(input_tokens=10,output_tokens=3,cache_read_input_tokens=20,cache_creation_input_tokens=5)) == (35,3)
    with pytest.raises(ProviderError):
        usage_counts('openai', {})


def test_local_unknown_model_has_no_silent_fallback():
    with pytest.raises(KeyError):
        local_text_tokens('imaginary-unknown', 'hello')
