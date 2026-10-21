import copy
import json
import socket
from pathlib import Path
from urllib.error import HTTPError

import pytest

from harness import calendar_pilot as pilot
from harness.client import LocalClient

ROOT = Path(__file__).parents[1]
SUITE = json.loads((ROOT / 'evals/proposals/v1_controlled_pilot_cases.json').read_text())
RAW = 'Original model prose retained for human review, not a semantic PASS.'
RUNTIME = {'key': pilot.MODEL, 'loaded_instances': [{'config': {'context_length': 8192}}]}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket, 'socket', lambda *a, **k: pytest.fail('No live model or Google allowed'))
    monkeypatch.setattr('harness.retry.time.sleep', lambda _: None)


def tool_call(case):
    c = case['expected_calls'][0]
    return {'role': 'assistant', 'tool_calls': [{'id': 'one', 'type': 'function',
            'function': {'name': c['name'], 'arguments': json.dumps(c['arguments'])}}]}


def transport(monkeypatch, override=None):
    captures = []
    def request(self, path, payload=None):
        captures.append(copy.deepcopy((path, payload)))
        if path == '/api/v1/models':
            return {'models': [copy.deepcopy(RUNTIME)]}
        assert path == '/chat/completions'
        case = next(c for c in SUITE['cases'] if c['prompt'] == payload['messages'][1]['content'])
        message = tool_call(case) if case['expected_calls'] and len(payload['messages']) == 2 else {'role': 'assistant', 'content': RAW}
        if override:
            message = override(case, payload, message)
        return {'choices': [{'message': message, 'finish_reason': 'stop'}]}
    monkeypatch.setattr(LocalClient, 'request', request)
    return captures


def client(cap=18, clock=lambda: 0):
    return pilot.PilotClient(pilot.Limits(cap, clock=clock), model=pilot.MODEL)


def test_six_case_actual_loop_fake_api_refs_and_snapshots(monkeypatch):
    captures = transport(monkeypatch)
    model = client()
    snapshots = []
    original = copy.deepcopy(SUITE)
    report = pilot.run_suite(SUITE, model, progress=snapshots.append)
    assert report['state'] == 'completed' and report['inference_attempts'] == 10
    assert len(captures) == 10 and sum(len(r['api_calls']) for r in report['results']) == 5
    assert all(r['automated_pass'] for r in report['results'])
    assert [r['run']['product_output']['render_status'] for r in report['results']] == ['rendered'] * 4 + ['unsupported', 'unknown']
    assert [r['expected_agent_exit'] for r in report['results']] == [0, 0, 0, 0, 1, 1]
    assert all(r['human_product_review'] == 'pending' for r in report['results'])
    assert report['results'][4]['raw_answer_review'] == 'not_applicable_no_inference'
    assert report['results'][4]['run']['answer'] == ''
    assert report['results'][4]['run']['input_validation']['model_called'] is False
    assert not any(r['case_id'] == 'v1p-05' for r in report['model_requests'])
    assert not report['semantic_pass_claim'] and report['google_requests'] == report['judge_requests'] == 0
    assert SUITE == original
    assert len(model.requests[0]['payload']['messages']) == 2  # No later mutable-message additions.
    assert len(model.requests[1]['payload']['messages']) == 4
    assert snapshots[0]['results'][0]['state'] == 'not_attempted'
    assert snapshots[-1]['state'] == 'completed'
    report['results'][0]['run']['answer'] = 'mutated'
    assert snapshots[-1]['results'][0]['run']['answer'] == RAW


@pytest.mark.parametrize('change', ['wrong_args', 'unknown_tool', 'extra', 'no_tool_case'])
def test_wrong_or_extra_calls_stop_before_simulated_operation(monkeypatch, change):
    if change == 'no_tool_case':
        # Independently exercise the runner guard beneath the production input gate.
        monkeypatch.setattr('harness.calendar_agent.date_clarification', lambda *_: None)
    def altered(case, payload, message):
        if change == 'no_tool_case':
            if case['id'] == 'v1p-05': return tool_call(SUITE['cases'][0])
            return message
        if case['id'] != 'v1p-01': return message
        if change == 'extra' and len(payload['messages']) > 2: return tool_call(case)
        if change == 'wrong_args':
            args = json.loads(message['tool_calls'][0]['function']['arguments'])
            args['start'] = '2029-01-23T10:10:00'
            message['tool_calls'][0]['function']['arguments'] = json.dumps(args)
        if change == 'unknown_tool': message['tool_calls'][0]['function']['name'] = 'create_event'
        return message
    transport(monkeypatch, altered)
    report = pilot.run_suite(SUITE, client())
    assert report['state'] == 'unexpected_tool'
    row = next(r for r in report['results'] if r['state'] == 'incomplete')
    assert len(row['api_calls']) == (1 if change == 'extra' else 0)
    assert row['partial_events'][-1]['type'] == 'assistant'
    assert any(r['state'] == 'not_attempted' for r in report['results'])
    assert 'automated_pass' not in row


def test_adapter_guard_cannot_execute_extra_or_wrong_read():
    c = pilot.GuardedCalendar(SUITE['cases'][0])
    with pytest.raises(pilot.StopPilot): c.check_availability('wrong', 'wrong')
    assert c.calls == []
    c.check_availability(**c.expected)
    with pytest.raises(pilot.StopPilot): c.check_availability(**c.expected)
    assert len(c.calls) == 1


def test_retry_counts_physical_requests_and_cap_blocks_second_send(monkeypatch):
    calls = []
    def unavailable(self, path, payload=None):
        calls.append(path)
        raise HTTPError('http://localhost', 503, 'unavailable', {}, None)
    monkeypatch.setattr(LocalClient, 'request', unavailable)
    model = client(cap=1)
    r = pilot.run_suite(SUITE, model)
    assert calls == ['/chat/completions']
    assert r['state'] == 'budget_exhausted' and r['inference_attempts'] == 1
    assert r['model_requests'][0]['error_type'] == 'HTTPError'
    assert r['results'][0]['state'] == 'incomplete'
    assert len([x for x in r['results'] if x['state'] == 'not_attempted']) == 5


def test_transient_retry_then_success_keeps_failed_attempt(monkeypatch):
    transport(monkeypatch)
    normal = LocalClient.request
    seen = []
    def retry(self, path, payload=None):
        seen.append(path)
        if len(seen) == 1: raise HTTPError('http://localhost', 503, 'transient', {}, None)
        return normal(self, path, payload)
    monkeypatch.setattr(LocalClient, 'request', retry)
    r = pilot.run_suite(SUITE, client())
    assert r['state'] == 'completed' and r['inference_attempts'] == 11
    assert [x['state'] for x in r['model_requests'][:2]] == ['error', 'returned']


def test_deadline_checked_before_retry_and_preserves_completed_case(monkeypatch):
    now = [0]
    def alter(case, payload, message):
        if case['id'] == 'v1p-01' and len(payload['messages']) > 2: now[0] = 600
        return message
    transport(monkeypatch, alter)
    r = pilot.run_suite(SUITE, client(clock=lambda: now[0]))
    assert r['state'] == 'deadline_exhausted'
    assert r['results'][0]['automated_pass']
    assert all(x['state'] == 'not_attempted' for x in r['results'][1:])
    assert r['inference_attempts'] == 2


def test_keyboard_interrupt_preserves_tool_evidence_and_all_planned_rows(monkeypatch):
    def interrupt(case, payload, message):
        if len(payload['messages']) > 2: raise KeyboardInterrupt
        return message
    transport(monkeypatch, interrupt)
    r = pilot.run_suite(SUITE, client())
    assert r['state'] == 'interrupted'
    assert r['results'][0]['partial_events'][-1]['type'] == 'tool'
    assert len(r['results'][0]['api_calls']) == 1 and len(r['results']) == 6
    assert r['model_requests'][-1]['error_type'] == 'KeyboardInterrupt'


def test_runtime_change_stops_before_next_case(monkeypatch):
    transport(monkeypatch)
    calls = []
    def runtime():
        calls.append(1)
        if len(calls) == 2: raise pilot.StopPilot('runtime_changed')
    r = pilot.run_suite(SUITE, client(), runtime_check=runtime)
    assert r['state'] == 'runtime_changed' and r['inference_attempts'] == 2
    assert r['results'][0]['automated_pass'] and r['results'][1]['state'] == 'not_attempted'


@pytest.mark.parametrize('mutation', ['language', 'offset', 'fixture', 'ids', 'status'])
def test_invalid_references_fail_before_model_calls(monkeypatch, mutation):
    s = copy.deepcopy(SUITE)
    if mutation == 'language': s['cases'][0]['language'] = 'es'
    if mutation == 'offset': s['cases'][0]['expected_api_interval']['start'] = '2029-01-23T09:10:00-07:00'
    if mutation == 'fixture': s['cases'][0]['fixture']['mode'] = 'live'
    if mutation == 'ids': s['cases'][1]['id'] = 'v1p-01'
    if mutation == 'status': s['cases'][5]['expected']['status'] = 'rendered'
    transport(monkeypatch)
    m = client()
    with pytest.raises(ValueError): pilot.run_suite(s, m)
    assert m.requests == []


@pytest.mark.parametrize('cap,seconds', [(0, 600), (19, 600), (True, 600), (1, 0), (1, 601), (1, float('nan')), (1, float('inf'))])
def test_invalid_budgets(cap, seconds):
    with pytest.raises(ValueError): pilot.Limits(cap, seconds)


def test_grading_never_uses_prose_as_fact_and_wrong_reference_stays_failure(monkeypatch):
    transport(monkeypatch)
    r = pilot.run_suite(SUITE, client())
    row = r['results'][0]
    case = SUITE['cases'][0]
    cal = pilot.GuardedCalendar(case); cal.calls = row['api_calls']
    damaged = copy.deepcopy(row['run'])
    damaged['product_output']['rendered_answer'] = 'Looks right!'
    assert not pilot.grade(case, damaged, cal)['product_reference_match']
    damaged = copy.deepcopy(row['run'])
    next(e for e in damaged['events'] if e['type'] == 'tool')['result']['time_facts']['query_interval']['in_query_timezone']['start']['datetime'] = 'wrong'
    assert not pilot.grade(case, damaged, cal)['python_facts_match']


def test_legacy_evaluator_default_still_has_no_product_output():
    from harness.calendar_evaluate import evaluate
    legacy = json.loads((ROOT / 'evals/calendar_cases.json').read_text())
    r = evaluate(legacy, lambda *_: {'role': 'assistant', 'content': 'Please clarify.'})
    assert len(r['results']) == 15
    assert all('product_output' not in x['run'] for x in r['results'])


def test_cli_opt_in_and_existing_directory_stop_before_runtime(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pilot, 'PilotClient', lambda *_: pytest.fail('Must stop before runtime'))
    with pytest.raises(SystemExit): pilot.main(['--private-dir', 'reports/runs/new'])
    existing = tmp_path / 'reports/runs/existing'; existing.mkdir(parents=True)
    sentinel = existing / 'old'; sentinel.write_text('preserved')
    with pytest.raises(FileExistsError):
        pilot.main(['--execute-controlled', '--cases', str(ROOT / 'evals/proposals/v1_controlled_pilot_cases.json'), '--private-dir', str(existing)])
    assert sentinel.read_text() == 'preserved'


def test_cli_fake_transport_private_evidence_and_expected_nonrendered_exit(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL', pilot.MODEL)
    monkeypatch.setenv('LM_STUDIO_BASE_URL', 'http://127.0.0.1:1234/v1')
    captures = transport(monkeypatch)
    out = tmp_path / 'reports/runs/pilot'
    code = pilot.main(['--execute-controlled', '--cases', str(ROOT / 'evals/proposals/v1_controlled_pilot_cases.json'), '--private-dir', str(out)])
    assert code == 0  # Harness matches expected unknown/unsupported; not agent exit 0 or semantic PASS.
    r = json.loads((out / 'raw.json').read_text())
    m = json.loads((out / 'manifest.json').read_text())
    assert m['runtime_unchanged'] and m['runtime_before'] == m['runtime_after']
    assert m['max_attempts'] == 18 and len(m['suite_sha256']) == 64
    assert all(path == '/chat/completions' or path == '/api/v1/models' for path, _ in captures)
    assert (out.stat().st_mode & 0o777) == 0o700
    assert all((p.stat().st_mode & 0o777) == 0o600 for p in out.iterdir())
    assert RAW in (out / 'raw.json').read_text() and RAW not in capsys.readouterr().out
    assert r['results'][4]['run']['product_output']['rendered_answer'] is None


def test_retry_deadline_blocks_physical_resend(monkeypatch):
    now, sends = [0], []
    def timeout(self, path, payload=None):
        sends.append(path); now[0] = 600
        raise HTTPError('http://localhost', 503, 'transient', {}, None)
    monkeypatch.setattr(LocalClient, 'request', timeout)
    r = pilot.run_suite(SUITE, client(clock=lambda: now[0]))
    assert r['state'] == 'deadline_exhausted' and len(sends) == r['inference_attempts'] == 1


def test_supported_raw_run_and_model_payload_unchanged_by_pilot(monkeypatch):
    from datetime import datetime
    from harness.calendar_agent import run_calendar_agent
    from harness.calendar_evaluate import ControlledCalendar
    captures = transport(monkeypatch)
    case = SUITE['cases'][0]
    normal = run_calendar_agent(case['prompt'], LocalClient(model=pilot.MODEL),
                               ControlledCalendar(case['fixture']['mode'], case['fixture']['busy']),
                               now=datetime.fromisoformat(SUITE['reference_now']))
    plain_requests = copy.deepcopy(captures)
    captures.clear()
    report = pilot.run_suite(SUITE, client())
    actual = copy.deepcopy(report['results'][0]['run'])
    actual.pop('product_output')
    assert actual == normal
    assert captures[:2] == plain_requests


@pytest.mark.parametrize('kind', ['interrupt', 'unloaded', 'changed'])
def test_cli_partial_or_preflight_failure_persists_honest_state(monkeypatch, tmp_path, capsys, kind):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL', pilot.MODEL)
    transport(monkeypatch)
    normal, native_calls = LocalClient.request, []
    def fail(self, path, payload=None):
        if path == '/api/v1/models':
            native_calls.append(path)
            if kind == 'unloaded': return {'models': [{'key': pilot.MODEL, 'loaded_instances': []}]}
            if kind == 'changed' and len(native_calls) >= 3:
                changed = copy.deepcopy(RUNTIME)
                changed['loaded_instances'][0]['id'] = 'different-instance'
                return {'models': [changed]}
        if kind == 'interrupt' and path == '/chat/completions' and len(payload['messages']) > 2:
            raise KeyboardInterrupt
        return normal(self, path, payload)
    monkeypatch.setattr(LocalClient, 'request', fail)
    out = tmp_path / 'reports/runs/partial'
    result = pilot.main(['--execute-controlled', '--cases', str(ROOT / 'evals/proposals/v1_controlled_pilot_cases.json'), '--private-dir', str(out)])
    assert result == 1
    saved = json.loads((out / 'raw.json').read_text())
    assert len(saved['results']) == 6 and not saved['semantic_pass_claim']
    if kind == 'unloaded':
        assert saved['state'] == 'preflight_error' and saved['inference_attempts'] == 0
        assert all(r['state'] == 'not_attempted' for r in saved['results'])
    elif kind == 'interrupt':
        assert saved['state'] == 'interrupted' and saved['inference_attempts'] == 2
        assert saved['results'][0]['partial_events'][-1]['type'] == 'tool'
    else:
        assert saved['state'] == 'runtime_changed' and saved['inference_attempts'] == 2
        assert saved['results'][0]['automated_pass']
        assert saved['results'][1]['state'] == 'not_attempted'
    assert RAW not in capsys.readouterr().out
