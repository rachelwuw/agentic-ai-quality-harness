import json
from datetime import datetime
from harness.calendar_agent import executor_for, run_calendar_agent
from harness.calendar_tools import CalendarError


class Calendar:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail
    def check_availability(self, start, end):
        self.calls.append((start, end))
        if self.fail:
            raise CalendarError('private error')
        return {'available': True, 'busy_intervals': []}


def test_real_tool_interface_observation_reaches_model():
    seen = []
    calendar = Calendar()
    call = {'role': 'assistant', 'tool_calls': [{'id': 'one', 'type': 'function',
            'function': {'name': 'check_availability', 'arguments': json.dumps({
                'start': '2026-10-06T10:00:00', 'end': '2026-10-06T10:30:00', 'time_zone': 'America/Los_Angeles'})}}]}
    responses = iter([call, {'role': 'assistant', 'content': 'Test calendar is free.'}])
    def model(messages, tools):
        seen.append(json.loads(json.dumps(messages)))
        assert [t['function']['name'] for t in tools] == ['check_availability']
        return next(responses)
    result = run_calendar_agent('Check tomorrow at 10 for 30 minutes', model, calendar,
                                now=datetime.fromisoformat('2026-10-05T12:00:00-07:00'))
    assert result['status'] == 'completed'
    assert calendar.calls == [('2026-10-06T10:00:00-07:00', '2026-10-06T10:30:00-07:00')]
    assert json.loads(seen[1][-1]['content'])['available'] is True
    assert '2026-10-05' in seen[0][0]['content']


def test_write_and_extra_arguments_blocked():
    calendar = Calendar()
    execute = executor_for(calendar)
    assert execute('create_event', '{}')['error'] == 'unknown_tool'
    assert execute('check_availability', '{"start":"x","end":"y","calendar_id":"primary"}')['error'] == 'invalid_arguments'
    assert execute('check_availability', '{')['error'] == 'invalid_json'
    assert not calendar.calls


def test_google_failure_is_unknown_not_free():
    result = executor_for(Calendar(fail=True))('check_availability', json.dumps({'start': '2026-10-06T10:00:00', 'end': '2026-10-06T10:30:00', 'time_zone': 'America/Los_Angeles'}))
    assert result == {'error': 'calendar_unavailable', 'available': None}


def test_clarification_can_finish_without_calendar_call():
    calendar = Calendar()
    result = run_calendar_agent('Am I free?', lambda *_: {'role': 'assistant', 'content': 'Which date and time?'}, calendar)
    assert not calendar.calls
    assert result['status'] == 'completed'


def test_format_feedback_then_corrected_retry_preserves_cross_midnight():
    calendar = Calendar()
    bad = {'start': '2026-10-06T23:45:00', 'end': '2026-10-07T0015:00', 'time_zone': 'America/Los_Angeles'}
    good = {**bad, 'end': '2026-10-07T00:15:00'}
    def call(args, cid):
        return {'role': 'assistant', 'tool_calls': [{'id': cid, 'type': 'function', 'function': {'name': 'check_availability', 'arguments': json.dumps(args)}}]}
    responses = iter([call(bad, 'bad'), call(good, 'corrected'), {'role': 'assistant', 'content': 'The requested cross-midnight interval is free.'}])
    def model(messages, tools):
        if messages[-1]['role'] == 'tool' and len(calendar.calls) == 0:
            feedback = json.loads(messages[-1]['content'])
            assert feedback['error'] == 'invalid_time_format'
            assert feedback['cross_midnight_supported'] is True
            assert '00:15:00' in feedback['message']
        return next(responses)
    run = run_calendar_agent('October 6 at 23:45 to October 7 at 00:15 Los Angeles', model, calendar)
    assert run['status'] == 'completed'
    assert calendar.calls == [('2026-10-06T23:45:00-07:00', '2026-10-07T00:15:00-07:00')]


def test_dst_feedback_requires_clarification_not_format_retry():
    calendar = Calendar()
    feedback = executor_for(calendar)('check_availability', json.dumps({'start': '2026-11-01T01:15:00', 'end': '2026-11-01T02:30:00', 'time_zone': 'America/Los_Angeles'}))
    assert feedback['error'] == 'dst_time_requires_clarification'
    assert 'do not retry by guessing' in feedback['action']
    assert not calendar.calls
