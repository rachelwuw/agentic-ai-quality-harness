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
