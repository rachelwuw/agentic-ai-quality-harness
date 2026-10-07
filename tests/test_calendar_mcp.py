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
