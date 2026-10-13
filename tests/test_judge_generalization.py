"""Offline checks for the approved experiment; never contacts a live model."""
import copy
import json
from pathlib import Path
import pytest
from harness.calendar_judge import local_complete, RUBRIC_VERSION
from harness.judge_generalization import schedule, run_request, compare, CASE_IDS


def inputs():
    return tuple(json.loads(Path(p).read_text()) for p in (
        'evals/judge_generalization_cases.json', 'evals/judge_generalization_labels.json',
        'evals/calendar_judge_generalization_rubric.json'))


def test_exact_schedule_and_payloads_without_labels():
    source, labels, rubric = inputs()
    calls = []
    class FakeClient:
        model = 'fake-offline'
        def request(self, path, payload):
            data = json.loads(payload['messages'][1]['content'])
            calls.append((payload, data))
            checks = [{'id': c['id'], 'verdict': 'PASS', 'reason': 'Offline transport fixture',
                       'evidence': ['Fixture']} for c in data['checks']]
            return {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps({'checks': checks})}}]}
    complete = local_complete(FakeClient(), thinking=True, max_tokens=6144)
    jobs = schedule(source)
    assert len(jobs) == 24
    assert [mode for _, mode in jobs] == list(('batch', 'c6', 'c7', 'c6', 'c7', 'batch', 'c7', 'batch', 'c6') * 2 + ('batch', 'c6', 'c7', 'c6', 'c7', 'batch'))
    for item, mode in jobs:
        result = run_request(item, mode, complete, rubric)
        assert result['status'] == 'reviewed'
        payload, data = calls[-1]
        assert data['answer'] == item['run']['answer']
        assert data['tool_events'] == item['run']['events']
        assert data['api_calls'] == item['api_calls']
        assert data['reference_facts'] == []
        assert not {'labels', 'expected', 'human_signoff', 'approval'} & data.keys()
        checks = data['checks']
        expected = item['answer_review']['criteria'] if mode == 'batch' else [item['answer_review']['criteria'][int(mode[1:])-1]]
        assert [c['requirement'] for c in checks] == expected
        assert [c['id'] for c in checks] == [f'c{i+1}' for i in range(len(expected))]
        assert payload['max_tokens'] == 6144 and payload['temperature'] == 0
        assert payload['response_format']['json_schema']['schema']['properties']['checks']['minItems'] == len(expected)
    for i in range(0, 24, 3):
        assert calls[i][1]['computed_trace_facts'] == calls[i+1][1]['computed_trace_facts'] == calls[i+2][1]['computed_trace_facts']
    assert RUBRIC_VERSION == 'calendar-answer-v10'


def report_fixture():
    source, labels, _ = inputs()
    results = []
    for item, mode in schedule(source):
        ids = ('c6', 'c7') if mode == 'batch' else (mode,)
        results.append({'id': item['id'], 'mode': mode, 'status': 'reviewed', 'generation': {},
                        'checks': [{'id': c if mode == 'batch' else 'c1',
                                    'verdict': labels['labels'][item['id']]['criteria'][c],
                                    'reason': 'Fixture', 'evidence': ['Fixture']} for c in ids]})
    return {'state': 'completed', 'results': results}, labels


def test_missing_and_error_outputs_do_not_inflate_denominators():
    report, labels = report_fixture()
    report['results'].pop()  # Missing final N4 batch remains in planned denominator.
    report['results'][0]['status'] = 'judge_error'
    result = compare(report, labels)
    assert not result['gates']['complete_24_valid']
    assert result['counts']['batch']['planned_targets'] == result['counts']['single']['planned_targets'] == 16
    assert result['counts']['batch']['available_targets'] < 16
    assert result['paired_targets'] < 16


def test_pair_improvements_regressions_and_uncertain():
    report, labels = report_fixture()
    report['results'][0]['checks'][0]['verdict'] = 'FAIL'  # P1 batch false fail, single correct.
    report['results'][2]['checks'][0]['verdict'] = 'UNCERTAIN'  # P1 c7 single regression.
    result = compare(report, labels)
    assert result['improvements'] == ['generalization-P1/c6']
    assert result['regressions'] == ['generalization-P1/c7']
    assert result['counts']['single']['uncertain'] == 1
    assert not result['gates']['at_least_two_improvements_zero_regressions']
    assert not result['gates']['positive_8_and_expected_fail_5']
    report['results'].append(copy.deepcopy(report['results'][0]))
    with pytest.raises(ValueError, match='Duplicate'):
        compare(report, labels)


def test_reject_changed_order_or_forbidden_extra_checks():
    source, _, _ = inputs()
    source['results'].reverse()
    with pytest.raises(ValueError, match='fixed order'):
        schedule(source)
    source['results'].reverse()
    source['results'][0]['answer_review']['forbidden_behaviors'] = ['Extra unapproved check']
    with pytest.raises(ValueError, match='unexpected checks'):
        schedule(source)


def test_perfect_both_formats_is_not_evidence_of_two_improvements():
    report, labels = report_fixture()
    result = compare(report, labels)
    assert result['gates']['complete_24_valid']
    assert result['gates']['positive_8_and_expected_fail_5']
    assert result['counts']['batch']['matches'] == result['counts']['single']['matches'] == 16
    assert result['improvements'] == result['regressions'] == []
    assert not result['gates']['at_least_two_improvements_zero_regressions']
    assert result['gates']['reason_evidence_review'] == 'pending_manual_review'
    assert result['gates']['cost_acceptance'] == 'pending_Rachel_review'
