import pytest
from harness.calendar_tools import resolve_local_interval


@pytest.mark.parametrize('date,offset', [('2026-10-06', '-07:00'), ('2026-12-06', '-08:00')])
def test_los_angeles_offset_is_resolved_by_date(date, offset):
    assert resolve_local_interval(date + 'T11:15:00', date + 'T11:45:00', 'America/Los_Angeles') == (date + 'T11:15:00' + offset, date + 'T11:45:00' + offset)


@pytest.mark.parametrize('start,end,zone', [
    ('2026-10-06T11:15:00-08:00', '2026-10-06T11:45:00-08:00', 'America/Los_Angeles'),
    ('2026-03-08T02:15:00', '2026-03-08T03:30:00', 'America/Los_Angeles'),
    ('2026-11-01T01:15:00', '2026-11-01T02:30:00', 'America/Los_Angeles'),
    ('2026-10-06T11:15:00', '2026-10-06T11:45:00', 'not/a/timezone'),
    ('2026-10-06T12:00:00', '2026-10-06T11:00:00', 'America/Los_Angeles'),
])
def test_bad_or_ambiguous_times_are_rejected(start, end, zone):
    with pytest.raises(ValueError):
        resolve_local_interval(start, end, zone)


def test_dst_crossing_compares_absolute_elapsed_time():
    assert resolve_local_interval('2026-03-08T01:30:00', '2026-03-08T03:30:00', 'America/Los_Angeles') == ('2026-03-08T01:30:00-08:00', '2026-03-08T03:30:00-07:00')


@pytest.mark.parametrize('query_start,query_end,zone,event_start,event_end,local_start,local_end,start_label,end_label', [
    ('2027-07-14T11:15:00', '2027-07-14T11:45:00', 'America/Los_Angeles',
     '2027-07-14T18:00:00+00:00', '2027-07-14T18:30:00+00:00',
     '2027-07-14T11:00:00-07:00', '2027-07-14T11:30:00-07:00', 'PDT', 'PDT'),
    ('2027-01-14T11:15:00', '2027-01-14T11:45:00', 'America/Los_Angeles',
     '2027-01-14T19:00:00+00:00', '2027-01-14T19:30:00+00:00',
     '2027-01-14T11:00:00-08:00', '2027-01-14T11:30:00-08:00', 'PST', 'PST'),
    ('2026-10-07T02:15:00', '2026-10-07T02:45:00', 'Asia/Taipei',
     '2026-10-06T11:00:00-07:00', '2026-10-06T11:30:00-07:00',
     '2026-10-07T02:00:00+08:00', '2026-10-07T02:30:00+08:00', 'CST', 'CST'),
    ('2027-01-06T08:45:00', '2027-01-06T09:15:00', 'America/Los_Angeles',
     '2027-01-07T00:30:00+08:00', '2027-01-07T01:00:00+08:00',
     '2027-01-06T08:30:00-08:00', '2027-01-06T09:00:00-08:00', 'PST', 'PST'),
    ('2026-03-08T01:45:00', '2026-03-08T03:45:00', 'America/Los_Angeles',
     '2026-03-08T01:30:00-08:00', '2026-03-08T03:30:00-07:00',
     '2026-03-08T01:30:00-08:00', '2026-03-08T03:30:00-07:00', 'PST', 'PDT'),
])
def test_tool_event_facts_use_existing_conversion_and_preserve_original(
        query_start, query_end, zone, event_start, event_end,
        local_start, local_end, start_label, end_label):
    import copy
    from harness.calendar_tools import check_local_availability
    from harness.trace_facts import interval
    original = {'available': False, 'busy_intervals': [
        {'start': {'dateTime': event_start}, 'end': {'dateTime': event_end}}]}
    snapshot = copy.deepcopy(original)
    class Calendar:
        calls = []
        def check_availability(self, start, end):
            self.calls.append((start, end))
            return original
    calendar = Calendar()
    result = check_local_availability(calendar, query_start, query_end, zone)
    assert original == snapshot
    assert result['busy_intervals'] == snapshot['busy_intervals']
    assert result['available'] is False and len(calendar.calls) == 1
    facts = result['time_facts']
    assert facts['query_interval'] == interval(*calendar.calls[0], zone)
    busy = facts['busy_intervals'][0]
    assert busy == {'busy_index': 0, **interval(event_start, event_end, zone),
                    'overlaps_query': True, 'query_fully_within_event': False}
    assert busy['in_query_timezone']['start'] == {'datetime': local_start, 'timezone_label': start_label}
    assert busy['in_query_timezone']['end'] == {'datetime': local_end, 'timezone_label': end_label}
    assert busy['in_query_timezone'] != facts['query_interval']['in_query_timezone']


def test_cal03_free_query_has_daylight_offset_but_no_invented_busy_event():
    from harness.calendar_tools import check_local_availability
    class Calendar:
        def check_availability(self, start, end):
            return {'available': True, 'busy_intervals': []}
    result = check_local_availability(Calendar(), '2026-10-06T11:30:00',
                                      '2026-10-06T12:00:00', 'America/Los_Angeles')
    facts = result['time_facts']
    assert facts['query_interval']['in_query_timezone']['start'] == {
        'datetime': '2026-10-06T11:30:00-07:00', 'timezone_label': 'PDT'}
    assert facts['busy_intervals'] == [] and facts['issues'] == []


@pytest.mark.parametrize('entry', [
    {'start': {'date': '2027-01-14'}, 'end': {'date': '2027-01-15'}},
    {'start': {'dateTime': '2027-01-14T11:00:00'}, 'end': {'dateTime': '2027-01-14T11:30:00'}},
    {'start': {'dateTime': 'bad'}, 'end': {'dateTime': 'bad'}},
])
def test_unsupported_event_conversion_preserves_busy_and_raw_evidence(entry):
    from harness.calendar_tools import check_local_availability
    class Calendar:
        def check_availability(self, start, end):
            return {'available': False, 'busy_intervals': [entry]}
    result = check_local_availability(Calendar(), '2027-01-14T11:15:00',
                                      '2027-01-14T11:45:00', 'America/Los_Angeles')
    assert result['available'] is False and result['busy_intervals'] == [entry]
    assert result['time_facts']['busy_intervals'] == [
        {'busy_index': 0, 'issue': 'busy_interval_unavailable_or_all_day'}]


@pytest.mark.parametrize('start,end,overlap,contained', [
    ('10:45', '11:15', True, False),
    ('11:15', '11:45', True, False),
    ('10:45', '11:45', True, False),
    ('11:05', '11:25', True, True),
    ('11:00', '11:30', True, True),
    ('10:30', '11:00', False, False),
    ('11:30', '12:00', False, False),
    ('12:00', '12:30', False, False),
])
def test_model_facts_distinguish_overlap_from_full_containment(start, end, overlap, contained):
    from harness.trace_facts import with_availability_time_facts
    raw = {'available': False, 'busy_intervals': [{
        'start': {'dateTime': '2027-07-14T18:00:00+00:00'},
        'end': {'dateTime': '2027-07-14T18:30:00+00:00'}}]}
    facts = with_availability_time_facts(raw, f'2027-07-14T{start}:00-07:00',
                                       f'2027-07-14T{end}:00-07:00', 'America/Los_Angeles')['time_facts']
    event = facts['busy_intervals'][0]
    assert event['overlaps_query'] is overlap
    assert event['query_fully_within_event'] is contained
    # Annotation cannot rewrite the adapter's availability or clip whole events.
    assert raw['available'] is False
    assert event['utc_start'] == '2027-07-14T18:00:00+00:00'
    assert event['utc_end'] == '2027-07-14T18:30:00+00:00'


def test_containment_is_per_event_not_union_of_busy_intervals():
    from harness.trace_facts import with_availability_time_facts
    raw = {'available': False, 'busy_intervals': [
        {'start': {'dateTime': '2027-07-14T11:00:00-07:00'},
         'end': {'dateTime': '2027-07-14T11:20:00-07:00'}},
        {'start': {'dateTime': '2027-07-14T11:20:00-07:00'},
         'end': {'dateTime': '2027-07-14T11:40:00-07:00'}}]}
    facts = with_availability_time_facts(raw, '2027-07-14T11:10:00-07:00',
                                       '2027-07-14T11:30:00-07:00', 'America/Los_Angeles')['time_facts']
    assert [entry['busy_index'] for entry in facts['busy_intervals']] == [0, 1]
    assert all(entry['overlaps_query'] for entry in facts['busy_intervals'])
    assert not any(entry['query_fully_within_event'] for entry in facts['busy_intervals'])
