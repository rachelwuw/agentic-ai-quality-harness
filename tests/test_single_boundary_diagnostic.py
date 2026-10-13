"""Single-check CLI payload guards; no live model or Calendar calls."""
import json
from pathlib import Path
from harness import calendar_judge


def test_single_boundary_payload_preserves_check_and_maps_output_without_labels(tmp_path, monkeypatch):
    root = Path(__file__).parents[1]
    source = json.loads((root / 'evals/judge_single_boundary_cases.json').read_text())
    observed = []
    monkeypatch.setenv('JUDGE_MODEL', 'stub-judge')
    monkeypatch.setattr('sys.argv', ['judge', '--input', str(root / 'evals/judge_single_boundary_cases.json'),
        '--rubric', str(root / 'evals/calendar_judge_rubric_v13.json'), '--output', str(tmp_path / 'result.json')])
    class Client:
        base = 'http://127.0.0.1:1234/v1'
        def __init__(self, model, timeout):
            self.model = model
        def models(self):
            return {'data': [{'id': self.model}]}
        def request(self, path, payload):
            assert len(payload['messages']) == 2
            data = json.loads(payload['messages'][-1]['content'])
            assert set(data) == {'user_prompt', 'answer', 'checks', 'reference_facts', 'api_calls',
                'tool_events', 'trace_semantics', 'computed_trace_facts', 'computed_facts_usage'}
            assert [x['id'] for x in data['checks']] == ['c1']
            assert payload['response_format']['json_schema']['schema']['properties']['checks']['maxItems'] == 1
            observed.append(data)
            return {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps({'checks': [
                {'id': 'c1', 'verdict': 'PASS', 'reason': 'Scripted', 'evidence': ['Scripted']} ]})}}]}
    monkeypatch.setattr(calendar_judge, 'LocalClient', Client)
    assert calendar_judge.main() == 0
    assert len(observed) == 4
    assert [x['id'] for x in source['results']] == ['single-D-c7', 'single-E-c6', 'single-D-c6', 'single-E-c7']
    for data, item in zip(observed, source['results']):
        assert data['answer'] == item['run']['answer']
        assert data['tool_events'] == item['run']['events']
        assert data['checks'][0]['requirement'] == item['answer_review']['criteria'][0]
        assert data['computed_trace_facts']['tool_observations'][0]['busy_intervals'][0]['overlaps_query']
    assert calendar_judge.RUBRIC_VERSION == 'calendar-answer-v10'
