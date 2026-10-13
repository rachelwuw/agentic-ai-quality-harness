"""Study execution guards with scripted model output; no live inference."""
import importlib.util
import json
from pathlib import Path


def test_wording_study_is_24_fresh_requests_with_isolated_change(tmp_path, monkeypatch):
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location('wording_study', root / 'evals/run_judge_wording_study.py')
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    monkeypatch.setattr(study, 'runtime', lambda: {'model': 'scripted'})
    monkeypatch.setattr('sys.argv', ['study', '--output-dir', str(tmp_path / 'results')])
    requests = []
    class Client:
        def __init__(self, **kwargs):
            self.model = kwargs['model']
        def request(self, path, payload):
            assert len(payload['messages']) == 2
            data = json.loads(payload['messages'][-1]['content'])
            assert set(data) == {'user_prompt', 'answer', 'checks', 'reference_facts', 'api_calls',
                'tool_events', 'trace_semantics', 'computed_trace_facts', 'computed_facts_usage'}
            assert len(data['checks']) == 9
            assert payload['temperature'] == 0 and payload['max_tokens'] == 6144
            assert payload['reasoning_effort'] == 'high'
            requests.append(data)
            content = json.dumps({'checks': [{'id': c['id'], 'verdict': 'PASS', 'reason': 'Scripted',
                        'evidence': ['Scripted evidence']} for c in data['checks']]})
            return {'choices': [{'finish_reason': 'stop', 'message': {'content': content}}],
                    'usage': {'completion_tokens_details': {'reasoning_tokens': 1024}}}
    monkeypatch.setattr(study, 'LocalClient', Client)
    assert study.main() == 0
    assert len(requests) == 24
    for start in (6, 12, 18):
        assert [x['answer'] for x in requests[start:start+6]] == [x['answer'] for x in requests[:6]]
    for first, changed in zip(requests[:6], requests[6:12]):
        for index, (a, b) in enumerate(zip(first['checks'], changed['checks'])):
            replacement = a['requirement'].replace('No conversion claim satisfies this check.',
                'If the answer makes no event-conversion claim, return PASS for this check.') if index in (5, 6) else a['requirement']
            assert b['requirement'] == replacement
    assert requests[:6] == requests[18:24]
    assert requests[6:12] == requests[12:18]
    assert json.loads((tmp_path / 'results/execution_complete.json').read_text())['requests'] == 24


def test_comparison_preserves_unavailable_judgments_and_detects_regressions():
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location('wording_compare', root / 'evals/compare_judge_wording_study.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    labels = {letter: {'overall': 'PASS', 'criteria': {f'c{i}': 'PASS' for i in range(1, 10)}} for letter in 'ABCDEF'}
    reports = {}
    for arm in ('original', 'clarified'):
        for round_number in (1, 2):
            items = []
            for letter in labels:
                checks = [{'id': cid, 'verdict': 'PASS', 'reason': 'Scripted', 'evidence': ['Scripted']}
                          for cid in labels[letter]['criteria']]
                items.append({'id': letter, 'status': 'reviewed', 'verdict': 'PASS', 'checks': checks,
                              'generation': {'elapsed_seconds': 1}})
            reports[(arm, round_number)] = {'state': 'completed', 'results': items}
    first = reports[('original', 1)]['results']
    first[0]['checks'][5]['verdict'] = 'FAIL'
    first[0]['verdict'] = 'FAIL'
    first[2].update(status='judge_error', error_category='transport_error', verdict='UNCERTAIN', checks=[])
    first[3]['checks'][1]['verdict'] = 'UNCERTAIN'
    first[3]['verdict'] = 'UNCERTAIN'
    regressed = reports[('clarified', 2)]['results'][1]
    regressed['checks'][6]['verdict'] = 'FAIL'
    regressed['verdict'] = 'FAIL'
    result = module.compare(reports, labels)
    original = result['summary']['original']
    assert original['planned_criteria'] == 108 and original['available_criteria'] == 99
    assert original['criterion_matches'] == 97
    assert original['valid_outputs'] == 11 and original['operational_errors'] == 1
    assert original['semantic_uncertain'] == 1
    assert original['criterion_repeat_available'] == 45 and original['criterion_repeat_consistent'] == 43
    assert result['cross_arm_improvements'] == 2
    assert result['cross_arm_regressions'] == 1
    assert result['cross_arm_unavailable'] == 9
