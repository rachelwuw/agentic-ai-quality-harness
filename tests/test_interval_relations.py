import copy
import hashlib
import json
from pathlib import Path

import pytest

from harness.interval_relations import derive_interval_relations, main
from harness.trace_facts import derive_trace_facts
from harness.calendar_judge import review


def saved(query_start='11:15', query_end='11:45'):
    return {'id': 'interval-case', 'structural_pass': True, 'api_calls': [],
            'run': {'events': [{'type': 'tool', 'name': 'check_availability', 'result': {
                'start': f'2027-07-14T{query_start}:00-07:00',
                'end': f'2027-07-14T{query_end}:00-07:00',
                'time_zone': 'America/Los_Angeles', 'available': False,
                'busy_intervals': [{'start': {'dateTime': '2027-07-14T18:00:00Z'},
                                    'end': {'dateTime': '2027-07-14T18:30:00Z'}}]}}]}}


def result(item):
    return item['run']['events'][0]['result']


def relation(item):
    return derive_interval_relations(item)['tool_observations'][0]['busy_intervals'][0]


@pytest.mark.parametrize('start,end,overlap,contained', [
    ('10:45', '11:15', True, False), ('11:15', '11:45', True, False),
    ('10:45', '11:45', True, False), ('11:05', '11:25', True, True),
    ('11:00', '11:30', True, True), ('11:00', '11:25', True, True),
    ('11:05', '11:30', True, True), ('10:30', '11:00', False, False),
    ('11:30', '12:00', False, False), ('12:00', '12:30', False, False),
])
def test_saved_trace_half_open_boundaries_and_different_offsets(start, end, overlap, contained):
    item = saved(start, end)
    before = copy.deepcopy(item)
    assert relation(item) == {'busy_index': 0, 'overlaps_query': overlap,
                              'query_fully_within_event': contained}
    assert item == before
    # The new consumer agrees with existing overlap evidence without changing it.
    assert derive_trace_facts(item)['tool_observations'][0]['busy_intervals'][0]['overlaps_query'] is overlap


@pytest.mark.parametrize('bad', [None, {}, {'start': {'date': '2027-07-14'}, 'end': {'date': '2027-07-15'}},
    {'start': {'dateTime': '2027-07-14T11:00:00'}, 'end': {'dateTime': '2027-07-14T11:30:00'}},
    {'start': {'dateTime': 'bad'}, 'end': {'dateTime': 'bad'}},
    {'start': {'dateTime': '2027-07-14T19:00:00Z'}, 'end': {'dateTime': '2027-07-14T18:00:00Z'}},
    {'start': {'dateTime': '2027-07-14T18:00:00Z'}, 'end': {'dateTime': '2027-07-14T18:00:00Z'}}])
def test_unsupported_event_is_unknown_not_nonoverlap(bad):
    item = saved(); result(item)['busy_intervals'] = [bad]
    assert relation(item) == {'busy_index': 0, 'overlaps_query': None,
        'query_fully_within_event': None, 'issue': 'interval_relationship_unavailable'}


@pytest.mark.parametrize('field,value', [('start', 'bad'), ('start', None),
    ('start', '2027-07-14T11:15:00'), ('end', '2027-07-14T10:00:00-07:00'),
    ('error', 'calendar_unavailable'), ('error', '')])
def test_invalid_query_or_tool_failure_is_unknown(field, value):
    item = saved(); result(item)[field] = value
    assert relation(item)['overlaps_query'] is None
    assert relation(item)['query_fully_within_event'] is None


def test_missing_and_empty_busy_arrays_are_distinct_and_do_not_infer_free():
    item = saved(); result(item).pop('busy_intervals'); result(item).pop('available')
    missing = derive_interval_relations(item)['tool_observations'][0]
    assert missing['busy_intervals'] is None and missing['reported_available'] is None
    result(item)['busy_intervals'] = []
    empty = derive_interval_relations(item)['tool_observations'][0]
    assert empty['busy_intervals'] == [] and empty['reported_available'] is None


def test_multiple_events_are_not_union_coverage():
    item = saved('11:10', '11:30')
    result(item)['busy_intervals'] = [
        {'start': {'dateTime': '2027-07-14T18:00:00Z'}, 'end': {'dateTime': '2027-07-14T18:20:00Z'}},
        {'start': {'dateTime': '2027-07-14T18:20:00Z'}, 'end': {'dateTime': '2027-07-14T18:40:00Z'}}]
    events = derive_interval_relations(item)['tool_observations'][0]['busy_intervals']
    assert events == [{'busy_index': n, 'overlaps_query': True, 'query_fully_within_event': False} for n in range(2)]


@pytest.mark.parametrize('busy', [None, {}, 'not an array'])
def test_malformed_busy_array_retains_unknown_and_diagnostic(busy):
    item = saved(); result(item)['busy_intervals'] = busy
    observation = derive_interval_relations(item)['tool_observations'][0]
    assert observation['busy_intervals'] is None
    assert 'busy_intervals_missing_or_malformed' in observation['issues']


def test_missing_events_retains_unknown_evidence_diagnostic():
    facts = derive_interval_relations({'run': {}})
    assert facts['tool_observations'] == []
    assert 'tool_event_trace_missing_or_malformed' in facts['issues']


def test_judge_messages_unchanged_after_offline_analysis():
    item = json.loads((Path(__file__).parents[1] / 'evals/judge_v9_new_wording_cases.json').read_text())['results'][0]
    before = copy.deepcopy(item)
    derive_interval_relations(item)
    seen = []
    def fake_complete(messages):
        seen.append(messages)
        return 'invalid json'
    review(item, [], fake_complete, derive_facts=True)
    # Frozen on main f073b0c before implementation: checks the entire model payload,
    # not just that the new fields are absent. No actual model is invoked.
    assert hashlib.sha256(json.dumps(seen, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '783493a4da555bda1c45623b932649646159fb35eac8a562f219da25cf66e58c'
    assert item == before


def test_offline_cli_writes_new_sidecar_and_never_overwrites_source(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket, 'socket', lambda *a, **kw: pytest.fail('Offline CLI must not access network'))
    source, output = tmp_path/'saved.json', tmp_path/'relations.json'
    source.write_text(json.dumps({'results': [saved()]}))
    original = source.read_bytes()
    assert main(['--input', str(source), '--output', str(output)]) == 0
    data = json.loads(output.read_text())
    assert data['results'][0]['tool_observations'][0]['busy_intervals'][0]['query_fully_within_event'] is False
    assert data['source_sha256'] == hashlib.sha256(original).hexdigest()
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        main(['--input', str(source), '--output', str(output)])
    with pytest.raises(SystemExit):
        main(['--input', str(source), '--output', str(source)])
    assert source.read_bytes() == original
