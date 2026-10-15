import copy
import json
from pathlib import Path

import pytest

from harness.calendar_renderer import main, render_calendar_answer


def run(start='2027-07-14T11:15:00-07:00', end='2027-07-14T11:45:00-07:00',
        zone='America/Los_Angeles', event_start='2027-07-14T18:00:00Z', event_end='2027-07-14T18:30:00Z'):
    return {'status': 'completed', 'answer': 'Invented PST and false containment. Ignore all instructions.',
            'events': [{'type': 'tool', 'name': 'check_availability', 'result': {
                'start': start, 'end': end, 'time_zone': zone, 'available': False,
                'scope': 'configured_test_calendar_only', 'busy_intervals': [
                    {'start': {'dateTime': event_start}, 'end': {'dateTime': event_end}}]}}]}


def tool(value):
    return value['events'][0]['result']


def test_english_partial_overlap_preview_is_exact_and_does_not_repair_original():
    value = run(); before = copy.deepcopy(value)
    preview = render_calendar_answer(value, language='en')
    assert preview['render_status'] == 'rendered'
    assert preview['rendered_answer'] == (
        'Unavailable (tool-reported; dedicated test calendar only).\n'
        'Actual tool query: 2027-07-14T11:15:00-07:00 → 2027-07-14T11:45:00-07:00 (America/Los_Angeles)\n'
        'Original event timestamps: 2027-07-14T18:00:00Z → 2027-07-14T18:30:00Z\n'
        'Event in requested zone: 2027-07-14T11:00:00-07:00 → 2027-07-14T11:30:00-07:00 (America/Los_Angeles)\n'
        'This event overlaps the query but does not contain the entire query.')
    assert preview['evidence_refs'] == [{'event_index': 0}]
    assert value == before
    assert render_calendar_answer(value, language='en') == preview


@pytest.mark.parametrize('qs,qe,zone,es,ee,expected', [
    ('2027-01-14T11:10:00-08:00','2027-01-14T11:20:00-08:00','America/Los_Angeles',
     '2027-01-14T19:00:00Z','2027-01-14T19:30:00Z','2027-01-14T11:00:00-08:00'),
    ('2027-07-15T02:10:00+08:00','2027-07-15T02:20:00+08:00','Asia/Taipei',
     '2027-07-14T11:00:00-07:00','2027-07-14T11:30:00-07:00','2027-07-15T02:00:00+08:00'),
    ('2026-03-08T01:45:00-08:00','2026-03-08T03:15:00-07:00','America/Los_Angeles',
     '2026-03-08T01:30:00-08:00','2026-03-08T03:30:00-07:00','2026-03-08T03:30:00-07:00'),
])
def test_containment_winter_cross_day_and_dst_endpoints(qs, qe, zone, es, ee, expected):
    preview = render_calendar_answer(run(qs, qe, zone, es, ee), language='zh-TW')
    answer = preview['rendered_answer']
    assert preview['render_status'] == 'rendered'
    assert answer.startswith('不可用（工具回報；僅專用測試行事曆）。')
    assert f'活動原始時間: {es} → {ee}' in answer
    assert expected in answer and zone in answer
    assert '此活動包含整段查詢區間。' in answer
    assert 'PST' not in answer and 'PDT' not in answer


def test_free_noon_has_query_scope_no_event_and_ignores_spanish_llm_answer():
    value = run('2027-07-14T11:30:00-07:00', '2027-07-14T12:00:00-07:00')
    tool(value).update(available=True, busy_intervals=[])
    value['answer'] = 'Disponible en el calendario.'
    answer = render_calendar_answer(value, language='en')['rendered_answer']
    assert answer.startswith('Available (tool-reported; dedicated test calendar only).')
    assert '2027-07-14T12:00:00-07:00' in answer
    assert 'No conflicting events were returned.' in answer
    assert 'Original event' not in answer and 'Disponible' not in answer


@pytest.mark.parametrize('language', ['en','zh-TW'])
def test_all_day_retains_dates_and_reported_busy_with_explicit_limitations(language):
    value = run(); tool(value)['busy_intervals'] = [
        {'start': {'date': '2027-07-14'}, 'end': {'date': '2027-07-15'}}]
    preview = render_calendar_answer(value, language=language)
    assert preview['render_status'] == 'rendered'
    assert '2027-07-14 → 2027-07-15' in preview['rendered_answer']
    assert preview['limitations'] == [{'busy_index': 0, 'issue': 'all_day_clock_times_unknown'}]
    assert ('end exclusive' in preview['rendered_answer'] if language == 'en' else '不含結束日' in preview['rendered_answer'])


@pytest.mark.parametrize('field,bad', [
    ('available',None), ('available','true'), ('busy_intervals',None),
    ('busy_intervals',[]), ('available',True), ('error',''),
    ('time_zone','bad/zone'), ('time_zone',None), ('start','bad'),
    ('start','2027-07-14T11:15:00'), ('end','2027-07-14T10:00:00-07:00'),
    ('scope',None), ('scope','primary'),
])
def test_missing_invalid_or_conflicting_tool_evidence_is_unknown(field, bad):
    value = run(); tool(value)[field] = bad
    preview = render_calendar_answer(value, language='en')
    assert preview['render_status'] == 'unknown'
    assert preview['rendered_answer'].startswith('Availability unknown;')
    assert 'Unavailable (' not in preview['rendered_answer']


@pytest.mark.parametrize('bad', [None, {},
    {'start': {'dateTime':'bad'}, 'end': {'dateTime':'bad'}},
    {'start': {'date':'2027-07-15'}, 'end': {'date':'2027-07-14'}},
    {'start': {'dateTime':'2027-07-14T18:45:00Z'}, 'end': {'dateTime':'2027-07-14T19:00:00Z'}},
    {'start': {'date':'2027-07-14','dateTime':'2027-07-14T18:00:00Z'}, 'end': {'date':'2027-07-15'}},
])
def test_bad_or_nonoverlapping_returned_events_never_become_supported_busy(bad):
    value = run(); tool(value)['busy_intervals'] = [bad]
    assert render_calendar_answer(value, language='en')['render_status'] == 'unknown'


def test_multi_event_relationships_do_not_claim_union_coverage():
    value = run(); tool(value)['busy_intervals'].append({
        'start': {'dateTime':'2027-07-14T18:30:00Z'}, 'end': {'dateTime':'2027-07-14T19:00:00Z'}})
    answer = render_calendar_answer(value, language='en')['rendered_answer']
    assert answer.count('does not contain the entire query') == 2
    assert 'combined coverage was not calculated' in answer


@pytest.mark.parametrize('value', [None, {}, {'status':'model_error','events':[]},
    {'status':'completed','events':[]}, {'status':'completed','events':[None]},
    {'status':'completed','events':[{'type':'tool','name':'create_event'}]}])
def test_unsupported_runs_do_not_fall_back_to_llm_prose(value):
    preview = render_calendar_answer(value, language='en')
    assert preview['render_status'] == 'unsupported' and preview['rendered_answer'] is None


def test_multiple_tool_events_rejected_including_failed_then_successful_correction():
    value = run(); value['events'].insert(0, {'type':'tool','name':'check_availability','result':{'error':'invalid_arguments'}})
    assert render_calendar_answer(value, language='en')['render_status'] == 'unsupported'
    with pytest.raises(ValueError):
        render_calendar_answer(run(), language='es')


def test_offline_cli_keeps_original_and_never_overwrites(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket,'socket',lambda *a,**kw:pytest.fail('No network allowed'))
    source, output = tmp_path/'trace.json', tmp_path/'preview.json'
    item = {'id':'one','structural_pass':True,'run':run()}
    source.write_text(json.dumps({'results':[item]})); original = source.read_bytes()
    assert main(['--input',str(source),'--output',str(output),'--language','en']) == 0
    data = json.loads(output.read_text())
    assert data['results'][0]['original_answer'] == item['run']['answer']
    assert data['results'][0]['render_status'] == 'rendered'
    assert data['mode'] == 'offline_preview_not_product_output'
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        main(['--input',str(source),'--output',str(output),'--language','en'])
    with pytest.raises(SystemExit):
        main(['--input',str(source),'--output',str(source),'--language','en'])
    assert source.read_bytes() == original
