"""Real local model evaluation with controlled Calendar data; no Google access."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from .calendar_agent import run_calendar_agent
from .calendar_tools import CalendarError
from .client import LocalClient


class ControlledCalendar:
    def __init__(self, fixture, busy):
        self.fixture, self.busy, self.calls = fixture, busy, []

    def check_availability(self, start, end):
        self.calls.append({'start': start, 'end': end})
        if self.fixture == 'raise_calendar_error':
            raise CalendarError('Controlled read failure')
        overlaps = (self.fixture == 'busy_fixture' and
                    datetime.fromisoformat(start) < datetime.fromisoformat(self.busy['end']) and
                    datetime.fromisoformat(end) > datetime.fromisoformat(self.busy['start']))
        intervals = [{'start': {'dateTime': self.busy['start']},
                      'end': {'dateTime': self.busy['end']}}] if overlaps else []
        return {'start': start, 'end': end, 'available': not overlaps,
                'busy_intervals': intervals, 'source': 'controlled_calendar_fixture',
                'scope': 'configured_test_calendar_only'}


def grade_structure(case, run, calendar):
    events = [e for e in run['events'] if e['type'] == 'tool']
    actual = []
    for event in events:
        try:
            args = json.loads(event['arguments'])
        except (ValueError, TypeError):
            args = None
        actual.append({'name': event['name'], 'arguments': args})
    expected = case['expected_calls']
    clarification = 'allowed_alternative' in case and not actual
    expected_api = case['expected_api_interval']
    checks = {
        'completed': run['status'] == 'completed',
        'tool_arguments': actual == expected or clarification,
        'api_interval': calendar.calls == ([] if expected_api is None else [expected_api]),
        'tool_outcome': (not events if not expected or clarification else
                         len(events) == 1 and events[0]['result'].get('available') is case['expected_available']),
    }
    return {'structural_pass': all(checks.values()), 'checks': checks,
            'answer_review': {'status': 'pending', 'criteria': case['answer_criteria'],
                              'forbidden_behaviors': case['forbidden_behaviors'], 'notes': ''},
            'overall_status': 'pending_review' if all(checks.values()) else 'failed_structure'}


def evaluate(suite, complete, selected=None, on_case=None):
    results = []
    for case in suite['cases']:
        if selected and case['id'] not in selected:
            continue
        calendar = ControlledCalendar(case['fixture'], suite['fixtures']['busy_fixture'])
        try:
            run = run_calendar_agent(case['prompt'], complete, calendar,
                                     now=datetime.fromisoformat(suite['reference_now']))
            item = {'id': case['id'], 'prompt': case['prompt'],
                    **grade_structure(case, run, calendar), 'api_calls': calendar.calls, 'run': run}
        except Exception as error:
            item = {'id': case['id'], 'structural_pass': False, 'overall_status': 'execution_error',
                    'error_type': type(error).__name__, 'api_calls': calendar.calls}
        results.append(item)
        if on_case:
            on_case(item)
    return {'entry_point': 'python_agent', 'calendar_mode': 'controlled_no_google_access',
            'reference_now': suite['reference_now'], 'total': len(results),
            'structural_passes': sum(x['structural_pass'] for x in results),
            'semantic_review_required': True, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', default='evals/calendar_cases.json')
    parser.add_argument('--ids', nargs='+', help='Optional case IDs for a small run')
    parser.add_argument('--output', default='reports/calendar-evaluation.json')
    args = parser.parse_args()
    suite = json.loads(Path(args.cases).read_text())
    if args.ids and set(args.ids) - {c['id'] for c in suite['cases']}:
        parser.error('Unknown case ID')
    client = LocalClient()
    client.models()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    def save_progress(item):
        progress.append(item)
        output.write_text(json.dumps({'state': 'running', 'model': client.model,
            'base_url': client.base, 'results': progress}, ensure_ascii=False, indent=2))
        print(item['id'] + ': ' + item['overall_status'], flush=True)
    progress = []
    print('Real local model; controlled Calendar responses; NO Google API access.', flush=True)
    report = evaluate(suite, client, set(args.ids or []), save_progress)
    report.update(model=client.model, base_url=client.base,
                  recorded_at=datetime.now().astimezone().isoformat())
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Structural passes: {report['structural_passes']}/{report['total']}; answers require human review.")
    print('Saved: ' + str(output))
    return int(report['structural_passes'] != report['total'])


if __name__ == '__main__':
    raise SystemExit(main())
