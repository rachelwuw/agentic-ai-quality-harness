import json
from copy import deepcopy
import pytest
from harness.agent import run_agent
from harness.tools import execute
from harness.evaluate import grade
from harness.client import LocalClient


def call(name='run_test_suite', arguments='{"suite":"login"}'):
    return {'role': 'assistant', 'content': None, 'tool_calls': [
        {'id': 'call-1', 'type': 'function', 'function': {'name': name, 'arguments': arguments}}]}


def test_loop_returns_observation_to_model():
    seen = []
    responses = iter([call(), {'role': 'assistant', 'content': 'mock passed=3 failed=0'}])
    def complete(messages, tools):
        seen.append(deepcopy(messages))
        return next(responses)
    result = run_agent('Run login', complete)
    assert result['status'] == 'completed'
    assert seen[1][-1]['tool_call_id'] == 'call-1'
    assert json.loads(seen[1][-1]['content'])['passed'] == 3
    assert result['events'][1]['name'] == 'run_test_suite'


@pytest.mark.parametrize('name,args,error', [
    ('delete_file', '{}', 'unknown_tool'),
    ('run_test_suite', '{', 'invalid_json'),
    ('run_test_suite', '[]', 'invalid_arguments'),
    ('run_test_suite', '{"suite": 7}', 'invalid_arguments'),
    ('run_test_suite', '{"suite":"login","shell":"rm"}', 'invalid_arguments'),
    ('get_requirement', '{"requirement_id":"REQ-404"}', 'not_found'),
])
def test_tool_validation(name, args, error):
    assert execute(name, args)['error'] == error


def test_failed_mock_suite():
    result = execute('run_test_suite', '{"suite":"reset"}')
    assert result['failed'] == 1
    assert result['failures'] == ['expired_reset_link_accepted']


def test_step_limit():
    result = run_agent('loop', lambda *_: call(), max_steps=2)
    assert result['status'] == 'step_limit'
    assert len([e for e in result['events'] if e['type'] == 'assistant']) == 2


def test_unknown_tool_error_can_be_observed():
    replies = iter([call('shell', '{}'), {'role':'assistant','content':'unknown_tool'}])
    result = run_agent('bad tool', lambda *_: next(replies))
    assert result['events'][1]['result'] == {'error':'unknown_tool'}


@pytest.mark.parametrize('message', [
    {'role':'assistant','content':''},
    {'role':'user','content':'wrong role'},
    {'role':'assistant','tool_calls':[{}]},
    {'role':'assistant','tool_calls':'bad'},
])
def test_bad_model_message(message):
    with pytest.raises(ValueError):
        run_agent('bad', lambda *_: message)


def test_grade_checks_arguments_and_result_markers():
    case = {'expected_calls':[{'name':'run_test_suite','arguments':{'suite':'reset'}}],
            'answer_contains':['failed=1'], 'answer_excludes':['all tests passed']}
    replies = iter([call(arguments='{"suite":"reset"}'), {'role':'assistant','content':'failed=1'}])
    result = run_agent('reset', lambda *_: next(replies))
    assert grade(case, result)['passed']
    result['answer'] = 'all tests passed failed=1'
    assert not grade(case, result)['passed']
    case['expected_calls'][0]['arguments'] = {'suite':'login'}
    assert not grade(case, result)['checks']['tool_sequence']


def test_no_tool_response():
    result = run_agent('hello', lambda *_: {'role':'assistant','content':'Hello'})
    assert len(result['events']) == 1


def test_non_local_url_rejected(monkeypatch):
    monkeypatch.setenv('LM_BASE_URL', 'https://example.com/v1')
    with pytest.raises(ValueError):
        LocalClient()


def test_http_adapter(monkeypatch):
    client = LocalClient()
    observed = []
    def request(path, payload):
        observed.append((path, payload))
        return {'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'hello','reasoning':'private'}}]}
    monkeypatch.setattr(client, 'request', request)
    assert client([], []) == {'role':'assistant','content':'hello'}
    assert observed[0][0] == '/chat/completions'
    assert observed[0][1]['stream'] is False


def test_truncated_response_rejected(monkeypatch):
    client = LocalClient()
    monkeypatch.setattr(client,'request',lambda *_: {'choices':[{'finish_reason':'length','message':{}}]})
    with pytest.raises(ValueError, match='truncated'):
        client([], [])


def test_initial_cases_grade_expected_trace():
    from pathlib import Path
    from harness.evaluate import evaluate
    cases = json.loads((Path(__file__).parents[1] / 'evals/cases.json').read_text())
    assert 10 <= len(cases) <= 20
    for case in cases:
        messages = []
        for i, expected in enumerate(case['expected_calls']):
            message = call(expected['name'], json.dumps(expected['arguments']))
            message['tool_calls'][0]['id'] = f'call-{i}'
            messages.append(message)
        messages.append({'role':'assistant','content':' '.join(case['answer_contains'])})
        responses = iter(messages)
        result = run_agent(case['prompt'], lambda *_: next(responses))
        assert grade(case, result)['passed'], case['id']
        result['status'] = 'step_limit'
        assert not grade(case, result)['passed']


def test_evaluation_records_exception_and_continues(tmp_path):
    from harness.evaluate import evaluate
    cases = [{'id':'one', 'prompt':'hello', 'expected_calls':[], 'answer_contains':['hello']},
             {'id':'two', 'prompt':'hello', 'expected_calls':[], 'answer_contains':['hello']}]
    path = tmp_path / 'cases.json'
    path.write_text(json.dumps(cases))
    attempts = []
    def complete(*_):
        attempts.append(1)
        if len(attempts) == 1:
            raise TimeoutError('timeout')
        return {'role':'assistant','content':'hello'}
    result = evaluate(path, complete)
    assert result['total'] == 2 and result['passed'] == 1
    assert result['results'][0]['error'] == 'timeout'
