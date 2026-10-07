import json
from urllib.error import HTTPError
import pytest
from harness.retry import retry_call
from harness.calendar_agent import executor_for
from harness.calendar_tools import CalendarTools, CalendarError
from harness.client import LocalClient
from harness.agent import run_agent


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr('harness.retry.time.sleep', lambda seconds: None)


@pytest.mark.parametrize('code,expected', [(429,3),(503,3),(401,1),(403,1),(400,1)])
def test_http_retry_limit_and_classification(code, expected):
    attempts = []
    def fail():
        raise HTTPError('http://localhost', code, 'error', {}, None)
    with pytest.raises(HTTPError):
        retry_call(fail, attempts)
    assert len(attempts) == expected
    assert attempts[-1]['retry'] is False
    assert [a['wait_seconds'] for a in attempts] == ([1,2,0] if expected == 3 else [0])


def test_transient_recovery_records_both_attempts():
    attempts = []
    responses = iter([TimeoutError(), 'success'])
    def call():
        result = next(responses)
        if isinstance(result, Exception): raise result
        return result
    assert retry_call(call, attempts) == 'success'
    assert [a['outcome'] for a in attempts] == ['error','success']


def test_model_failure_preserves_attempts_and_does_not_invoke_tools(monkeypatch):
    client = LocalClient()
    def fail(*args): raise TimeoutError()
    monkeypatch.setattr(client, 'request', fail)
    def forbidden(*args): pytest.fail('Tool must not be called')
    result = run_agent('check', client, executor=forbidden)
    assert result['status'] == 'model_error'
    assert len(result['events']) == 3
    assert result['events'][-1]['retry'] is False


def test_judge_transport_remains_single_attempt(monkeypatch):
    client = LocalClient()
    calls = []
    def fail(*args, **kwargs):
        calls.append(1)
        raise TimeoutError()
    monkeypatch.setattr('harness.client.urlopen', fail)
    with pytest.raises(TimeoutError): client.request('/chat/completions', {})
    assert len(calls) == 1


@pytest.mark.parametrize('statuses', [(503,200),(429,429,429),(403,)])
def test_calendar_retries_only_transient_reads(statuses):
    class Response:
        def __init__(self,status): self.status_code = status
        def json(self): return {'items':[]}
    class Session:
        def __init__(self): self.calls = 0
        def get(self,*args,**kwargs):
            status = statuses[self.calls]; self.calls += 1
            return Response(status)
    session = Session(); tool = CalendarTools('test', session)
    if statuses[-1] == 200:
        result = tool.check_availability('2026-10-06T11:00:00-07:00','2026-10-06T11:30:00-07:00')
        assert result['available'] is True
        assert len(result['attempts']) == 2
    else:
        with pytest.raises(CalendarError): tool.check_availability('2026-10-06T11:00:00-07:00','2026-10-06T11:30:00-07:00')
    assert session.calls == len(statuses)
    assert len(tool.attempt_events) == len(statuses)


def test_single_argument_correction_then_block():
    class Calendar:
        def check_availability(self,*args): pytest.fail('Invalid calls must never reach Calendar')
    execute = executor_for(Calendar())
    assert execute('check_availability','{')['corrections_remaining'] == 1
    assert execute('check_availability','{}')['corrections_remaining'] == 0
    valid = json.dumps({'start':'2026-10-06T11:00:00','end':'2026-10-06T11:30:00','time_zone':'America/Los_Angeles'})
    assert execute('check_availability',valid)['error'] == 'retry_limit_reached'


def test_calendar_failure_blocks_new_calls_and_preserves_attempts():
    class Calendar:
        def __init__(self): self.calls = 0; self.attempt_events = []
        def check_availability(self,*args):
            self.calls += 1
            self.attempt_events = [{'attempt':1,'outcome':'error','retry':False}]
            raise CalendarError('authorization failed')
    calendar = Calendar(); execute = executor_for(calendar)
    args = json.dumps({'start':'2026-10-06T11:00:00','end':'2026-10-06T11:30:00','time_zone':'America/Los_Angeles'})
    first = execute('check_availability',args)
    assert first['available'] is None
    assert first['attempts'][0]['outcome'] == 'error'
    assert execute('check_availability',args)['error'] == 'retry_limit_reached'
    assert calendar.calls == 1


def test_core_retry_module_imports_without_calendar_dependencies(monkeypatch):
    import builtins
    import runpy
    from pathlib import Path
    original = builtins.__import__
    def restricted(name, *args, **kwargs):
        if name == 'requests.exceptions': raise ImportError('Calendar extras unavailable')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', restricted)
    module = runpy.run_path(str(Path(__file__).parents[1] / 'src/harness/retry.py'))
    assert module['transient'](TimeoutError())
    assert not module['transient'](ValueError())
