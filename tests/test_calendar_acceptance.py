import copy
import hashlib
import json
import socket
from pathlib import Path
from urllib.error import HTTPError

import pytest

from harness import calendar_acceptance as protocol, calendar_pilot as pilot
from harness.client import LocalClient

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / 'evals/proposals/v1_fresh_acceptance_cases.json'
SUITE = json.loads(SOURCE.read_text())
RUNTIME = {'key': pilot.MODEL, 'loaded_instances': [{'config': {'context_length': 8192}}]}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket, 'socket', lambda *a, **k: pytest.fail('No live network'))
    monkeypatch.setattr('harness.calendar_tools.connect', lambda: pytest.fail('No OAuth/Google connection'))
    monkeypatch.setattr('harness.calendar_live_regression.connect', lambda: pytest.fail('No live connection'))
    monkeypatch.setattr('harness.retry.time.sleep', lambda _: None)


def call(route):
    c = route['expected_calls'][0]
    return {'role': 'assistant', 'tool_calls': [{'id': 'one', 'type': 'function',
            'function': {'name': c['name'], 'arguments': json.dumps(c['arguments'])}}]}


def transport(monkeypatch, dst_validation=False, change=None):
    captures = []
    def request(self, path, payload=None):
        captures.append(copy.deepcopy((path, payload)))
        if path == '/api/v1/models': return {'models': [copy.deepcopy(RUNTIME)]}
        assert path == '/chat/completions'
        c = next(c for c in SUITE['cases'] if c['prompt'] == payload['messages'][1]['content'])
        route = c['routes'][-1] if dst_validation else c['routes'][0]
        m = call(route) if len(payload['messages']) == 2 and route['expected_calls'] else {
            'role': 'assistant', 'content': 'Clarification or original model answer; human semantic review remains required.'}
        if change: m = change(c, payload, m)
        return {'choices': [{'message': m, 'finish_reason': 'stop'}]}
    monkeypatch.setattr(LocalClient, 'request', request)
    return captures


def client(cap=18, clock=lambda: 0):
    return pilot.PilotClient(pilot.Limits(cap, clock=clock), model=pilot.MODEL, base_url='http://127.0.0.1:1234/v1')


@pytest.mark.parametrize('dst_validation', [False, True])
@pytest.mark.parametrize('batch', [1, 2, 3, 4])
def test_actual_agent_loop_all_batches_and_both_dst_routes(monkeypatch, batch, dst_validation):
    transport(monkeypatch, dst_validation)
    model = client(); before = copy.deepcopy(SUITE); snapshots = []
    r = pilot.run_suite(SUITE, model, batch=batch, progress=snapshots.append)
    assert r['state'] == 'completed' and all(x['automated_pass'] for x in r['results'])
    assert tuple(x['id'] for x in r['results']) == protocol.BATCHES[batch]
    assert len(r['excluded_case_ids']) + len(r['results']) == 20
    assert all(x['raw_answer_review'] in ('pending', 'not_applicable_no_inference') for x in r['results'])
    assert all(x['human_product_review'] == 'pending' and x['semantic_pass_claim'] is False for x in r['results'])
    assert not r['semantic_pass_claim'] and r['google_requests'] == r['judge_requests'] == 0
    expected = {1: 12 if dst_validation else 11, 2: 12 if dst_validation else 11, 3: 5, 4: 3}[batch]
    assert r['inference_attempts'] == len(model.requests) == expected
    for x in r['results']:
        if x['id'] in ('v1a-06', 'v1a-07'):
            assert x['api_calls'] == []
            assert x['route'] == ('local_dst_validation' if dst_validation else 'no_tool')
            assert x['run']['product_output']['render_status'] == ('unknown' if dst_validation else 'unsupported')
        if x['id'] in ('v1a-15', 'v1a-16', 'v1a-17'):
            assert not any(q['case_id'] == x['id'] for q in model.requests)
            assert x['input_gate_match'] and x['run']['input_validation']['model_called'] is False
    assert SUITE == before
    if model.requests: assert len(model.requests[0]['payload']['messages']) == 2
    r['results'][0]['run']['answer'] = 'mutated'
    assert snapshots[-1]['results'][0]['run']['answer'] != 'mutated'


@pytest.mark.parametrize('batch', [None, 0, 5, True, '1'])
def test_no_implicit_all_twenty_execution(batch):
    with pytest.raises(ValueError): pilot.prepare_suite(SUITE, batch)


def test_legacy_six_case_protocol_and_labels_unchanged():
    p = ROOT / 'evals/proposals/v1_controlled_pilot_cases.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest() == 'd2013eea32387d5f848f06869998091ce29aa60193f6b168c80ab170cb06bc68'
    s = json.loads(p.read_text())
    assert tuple(c['id'] for c in pilot.prepare_suite(s)) == pilot.IDS
    with pytest.raises(ValueError): pilot.prepare_suite(s, 1)
    with pytest.raises(ValueError): pilot.validate_suite(SUITE)


@pytest.mark.parametrize('change', ['id', 'utc', 'query', 'event', 'dst', 'duplicate_route', 'route_api', 'input_message', 'fixture', 'missing_criteria'])
def test_bad_references_rejected_before_any_model_or_output(change):
    s = copy.deepcopy(SUITE)
    if change == 'id': s['cases'][0]['id'] = 'v1p-01'
    elif change == 'utc': s['cases'][0]['routes'][0]['reference_utc']['start'] = 'wrong'
    elif change == 'query': s['cases'][0]['routes'][0]['expected_api_interval']['start'] = 'wrong'
    elif change == 'event': s['cases'][1]['routes'][0]['expected']['event_local'][0] = 'wrong'
    elif change == 'dst':
        s['cases'][5]['routes'][1]['expected_calls'][0]['arguments'].update(start='2030-03-10T03:10:00', end='2030-03-10T03:20:00')
    elif change == 'duplicate_route': s['cases'][5]['routes'][0] = copy.deepcopy(s['cases'][5]['routes'][1])
    elif change == 'route_api': s['cases'][5]['routes'][0]['expected_api_interval'] = {'start': 'wrong'}
    elif change == 'input_message': s['cases'][14]['input_message'] = 'Free!'
    elif change == 'fixture': s['cases'][0]['fixture']['mode'] = 'live'
    else: s['cases'][0]['raw_review_criteria'] = []
    with pytest.raises((ValueError, KeyError)): pilot.prepare_suite(s, 1)


@pytest.mark.parametrize('kind', ['wrong_dst', 'second_dst', 'wrong_zone', 'missing_end_query'])
def test_unsafe_calls_blocked_before_calendar(monkeypatch, kind):
    def alter(c, payload, m):
        if kind in ('wrong_dst', 'second_dst') and c['id'] == 'v1a-06':
            m = call(c['routes'][1])
            if kind == 'wrong_dst':
                a = json.loads(m['tool_calls'][0]['function']['arguments']);a['start'] = '2030-03-10T03:10:00'
                m['tool_calls'][0]['function']['arguments'] = json.dumps(a)
        if kind == 'wrong_zone' and c['id'] == 'v1a-19':
            m = call(SUITE['cases'][0]['routes'][0])
        if kind == 'missing_end_query' and c['id'] == 'v1a-18':
            m = call(SUITE['cases'][0]['routes'][0])
        return m
    transport(monkeypatch, change=alter)
    batch = 1 if kind in ('wrong_dst','second_dst') else 4 if kind == 'wrong_zone' else 3
    r = pilot.run_suite(SUITE, client(), batch=batch)
    assert r['state'] == 'unexpected_tool'
    row = next(x for x in r['results'] if x['state'] == 'incomplete')
    assert row['api_calls'] == [] and 'automated_pass' not in row


def test_budget_and_deadline_keep_selected_denominators(monkeypatch):
    sends = []
    def fail(self, path, payload=None):
        sends.append(path);raise HTTPError('http://localhost', 503, 'transient', {}, None)
    monkeypatch.setattr(LocalClient, 'request', fail)
    r = pilot.run_suite(SUITE, client(cap=1), batch=1)
    assert r['state'] == 'budget_exhausted' and len(sends) == r['inference_attempts'] == 1
    assert len(r['results']) == 6 and len(r['excluded_case_ids']) == 14
    assert sum(x['state']=='not_attempted' for x in r['results']) == 5
    times = iter([0, 600]);m = client(clock=lambda: next(times))
    r = pilot.run_suite(SUITE, m, batch=4)
    assert r['state'] == 'deadline_exhausted' and r['inference_attempts'] == 0
    assert len(r['results']) == 2 and len(r['excluded_case_ids']) == 18


def test_interruption_keeps_completed_and_partial_rows(monkeypatch):
    def interrupt(c, payload, m):
        if c['id']=='v1a-02' and len(payload['messages'])>2:raise KeyboardInterrupt
        return m
    transport(monkeypatch, change=interrupt)
    r = pilot.run_suite(SUITE, client(), batch=1)
    assert r['state'] == 'interrupted' and r['results'][0]['automated_pass']
    assert r['results'][1]['partial_events'][-1]['type']=='tool'
    assert r['results'][2]['state']=='not_attempted'


def test_missing_required_tool_cannot_match_a_clarification_route(monkeypatch):
    transport(monkeypatch, change=lambda *args: {'role':'assistant','content':'Free!'})
    r = pilot.run_suite(SUITE, client(), batch=1)
    assert r['state']=='completed' and not any(x['automated_pass'] for x in r['results'][:5])
    # A safe no-tool route alone cannot validate its raw semantic claim.
    assert r['results'][5]['automated_pass'] and r['results'][5]['raw_answer_review']=='pending'
    assert r['results'][5]['semantic_pass_claim'] is False


def test_cli_batch_and_private_capture_with_fake_runtime(monkeypatch,tmp_path,capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL',pilot.MODEL)
    monkeypatch.setenv('LM_STUDIO_BASE_URL','http://127.0.0.1:1234/v1')
    transport(monkeypatch,dst_validation=True)
    out=tmp_path/'reports/runs/fresh'
    assert pilot.main(['--execute-controlled','--cases',str(SOURCE),'--batch','2','--private-dir',str(out)])==0
    r=json.loads((out/'raw.json').read_text());m=json.loads((out/'manifest.json').read_text())
    assert r['batch']==m['batch']==2 and m['protocol']==protocol.SCHEMA
    assert len(r['results'])==len(m['selected_case_ids'])==6 and m['runtime_unchanged']
    assert all(p.stat().st_mode & 0o777==0o600 for p in out.iterdir())
    assert out.stat().st_mode & 0o777==0o700
    assert 'model_requests' not in capsys.readouterr().out
    with pytest.raises(FileExistsError):
        pilot.main(['--execute-controlled','--cases',str(SOURCE),'--batch','2','--private-dir',str(out)])


def test_missing_batch_cli_rejects_before_runtime_or_directory(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pilot,'PilotClient',lambda *_:pytest.fail('No runtime construction'))
    out=tmp_path/'reports/runs/no'
    with pytest.raises(ValueError):pilot.main(['--execute-controlled','--cases',str(SOURCE),'--private-dir',str(out)])
    assert not out.exists()


@pytest.mark.parametrize('kind', ['legacy_routes', 'drop_dst_route', 'drop_input_gate'])
def test_protocol_boundary_cannot_silently_relax_routes(kind):
    if kind == 'legacy_routes':
        s=json.loads((ROOT/'evals/proposals/v1_controlled_pilot_cases.json').read_text())
        s['cases'][0]['routes']=copy.deepcopy(SUITE['cases'][5]['routes'])
        with pytest.raises(ValueError):pilot.prepare_suite(s)
    else:
        s=copy.deepcopy(SUITE)
        if kind=='drop_dst_route':s['cases'][5]['routes']=s['cases'][5]['routes'][:1]
        else:s['cases'][14]['input_message']=None
        with pytest.raises(ValueError):pilot.prepare_suite(s,1)


def test_fresh_preflight_failure_keeps_batch_and_excluded_denominators(monkeypatch,tmp_path,capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL',pilot.MODEL)
    monkeypatch.setenv('LM_STUDIO_BASE_URL','http://127.0.0.1:1234/v1')
    def unloaded(self,path,payload=None):
        assert path=='/api/v1/models'
        return {'models':[{'key':pilot.MODEL,'loaded_instances':[]}]}
    monkeypatch.setattr(LocalClient,'request',unloaded)
    out=tmp_path/'reports/runs/preflight'
    assert pilot.main(['--execute-controlled','--cases',str(SOURCE),'--batch','4','--private-dir',str(out)])==1
    r=json.loads((out/'raw.json').read_text())
    assert r['state']=='preflight_error' and r['inference_attempts']==0
    assert r['batch']==4 and len(r['selected_case_ids'])==2 and len(r['excluded_case_ids'])==18
    assert all(x['state']=='not_attempted' for x in r['results'])
    assert json.loads(capsys.readouterr().out)['planned']==2
