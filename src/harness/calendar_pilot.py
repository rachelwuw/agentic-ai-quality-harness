"""Explicit controlled renderer pilot; fake Calendar only, no Google connection."""
import argparse
import copy
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

from .calendar_agent import run_calendar_agent
from .calendar_evaluate import ControlledCalendar
from .calendar_live_regression import MODEL, private_directory, write_private
from .calendar_tools import resolve_local_interval
from .client import LocalClient
from .trace_facts import interval

IDS = tuple(f'v1p-{n:02}' for n in range(1, 7))
MAX_ATTEMPTS = 18
MAX_SECONDS = 600


class StopPilot(BaseException):
    """Control-flow stop must bypass model retries and the agent's error handler."""
    def __init__(self, state):
        self.state = state


class Limits:
    def __init__(self, attempts=MAX_ATTEMPTS, seconds=MAX_SECONDS, clock=time.monotonic):
        if type(attempts) is not int or not 1 <= attempts <= MAX_ATTEMPTS:
            raise ValueError('Invalid physical inference attempt cap')
        if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or not 0 < seconds <= MAX_SECONDS:
            raise ValueError('Invalid orchestration deadline')
        self.cap, self.seconds, self.clock = attempts, seconds, clock
        self.used, self.started = 0, clock()

    def check(self):
        if self.clock() - self.started >= self.seconds:
            raise StopPilot('deadline_exhausted')

    def take(self):
        self.check()
        if self.used >= self.cap:
            raise StopPilot('budget_exhausted')
        self.used += 1


class PilotClient(LocalClient):
    """Count each physical inference send, including LocalClient transport retries."""
    def __init__(self, limits, **kwargs):
        super().__init__(**kwargs)
        self.limits, self.requests, self.case_id = limits, [], None

    def request(self, path, payload=None):
        if path != '/chat/completions':
            raise ValueError('Pilot inference client only permits chat completions')
        self.limits.take()
        record = {'case_id': self.case_id, 'payload': copy.deepcopy(payload), 'state': 'started'}
        self.requests.append(record)
        try:
            response = super().request(path, payload)
            record.update(state='returned', response=copy.deepcopy(response))
            return response
        except BaseException as error:
            record.update(state='error', error_type=type(error).__name__)
            raise


def validate_suite(suite):
    """Validate references before model construction/output creation; no grading labels rewritten."""
    if suite.get('schema') != 'calendar-controlled-renderer-pilot-v1':
        raise ValueError('Unsupported pilot schema')
    now = datetime.fromisoformat(suite['reference_now'])
    if now.utcoffset() is None:
        raise ValueError('Frozen reference time requires an offset')
    cases = suite['cases']
    if tuple(c['id'] for c in cases) != IDS:
        raise ValueError('Expected six reviewed pilot ids in order')
    for case in cases:
        if case['language'] not in ('en', 'zh-TW') or not isinstance(case['prompt'], str) or not case['prompt'].strip():
            raise ValueError('Invalid prompt/language')
        calls, api, expected = case['expected_calls'], case['expected_api_interval'], case['expected']
        mode = case['fixture']['mode']
        if mode not in ('busy_fixture', 'none', 'raise_calendar_error'):
            raise ValueError('Unsupported controlled fixture')
        if not isinstance(expected['lines'], list) or not all(isinstance(s, str) for s in expected['lines']):
            raise ValueError('Expected literal reference lines')
        if not calls:
            if api is not None or mode != 'none' or expected != {'status': 'unsupported', 'lines': [], 'available': None, 'event_local': None}:
                raise ValueError('Invalid no-tool reference')
            continue
        if len(calls) != 1 or calls[0]['name'] != 'check_availability':
            raise ValueError('Expected one availability call')
        start, end = resolve_local_interval(**calls[0]['arguments'])
        if api != {'start': start, 'end': end}:
            raise ValueError('API interval differs from independent reference')
        if mode == 'raise_calendar_error':
            if expected['status'] != 'unknown' or expected['available'] is not None or expected['event_local'] is not None:
                raise ValueError('Invalid error reference')
        elif mode == 'busy_fixture':
            busy = case['fixture']['busy']
            fact = interval(busy['start'], busy['end'], calls[0]['arguments']['time_zone'])
            q = interval(start, end)
            overlaps = fact['utc_start'] < q['utc_end'] and fact['utc_end'] > q['utc_start']
            local = fact['in_query_timezone']
            endpoints = [local['start']['datetime'], local['end']['datetime']] if overlaps else None
            if expected['status'] != 'rendered' or expected['available'] is not (not overlaps) or expected['event_local'] != endpoints:
                raise ValueError('Fixture differs from reference facts')
        else:
            raise ValueError('No-fixture mode cannot permit a tool call')
        if not expected['lines']:
            raise ValueError('Expected product reference is missing')
    return cases


class GuardedCalendar(ControlledCalendar):
    def __init__(self, case):
        fixture = case['fixture']
        super().__init__(fixture['mode'], fixture.get('busy'))
        self.expected, self.attempted = case['expected_api_interval'], []

    def check_availability(self, start, end):
        args = {'start': start, 'end': end}
        self.attempted.append(args)
        if self.calls or args != self.expected:
            raise StopPilot('unexpected_tool')
        return super().check_availability(start, end)


def grade(case, run, calendar):
    tools = [e for e in run['events'] if e['type'] == 'tool']
    actual = [{'name': e['name'], 'arguments': json.loads(e['arguments'])} for e in tools]
    expected, product = case['expected'], run['product_output']
    checks = {'completed': run['status'] == 'completed',
              'tool_arguments': actual == case['expected_calls'],
              'api_interval': calendar.calls == ([] if case['expected_api_interval'] is None else [case['expected_api_interval']])}
    result = tools[0]['result'] if tools else None
    if not tools:
        facts_ok = not case['expected_calls']
    elif case['fixture']['mode'] == 'raise_calendar_error':
        facts_ok = result.get('error') == 'calendar_unavailable' and result.get('available') is None
    else:
        zone = case['expected_calls'][0]['arguments']['time_zone']
        query = result.get('time_facts', {}).get('query_interval', {}).get('in_query_timezone', {})
        api = case['expected_api_interval']
        facts_ok = (result.get('available') is expected['available'] and query.get('time_zone') == zone and
                    [query.get(k, {}).get('datetime') for k in ('start', 'end')] == [api['start'], api['end']])
        busy = result.get('time_facts', {}).get('busy_intervals', [])
        converted = [[f.get('in_query_timezone', {}).get(k, {}).get('datetime') for k in ('start', 'end')] for f in busy]
        facts_ok = facts_ok and converted == ([] if expected['event_local'] is None else [expected['event_local']])
    reference = '\n'.join(expected['lines']) if expected['status'] != 'unsupported' else None
    product_ok = (product['language'] == case['language'] and product['render_status'] == expected['status'] and
                  product['rendered_answer'] == reference)
    return {'structural_checks': checks, 'python_facts_match': facts_ok,
            'product_reference_match': product_ok, 'expected_agent_exit': int(expected['status'] != 'rendered'),
            'automated_pass': all(checks.values()) and facts_ok and product_ok,
            'raw_answer_review': 'pending', 'human_product_review': 'pending', 'semantic_pass_claim': False}


def run_suite(suite, client, *, progress=None, runtime_check=None):
    cases = validate_suite(suite)
    report = {'schema': suite['schema'], 'state': 'running', 'case_definitions': copy.deepcopy(suite),
              'google_requests': 0, 'judge_requests': 0, 'semantic_pass_claim': False,
              'results': [{'id': c['id'], 'state': 'not_attempted'} for c in cases]}
    def save():
        report.update(model_requests=copy.deepcopy(client.requests), inference_attempts=client.limits.used)
        if progress:
            progress(copy.deepcopy(report))
    save()
    try:
        for case, row in zip(cases, report['results']):
            client.limits.check()
            if runtime_check:
                runtime_check()
            row['state'], client.case_id = 'running', case['id']
            calendar, trail, accepted = GuardedCalendar(case), [], []
            def complete(messages, tools):
                client.limits.check()
                try:
                    message = client(messages, tools)
                finally:
                    complete.attempt_events = copy.deepcopy(getattr(client, 'attempt_events', []))
                trail.append({'type': 'assistant', 'message': copy.deepcopy(message)})
                calls = message.get('tool_calls') or []
                if calls:
                    try:
                        proposed = [{'name': c['function']['name'], 'arguments': json.loads(c['function']['arguments'])} for c in calls]
                    except (KeyError, TypeError, ValueError):
                        raise StopPilot('unexpected_tool') from None
                    if accepted or proposed != case['expected_calls']:
                        raise StopPilot('unexpected_tool')
                    accepted.extend(proposed)
                return message
            def on_event(event):
                trail.append(copy.deepcopy(event))
                row['partial_events'] = copy.deepcopy(trail)
                save()
            try:
                run = run_calendar_agent(case['prompt'], complete, calendar,
                                         now=datetime.fromisoformat(suite['reference_now']),
                                         renderer_language=case['language'], on_event=on_event)
                row.update(state='completed', run=copy.deepcopy(run), api_calls=calendar.calls,
                           **grade(case, run, calendar))
                row.pop('partial_events', None)
            except BaseException:
                row.update(state='incomplete', partial_events=copy.deepcopy(trail), api_calls=calendar.calls)
                raise
            save()
            if runtime_check:
                runtime_check()
            if run['status'] != 'completed':
                report['state'] = 'model_error'
                break
        else:
            report['state'] = 'completed'
    except StopPilot as stop:
        report['state'] = stop.state
    except KeyboardInterrupt:
        report['state'] = 'interrupted'
    except Exception as error:
        report.update(state='execution_error', error_type=type(error).__name__)
    finally:
        save()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-controlled', action='store_true')
    parser.add_argument('--cases', default='evals/proposals/v1_controlled_pilot_cases.json')
    parser.add_argument('--private-dir', required=True)
    parser.add_argument('--max-attempts', type=int, default=MAX_ATTEMPTS)
    parser.add_argument('--deadline-seconds', type=float, default=MAX_SECONDS)
    args = parser.parse_args(argv)
    if not args.execute_controlled:
        parser.error('Real local inference requires --execute-controlled and separate approval')
    # Validate every local input before connecting to a model or creating output.
    raw = Path(args.cases).read_bytes()
    suite = json.loads(raw)
    validate_suite(suite)
    limits = Limits(args.max_attempts, args.deadline_seconds)
    output = private_directory(args.private_dir)
    root = Path(__file__).resolve().parent
    manifest = {'suite_sha256': hashlib.sha256(raw).hexdigest(),
                'code_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('*.py'))},
                'max_attempts': limits.cap, 'deadline_seconds': limits.seconds, 'model_settings_changed': False}
    write_private(output / 'manifest.json', manifest)
    def save(value):
        nonlocal report
        report = copy.deepcopy(value)
        write_private(output / 'raw.json', report)
    report = {'state': 'preflight_error', 'results': [{'id': c['id'], 'state': 'not_attempted'} for c in suite['cases']],
              'semantic_pass_claim': False, 'google_requests': 0, 'judge_requests': 0}
    client = None
    try:
        client = PilotClient(limits)
        if client.model != MODEL:
            raise ValueError('Configured model differs from reviewed SUT')
        native = LocalClient(model=MODEL, base_url=client.base.removesuffix('/v1'), timeout=30)
        def runtime():
            rows = native.request('/api/v1/models')['models']
            value = next(m for m in rows if m['key'] == MODEL)
            instances = value['loaded_instances']
            if len(instances) != 1 or instances[0]['config']['context_length'] != 8192:
                raise ValueError('Reviewed SUT must already be loaded with context 8192')
            return value
        before = runtime()
        manifest['runtime_before'] = copy.deepcopy(before)
        write_private(output / 'manifest.json', manifest)
        def runtime_check():
            latest = runtime()
            manifest['runtime_after'] = copy.deepcopy(latest)
            manifest['runtime_unchanged'] = before == latest
            if not manifest['runtime_unchanged']:
                raise StopPilot('runtime_changed')
        report = run_suite(suite, client, progress=save, runtime_check=runtime_check)
    except KeyboardInterrupt:
        report['state'] = 'interrupted'
    except Exception as error:
        report['error_type'] = type(error).__name__
    finally:
        if client is not None:
            report.update(inference_attempts=limits.used, model_requests=copy.deepcopy(client.requests))
        save(report)
        write_private(output / 'manifest.json', manifest)
    passed = sum(r.get('automated_pass') is True for r in report['results'])
    print(json.dumps({'state': report['state'], 'planned': len(report['results']), 'automated_matches': passed,
                      'inference_attempts': limits.used, 'semantic_pass_claim': False}))
    return int(report['state'] != 'completed' or passed != len(suite['cases']) or not manifest.get('runtime_unchanged'))


if __name__ == '__main__':
    raise SystemExit(main())
