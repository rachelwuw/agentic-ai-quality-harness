"""Deterministic API simulations; these do not use Google or the local model."""
import pytest
from harness.calendar_tools import CalendarTools, CalendarError, validate_interval

START = '2026-10-06T10:00:00-07:00'
END = '2026-10-06T10:30:00-07:00'
BUSY = {'start': {'dateTime': START}, 'end': {'dateTime': END}}


class Response:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status
    def json(self):
        return self.data


class Session:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []
    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_empty_calendar_and_request_boundaries():
    session = Session(Response({'items': []}))
    result = CalendarTools('test@example.com', session).check_availability(START, END)
    assert result['available'] is True
    url, request = session.calls[0]
    assert 'test%40example.com/events' in url
    assert request['params']['timeMin'] == START
    assert request['params']['timeMax'] == END
    assert request['params']['singleEvents'] == 'true'


def test_conflict_on_second_page_and_free_events_ignored():
    session = Session(Response({'items': [{**BUSY, 'transparency': 'transparent'},
                                          {**BUSY, 'status': 'cancelled'}], 'nextPageToken': 'next'}),
                      Response({'items': [BUSY]}))
    result = CalendarTools('test', session).check_availability(START, END)
    assert result['available'] is False
    assert result['busy_intervals'] == [BUSY]
    assert session.calls[1][1]['params']['pageToken'] == 'next'


def test_all_day_event_blocks_time():
    event = {'start': {'date': '2026-10-06'}, 'end': {'date': '2026-10-07'}}
    result = CalendarTools('test', Session(Response({'items': [event]}))).check_availability(START, END)
    assert not result['available']
    assert result['busy_intervals'] == [event]


@pytest.mark.parametrize('response', [Response({}, 403), Response({}, 500), TimeoutError('secret'),
                                      Response({'items': [{}]}), Response({'items': 'invalid'})])
def test_failures_never_report_free(response):
    with pytest.raises(CalendarError):
        CalendarTools('test', Session(response)).check_availability(START, END)


def test_partial_read_failure_never_reports_free():
    with pytest.raises(CalendarError):
        CalendarTools('test', Session(Response({'items': [], 'nextPageToken': 'next'}),
                                      Response({}, 503))).check_availability(START, END)


@pytest.mark.parametrize('start,end', [('2026-10-06T10:00:00', END), (END, START), (START, START),
                                     ('bad', END), (START, '2026-12-06T10:00:00-08:00')])
def test_invalid_times_rejected_before_api_call(start, end):
    session = Session()
    with pytest.raises(ValueError):
        CalendarTools('test', session).check_availability(start, end)
    assert not session.calls


def test_offsets_are_compared_as_instants():
    with pytest.raises(ValueError):
        validate_interval('2026-10-06T10:00:00-07:00', '2026-10-06T16:30:00Z')


def test_primary_calendar_rejected():
    with pytest.raises(ValueError):
        CalendarTools('primary', Session())


def test_omitted_items_on_final_page_is_an_empty_collection():
    result = CalendarTools('test', Session(Response({}))).check_availability(START, END)
    assert result['available'] is True
    assert result['busy_intervals'] == []


def test_omitted_items_does_not_skip_a_later_conflict():
    session = Session(Response({'nextPageToken': 'next'}), Response({'items': [BUSY]}))
    result = CalendarTools('test', session).check_availability(START, END)
    assert result['available'] is False
    assert result['busy_intervals'] == [BUSY]
    assert session.calls[1][1]['params']['pageToken'] == 'next'


@pytest.mark.parametrize('token', [None, False, 0, '', ' ', [], {}, 7])
def test_present_invalid_page_token_never_reports_availability(token):
    session = Session(Response({'items': [], 'nextPageToken': token}))
    with pytest.raises(CalendarError):
        CalendarTools('test', session).check_availability(START, END)
    assert len(session.calls) == 1


@pytest.mark.parametrize('data', [None, [], 'invalid', 0])
def test_non_object_response_never_reports_availability(data):
    with pytest.raises(CalendarError):
        CalendarTools('test', Session(Response(data))).check_availability(START, END)


def test_omitted_items_followed_by_failed_page_never_reports_availability():
    session = Session(Response({'nextPageToken': 'next'}), Response({}, 403))
    with pytest.raises(CalendarError):
        CalendarTools('test', session).check_availability(START, END)
    assert len(session.calls) == 2


def test_repeated_page_token_never_reports_availability():
    session = Session(Response({'nextPageToken': 'next'}), Response({'nextPageToken': 'next'}))
    with pytest.raises(CalendarError):
        CalendarTools('test', session).check_availability(START, END)
    assert len(session.calls) == 2
