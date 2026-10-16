"""Offline only: scripted model, controlled calendar and fake HTTP transport."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.error import URLError
import pytest
from harness import calendar_live_regression as live
from harness.calendar_evaluate import ControlledCalendar
from harness.calendar_tools import CalendarError, CalendarTools
from harness.client import LocalClient

SUITE = json.loads(Path('evals/calendar_live_readonly_cases.json').read_text())


def scripted():
    replies = []
    for c in SUITE['cases']:
        call = c['expected_calls'][0]
        replies += [{'role': 'assistant', 'tool_calls': [{'id': c['id'], 'type': 'function', 'function': {
            'name': call['name'], 'arguments': json.dumps(call['arguments'])}}]},
            {'role': 'assistant', 'content': 'Offline response; pending semantic review.'}]
    it = iter(replies)
    return lambda *_: next(it)


def calendar():
    return ControlledCalendar('busy_fixture', SUITE['fixtures']['busy_fixture'])


def test_six_queries_and_pending_answers_without_google_or_live_model():
    c = calendar()
    updates = []
    r = live.run_suite(SUITE, scripted(), c, progress=lambda x: updates.append(copy.deepcopy(x)))
    assert r['state'] == 'completed' and len(c.calls) == 6
    assert all(x['fixture_matches'] for x in r['direct'])
    assert all(x['structural_pass'] and x['answer_review']['status'] == 'pending' for x in r['results'])
    assert all(x['fixture_comparison'] == 'same_intervals' for x in r['results'])
    assert any(x['results'] and x['results'][0]['tool_events'] for x in updates)


def test_missing_fixture_stops_before_any_model_call():
    c = ControlledCalendar('empty_interval', SUITE['fixtures']['busy_fixture'])
    r = live.run_suite(SUITE, lambda *_: pytest.fail('Model must not be called'), c)
    assert r['state'] == 'fixture_precondition_failed'
    assert len(c.calls) == 1 and r['results'] == []


def test_adapter_failure_is_unknown_not_free_and_skips_model():
    c = ControlledCalendar('raise_calendar_error', SUITE['fixtures']['busy_fixture'])
    r = live.run_suite(SUITE, lambda *_: pytest.fail('Model must not be called'), c)
    assert r['state'] == 'adapter_error'
    assert 'fixture_matches' not in r['direct'][0]


def test_fixture_drift_is_inconclusive_and_stops_remaining_agent_cases():
    c = calendar()
    original = c.check_availability
    def changing(start, end):
        result = original(start, end)
        if len(c.calls) == 4:
            result.update(available=True, busy_intervals=[])
        return result
    c.check_availability = changing
    r = live.run_suite(SUITE, scripted(), c)
    assert r['state'] == 'fixture_changed'
    assert len(r['results']) == 1 and len(c.calls) == 4
    assert r['results'][0]['fixture_comparison'] == 'changed_intervals'


def test_unplanned_and_extra_agent_reads_never_reach_calendar():
    c = calendar()
    expected = SUITE['cases'][0]['expected_api_interval']
    bounded = live.OneReadCalendar(c, expected)
    with pytest.raises(CalendarError):
        bounded.check_availability('2030-01-01T00:00:00+00:00', '2030-01-01T00:30:00+00:00')
    assert c.calls == []
    bounded.check_availability(**expected)
    with pytest.raises(CalendarError):
        bounded.check_availability(**expected)
    assert len(c.calls) == 1 and len(bounded.attempted_calls) == 3


def test_budget_stop_keeps_completed_and_unattempted_denominators():
    r = live.run_suite(SUITE, scripted(), calendar(), stop_requested=lambda: True)
    assert r['state'] == 'budget_exhausted'
    assert len(r['results']) == 1
    s = live.public_summary(r, live.Budget(), live.Budget())
    assert len(s['cases']) == 3 and s['cases'][1]['agent_structure'] is None


class Inner:
    def __init__(self, statuses=(200,)):
        self.calls, self.statuses = [], iter(statuses)
    def send(self, request, **kwargs):
        self.calls.append(request)
        return SimpleNamespace(status_code=next(self.statuses), close=lambda: None,
                               json=lambda: {'items': []})
    def close(self): pass


def request(method='GET', host='www.googleapis.com', path='/calendar/v3/calendars/test/events'):
    return SimpleNamespace(method=method, url='https://' + host + path + '?timeMin=private-date')


def test_actual_send_budget_includes_repeated_sends_and_blocks_thirteenth():
    inner = Inner((200,) * 12)
    budget = live.Budget()
    guard = live.ReadOnlyAdapter(inner, 'test', budget)
    for _ in range(12): guard.send(request())
    with pytest.raises(live.BudgetExceeded): guard.send(request())
    assert budget.used == len(inner.calls) == len(guard.records) == 12
    assert budget.exhausted


@pytest.mark.parametrize('req', [request('POST'), request(host='other.example'),
    request(path='/calendar/v3/calendars/other/events'),
    request(path='/calendar/v3/calendars/test/events/event-id')])
def test_guard_blocks_writes_other_calendars_and_other_endpoints(req):
    inner = Inner()
    guard = live.ReadOnlyAdapter(inner, 'test', live.Budget())
    with pytest.raises(CalendarError): guard.send(req)
    assert not inner.calls and guard.budget.used == 0


def test_calendar_transport_retry_is_counted_without_real_http(monkeypatch):
    from harness import retry
    monkeypatch.setattr(retry.time, 'sleep', lambda _: None)
    inner = Inner((503, 200))
    guard = live.ReadOnlyAdapter(inner, 'test', live.Budget())
    class Session:
        def get(self, url, **kwargs):
            return guard.send(SimpleNamespace(method='GET', url=url))
    result = CalendarTools('test', Session()).check_availability(
        '2026-10-06T11:30:00-07:00', '2026-10-06T12:00:00-07:00')
    assert result['available'] and guard.budget.used == 2
    assert [x['http_status'] for x in guard.records] == [503, 200]


def test_model_retries_count_against_budget(monkeypatch):
    from harness import retry
    monkeypatch.setattr(retry.time, 'sleep', lambda _: None)
    calls = []
    def fake(self, path, payload=None):
        calls.append(path)
        if len(calls) == 1: raise URLError('offline transient')
        return {'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': 'Offline'}}]}
    monkeypatch.setattr(LocalClient, 'request', fake)
    client = live.BoundedClient(live.Budget(1))
    with pytest.raises(live.BudgetExceeded): client([], [])
    assert client.budget.used == 1 and client.budget.exhausted and len(calls) == 1


def test_public_summary_drops_private_canaries_and_keeps_review_pending():
    r = live.run_suite(SUITE, scripted(), calendar())
    r['private'] = 'CANARY calendar-id token full-answer 2030-01-01'
    r['results'][0]['run']['answer'] = 'CANARY private final answer'
    r['direct'][0]['tool_result']['source'] = 'CANARY calendar identifier'
    summary = live.public_summary(r, live.Budget(), live.Budget())
    raw = json.dumps(summary)
    assert 'CANARY' not in raw and '2026-' not in raw and 'tool_result' not in raw
    assert summary['semantic_pass_claim'] is False
    assert all(x['answer_review'] == 'pending' for x in summary['cases'])


def test_opt_in_checked_before_loading_cases_runtime_or_oauth(monkeypatch, tmp_path):
    monkeypatch.setattr(live, 'connect', lambda: pytest.fail('No credentials access'))
    monkeypatch.setattr(live, 'BoundedClient', lambda *_: pytest.fail('No runtime access'))
    dest = tmp_path / 'never-created'
    with pytest.raises(SystemExit):
        live.main(['--private-dir', str(dest), '--cases', 'does-not-exist'])
    assert not dest.exists()


def test_private_output_is_new_owner_only_and_cannot_be_in_baselines(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    dest = live.private_directory('reports/runs/private-live')
    live.write_private(dest/'raw.json', {'private': 'fixture'})
    assert dest.stat().st_mode & 0o777 == 0o700
    assert (dest/'raw.json').stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError): live.private_directory('reports/runs/private-live')
    with pytest.raises(ValueError): live.private_directory('reports/baseline/private-live')


def test_suite_rejects_changed_expected_instant_before_network():
    suite = copy.deepcopy(SUITE)
    suite['cases'][0]['expected_api_interval']['start'] = '2026-10-06T11:15:00-08:00'
    with pytest.raises(ValueError): live.validate_suite(suite)


@pytest.mark.parametrize('language,api_error', [(None,False), ('en',False), ('zh-TW',False), ('en',True)])
def test_opt_in_cli_end_to_end_uses_fake_http_and_local_model_only(monkeypatch, tmp_path, capsys, language, api_error):
    from datetime import datetime
    from urllib.parse import parse_qs, urlencode, urlsplit
    suite_path = Path('evals/calendar_live_readonly_cases.json').resolve()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL', live.MODEL)
    monkeypatch.delenv('LM_STUDIO_BASE_URL', raising=False)
    monkeypatch.setenv('LM_BASE_URL', 'http://127.0.0.1:1234/v1')
    complete = scripted()
    payloads = []
    runtime = {'key': live.MODEL, 'loaded_instances': [{'config': {'context_length': 8192}}]}
    def local_request(self, path, payload=None):
        if path == '/api/v1/models': return {'models': [runtime]}
        assert path == '/chat/completions'
        payloads.append(copy.deepcopy(payload))
        return {'choices': [{'finish_reason': 'stop', 'message': complete(None, None)}]}
    monkeypatch.setattr(LocalClient, 'request', local_request)
    fixture = SUITE['fixtures']['busy_fixture']
    sends = []
    class FixtureHTTP:
        def send(self, req, **kwargs):
            sends.append(req)
            if api_error and len(sends) == 4:
                return SimpleNamespace(status_code=400, json=lambda: pytest.fail('Do not inspect error body'))
            params = parse_qs(urlsplit(req.url).query)
            overlap = (datetime.fromisoformat(params['timeMin'][0]) < datetime.fromisoformat(fixture['end'])
                       and datetime.fromisoformat(params['timeMax'][0]) > datetime.fromisoformat(fixture['start']))
            items = [{'start': {'dateTime': fixture['start']}, 'end': {'dateTime': fixture['end']}}] if overlap else []
            return SimpleNamespace(status_code=200, json=lambda: {'items': items})
        def close(self): pass
    class Session:
        def __init__(self): self.adapter = FixtureHTTP()
        def get_adapter(self, url): return self.adapter
        def mount(self, prefix, adapter): self.adapter = adapter
        def get(self, url, params, **kwargs):
            return self.adapter.send(SimpleNamespace(method='GET', url=url + '?' + urlencode(params)))
        def close(self): self.adapter.close()
    monkeypatch.setattr(live, 'connect', lambda: CalendarTools('PRIVATE-CALENDAR-CANARY', Session()))
    flags = [] if language is None else ['--renderer', 'python', '--language', language]
    code = live.main(['--live-readonly', '--cases', str(suite_path), '--private-dir', 'reports/runs/test', *flags])
    assert code == int(api_error)
    summary = json.loads(capsys.readouterr().out)
    assert summary['google_events_http_sends'] == summary['model_inference_attempts'] == 6
    assert summary['elapsed_seconds'] >= 0 and len(summary['implementation_sha256']) == 64
    assert 'PRIVATE-CALENDAR-CANARY' not in json.dumps(summary)
    raw = json.loads(Path('reports/runs/test/raw.json').read_text())
    assert len(raw['events_http']) == 6
    assert all(x['structural_pass'] for x in raw['results'][1:])
    assert raw['results'][0]['structural_pass'] is (not api_error)
    assert all(p['temperature'] == 0 and p['max_tokens'] == 2048 for p in payloads)
    assert all('reasoning_effort' not in p for p in payloads)
    if language is None:
        assert 'renderer_counts' not in summary
        assert all('product_output' not in r['run'] for r in raw['results'])
    else:
        assert summary['renderer_counts']['planned'] == 3
        assert summary['renderer_counts']['rendered'] == (2 if api_error else 3)
        assert summary['renderer_counts']['unknown'] == int(api_error)
        assert all(c['renderer_status'] == 'rendered' for c in summary['cases'][1:])
        for row in raw['results']:
            product = row['run']['product_output']
            assert product['language'] == language
            assert product['provenance']['source'] == 'current_python_agent_run'
            assert row['run']['answer'] == 'Offline response; pending semantic review.'
        assert Path('reports/runs/test/raw.json').stat().st_mode & 0o777 == 0o600
        assert len(payloads[0]['messages']) == 2
        assert len(payloads[1]['messages']) == 4


def test_guard_does_not_record_authorization_or_error_response_bodies():
    class ErrorHTTP:
        def send(self, req, **kwargs):
            return SimpleNamespace(status_code=401, json=lambda: pytest.fail('Do not read auth error body'))
        def close(self): pass
    guard = live.ReadOnlyAdapter(ErrorHTTP(), 'test', live.Budget())
    req = request()
    req.headers = {'Authorization': 'Bearer SECRET-CANARY'}
    guard.send(req)
    assert 'SECRET-CANARY' not in json.dumps(guard.records)
    assert 'projected_response' not in guard.records[0]


def test_unloaded_sut_stops_before_oauth_without_auto_loading(monkeypatch, tmp_path, capsys):
    suite_path = Path('evals/calendar_live_readonly_cases.json').resolve()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL', live.MODEL)
    monkeypatch.setattr(LocalClient, 'request', lambda *_: {'models': [{'key': live.MODEL, 'loaded_instances': []}]})
    monkeypatch.setattr(live, 'connect', lambda: pytest.fail('No OAuth before runtime ready'))
    result = live.main(['--live-readonly', '--cases', str(suite_path), '--private-dir', 'reports/runs/blocked'])
    assert result == 1
    summary = json.loads(capsys.readouterr().out)
    assert summary['state'] == 'preflight_error'
    assert summary['google_events_http_sends'] == summary['model_inference_attempts'] == 0


def test_operational_errors_are_not_reported_as_fixture_or_graded_failures():
    c = ControlledCalendar('raise_calendar_error', SUITE['fixtures']['busy_fixture'])
    r = live.run_suite(SUITE, lambda *_: pytest.fail('No model call'), c)
    summary = live.public_summary(r, live.Budget(), live.Budget())
    assert summary['cases'][0]['fixture_precondition'] is None
    assert summary['cases'][0]['agent_structure'] is None
    assert summary['cases'][0]['answer_review'] == 'not_attempted'


@pytest.mark.parametrize('language', [None, 'en'])
def test_cli_interruption_preserves_latest_private_progress(monkeypatch, tmp_path, capsys, language):
    suite_path = Path('evals/calendar_live_readonly_cases.json').resolve()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('SUT_MODEL', live.MODEL)
    runtime = {'key': live.MODEL, 'loaded_instances': [{'config': {'context_length': 8192}}]}
    monkeypatch.setattr(LocalClient, 'request', lambda *_: {'models': [runtime]})
    closed = []
    class Session:
        def get_adapter(self, url): return Inner()
        def mount(self, prefix, adapter): pass
        def close(self): closed.append(True)
    monkeypatch.setattr(live, 'connect', lambda: SimpleNamespace(calendar_id='test', session=Session()))
    def interrupted(suite, complete, calendar, *, progress, stop_requested, renderer_language=None):
        progress({'state': 'running', 'direct': [{'id': live.IDS[0], 'fixture_matches': True}], 'results': []})
        raise KeyboardInterrupt
    monkeypatch.setattr(live, 'run_suite', interrupted)
    flags = [] if language is None else ['--renderer', 'python', '--language', language]
    code = live.main(['--live-readonly', '--cases', str(suite_path), '--private-dir', 'reports/runs/interrupted', *flags])
    assert code == 1 and closed == [True]
    assert json.loads(capsys.readouterr().out)['state'] == 'interrupted'
    raw = json.loads(Path('reports/runs/interrupted/raw.json').read_text())
    assert raw['state'] == 'interrupted' and len(raw['direct']) == 1
    if language is not None:
        assert json.loads(Path('reports/runs/interrupted/summary.json').read_text())['renderer_counts']['not_attempted'] == 3


def test_renderer_preserves_same_raw_runs_and_model_inputs_without_extra_calls(monkeypatch):
    from datetime import datetime, timezone
    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):return datetime(2026,10,5,18,tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr(live,'datetime',Frozen)
    models, calendars, reports = [], [], []
    for language in (None,'en','zh-TW'):
        seen=[];complete=scripted();c=calendar()
        def record(messages,tools):
            seen.append(copy.deepcopy((messages,tools)))
            return complete(messages,tools)
        report=live.run_suite(SUITE,record,c,renderer_language=language)
        if language is not None:
            assert report.pop('renderer_language')==language
            for row in report['results']:
                assert row['run'].pop('product_output')['render_status']=='rendered'
        models.append(seen);calendars.append(c.calls);reports.append(report)
    assert models[0]==models[1]==models[2] and len(models[0])==6
    assert calendars[0]==calendars[1]==calendars[2] and len(calendars[0])==6
    assert reports[0]==reports[1]==reports[2]


@pytest.mark.parametrize('flags', [['--renderer','python'],['--language','en'],['--renderer','python','--language','es']])
def test_renderer_flags_rejected_before_case_reads_or_dependencies(flags,monkeypatch,tmp_path):
    monkeypatch.setattr(live,'BoundedClient',lambda *_:pytest.fail('No runtime'))
    monkeypatch.setattr(live,'connect',lambda:pytest.fail('No OAuth'))
    dest=tmp_path/'not-created'
    with pytest.raises(SystemExit):
        live.main(['--live-readonly','--cases','missing-file','--private-dir',str(dest),*flags])
    assert not dest.exists()
    with pytest.raises(ValueError):
        live.run_suite({},None,None,renderer_language='es')


def test_renderer_unknown_on_agent_api_failure_and_unsupported_without_tools():
    c=calendar();original=c.check_availability
    def fail_first_agent(start,end):
        if len(c.calls)==3:
            c.calls.append({'start':start,'end':end});raise CalendarError('PRIVATE-ERROR-CANARY')
        return original(start,end)
    c.check_availability=fail_first_agent
    r=live.run_suite(SUITE,scripted(),c,renderer_language='en')
    assert r['results'][0]['run']['product_output']['render_status']=='unknown'
    summary=live.public_summary(r,live.Budget(),live.Budget())
    assert summary['renderer_counts']['unknown']==1
    assert 'PRIVATE-ERROR-CANARY' not in json.dumps(summary)
    replies=[{'role':'assistant','content':'PRIVATE-ANSWER-CANARY free!'}]
    for case in SUITE['cases'][1:]:
        function=case['expected_calls'][0]
        replies.extend([{'role':'assistant','tool_calls':[{'id':'one','type':'function','function':{
            'name':function['name'],'arguments':json.dumps(function['arguments'])}}]},
            {'role':'assistant','content':'PRIVATE-ANSWER-CANARY'}])
    iterator=iter(replies)
    r=live.run_suite(SUITE,lambda *_:next(iterator),calendar(),renderer_language='en')
    product=r['results'][0]['run']['product_output']
    assert product['render_status']=='unsupported' and product['rendered_answer'] is None
    summary=live.public_summary(r,live.Budget(),live.Budget())
    assert summary['renderer_counts']['unsupported']==1 and 'PRIVATE-ANSWER-CANARY' not in json.dumps(summary)


def test_renderer_summary_is_allowlisted_and_has_unattempted_denominators():
    r=live.run_suite(SUITE,scripted(),calendar(),renderer_language='en',stop_requested=lambda:True)
    r['results'][0]['run']['product_output'].update(render_status='PRIVATE-CANARY 2030-01-01',rendered_answer='PRIVATE-CANARY')
    summary=live.public_summary(r,live.Budget(),live.Budget())
    counts=summary['renderer_counts']
    assert counts['planned']==3 and counts['unavailable']==1 and counts['not_attempted']==2
    assert sum(v for k,v in counts.items() if k!='planned')==3
    assert 'PRIVATE-CANARY' not in json.dumps(summary) and '2030-' not in json.dumps(summary)
    assert summary['semantic_pass_claim'] is False
    failed=live.run_suite(SUITE,None,ControlledCalendar('raise_calendar_error',SUITE['fixtures']['busy_fixture']),renderer_language='en')
    assert live.public_summary(failed,live.Budget(),live.Budget())['renderer_counts']['not_attempted']==3
