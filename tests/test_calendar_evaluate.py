import json
from pathlib import Path
from harness.calendar_evaluate import ControlledCalendar, evaluate, grade_structure

SUITE = json.loads((Path(__file__).parents[1] / 'evals/calendar_cases.json').read_text())


def test_boundary_and_timezone_fixture():
    c = ControlledCalendar('busy_fixture', SUITE['fixtures']['busy_fixture'])
    assert not c.check_availability('2026-10-07T02:15:00+08:00', '2026-10-07T02:45:00+08:00')['available']
    assert c.check_availability('2026-10-06T11:30:00-07:00', '2026-10-06T12:00:00-07:00')['available']


def test_wrong_interval_fails_even_when_answer_sounds_correct():
    case = SUITE['cases'][2]
    c = ControlledCalendar(case['fixture'], SUITE['fixtures']['busy_fixture'])
    c.calls = [{'start': '2026-10-06T12:30:00-07:00', 'end': '2026-10-06T13:00:00-07:00'}]
    run = {'status': 'completed', 'answer': 'Free', 'events': [{'type': 'tool', 'name': 'check_availability',
        'arguments': json.dumps(case['expected_calls'][0]['arguments']), 'result': {'available': True}}]}
    grade = grade_structure(case, run, c)
    assert not grade['structural_pass']
    assert grade['answer_review']['status'] == 'pending'


def test_controlled_suite_runs_without_google_and_keeps_review_pending():
    responses = []
    for case in SUITE['cases']:
        if case['expected_calls']:
            call = case['expected_calls'][0]
            responses.append({'role': 'assistant', 'tool_calls': [{'id': case['id'], 'type': 'function',
                'function': {'name': call['name'], 'arguments': json.dumps(call['arguments'])}}]})
        responses.append({'role': 'assistant', 'content': 'Requires manual semantic review.'})
    scripted = iter(responses)
    report = evaluate(SUITE, lambda *_: next(scripted))
    assert report['total'] == 15
    assert report['structural_passes'] == 15
    assert all(x['overall_status'] == 'pending_review' for x in report['results'])


def test_missing_information_tool_call_fails():
    case = SUITE['cases'][9]
    c = ControlledCalendar('none', SUITE['fixtures']['busy_fixture'])
    run = {'status': 'completed', 'answer': 'Free', 'events': [{'type': 'tool', 'name': 'check_availability',
        'arguments': '{}', 'result': {'available': True}}]}
    assert not grade_structure(case, run, c)['structural_pass']
