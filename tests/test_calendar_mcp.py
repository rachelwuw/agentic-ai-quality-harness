import asyncio
import pytest
pytest.importorskip('mcp')
from harness import calendar_mcp


def test_mcp_exposes_only_read_tools():
    tools = asyncio.run(calendar_mcp.server.list_tools())
    assert {tool.name for tool in tools} == {'check_availability', 'get_current_time'}


def test_adapter_reuses_tool_and_closes_session(monkeypatch):
    calls = []
    class Session:
        def close(self):
            calls.append('closed')
    class Calendar:
        session = Session()
        def check_availability(self, start, end):
            calls.append((start, end))
            return {'available': True}
    monkeypatch.setattr(calendar_mcp, 'connect', lambda: Calendar())
    assert calendar_mcp.check_availability('2026-10-06T10:00:00', '2026-10-06T10:30:00')['available']
    assert calls == [('2026-10-06T10:00:00-07:00', '2026-10-06T10:30:00-07:00'), 'closed']


def test_invalid_time_does_not_open_google_connection(monkeypatch):
    monkeypatch.setattr(calendar_mcp, 'connect', lambda: pytest.fail('Connection should not open'))
    result = calendar_mcp.check_availability('tomorrow', 'later')
    assert result['error'] == 'invalid_time_format'
    assert result['available'] is None


def test_mcp_and_python_agent_share_converted_event_facts(monkeypatch):
    from harness.calendar_agent import executor_for
    import json
    closed = []
    class Session:
        def close(self): closed.append(True)
    class Calendar:
        session = Session()
        def check_availability(self, start, end):
            return {'start': start, 'end': end, 'available': False, 'busy_intervals': [
                {'start': {'dateTime': '2026-10-06T11:00:00-07:00'},
                 'end': {'dateTime': '2026-10-06T11:30:00-07:00'}}]}
    monkeypatch.setattr(calendar_mcp, 'connect', lambda: Calendar())
    args = {'start': '2026-10-07T02:15:00', 'end': '2026-10-07T02:45:00', 'time_zone': 'Asia/Taipei'}
    actual = calendar_mcp.check_availability(**args)
    assert actual == executor_for(Calendar())('check_availability', json.dumps(args))
    assert actual['time_facts']['busy_intervals'][0]['in_query_timezone']['start']['datetime'] == '2026-10-07T02:00:00+08:00'
    assert closed == [True]
