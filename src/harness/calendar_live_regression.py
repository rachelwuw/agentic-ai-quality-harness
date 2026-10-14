"""Opt-in live read-only regression. Private evidence only; never run in ordinary CI."""
import argparse
import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit, parse_qs
from zoneinfo import ZoneInfo
from .calendar_agent import run_calendar_agent
from .calendar_evaluate import grade_structure
from .calendar_tools import CalendarError, check_local_availability, connect, resolve_local_interval
from .client import LocalClient
from .trace_facts import interval

IDS = ('live-overlap', 'live-adjacent', 'live-empty')
MODEL = 'openai/gpt-oss-20b'
LIMIT = 12


class BudgetExceeded(CalendarError):
    pass


class Budget:
    def __init__(self, limit=LIMIT):
        self.limit, self.used, self.exhausted = limit, 0, False

    def take(self):
        if self.used >= self.limit:
            self.exhausted = True
            raise BudgetExceeded('Live regression request limit reached')
        self.used += 1


class ReadOnlyAdapter:
    """Count physical events HTTP sends, including AuthorizedSession auth retries.

    OAuth refresh uses Google's separate auth transport and is not counted here.
    No headers or credentials are recorded. The exact path is kept only in memory.
    """
    def __init__(self, inner, calendar_id, budget):
        self.inner, self.budget = inner, budget
        self.path = '/calendar/v3/calendars/' + quote(calendar_id, safe='') + '/events'
        self.records = []

    def send(self, request, **kwargs):
        url = urlsplit(request.url)
        if request.method != 'GET' or url.scheme != 'https' or url.netloc != 'www.googleapis.com' or url.path != self.path:
            raise CalendarError('Unexpected live regression request blocked')
        self.budget.take()
        record = {'method': 'GET', 'query': parse_qs(url.query), 'state': 'started'}
        self.records.append(record)
        started = time.perf_counter()
        try:
            response = self.inner.send(request, **kwargs)
            record.update(state='returned', http_status=response.status_code)
            if response.status_code == 200:
                try:
                    data = response.json()
                    record['projected_response'] = {k: data[k] for k in ('items', 'nextPageToken') if k in data} if isinstance(data, dict) else None
                except (TypeError, ValueError):
                    record['json_valid'] = False
            return response
        except Exception as error:
            record.update(state='error', error_type=type(error).__name__)
            raise
        finally:
            record['elapsed_seconds'] = round(time.perf_counter() - started, 3)

    def close(self):
        self.inner.close()


class BoundedClient(LocalClient):
    def __init__(self, budget):
        super().__init__()
        self.budget = budget

    def request(self, path, payload=None):
        if path == '/chat/completions':
            self.budget.take()  # Every retry passes through request again.
        return super().request(path, payload)


def validate_suite(suite):
    cases = suite['cases']
    if tuple(c['id'] for c in cases) != IDS:
        raise ValueError('Expected exactly the three reviewed cases in fixed order')
    fixture = suite['fixtures']['busy_fixture']
    interval(fixture['start'], fixture['end'], fixture['time_zone'])
    for c in cases:
        if len(c['expected_calls']) != 1 or c['expected_calls'][0]['name'] != 'check_availability':
            raise ValueError('Expected one read-only call per case')
        args = c['expected_calls'][0]['arguments']
        if set(args) != {'start', 'end', 'time_zone'} or not isinstance(c['prompt'], str) or not c['prompt'].strip():
            raise ValueError('Invalid case arguments/prompt')
        if not isinstance(c['expected_available'], bool):
            raise ValueError('Expected a boolean availability label')
        start, end = resolve_local_interval(**args)
        if c['expected_api_interval'] != {'start': start, 'end': end}:
            raise ValueError('Case expected API interval does not match Python resolution')
        if not c['answer_criteria'] or not isinstance(c['forbidden_behaviors'], list):
            raise ValueError('Missing semantic review criteria')
    return cases


def snapshot(result):
    """Compare observable intervals, ignoring order/offset spelling, not identity."""
    if not isinstance(result.get('available'), bool) or result.get('scope') != 'configured_test_calendar_only':
        raise ValueError('Invalid availability or scope')
    values = []
    for busy in result['busy_intervals']:
        fact = interval(busy['start']['dateTime'], busy['end']['dateTime'])
        values.append((fact['utc_start'], fact['utc_end']))
    return {'available': result['available'], 'busy': sorted(values)}


def fixture_matches(case, result, fixture):
    actual = snapshot(result)
    f = interval(fixture['start'], fixture['end'])
    expected = [] if case['expected_available'] else [(f['utc_start'], f['utc_end'])]
    return actual == {'available': case['expected_available'], 'busy': expected}


class OneReadCalendar:
    """One exact planned query per agent case; wrong/extra reads are blocked."""
    def __init__(self, calendar, expected):
        self.calendar, self.expected = calendar, expected
        self.calls, self.attempted_calls, self.results, self.attempt_events = [], [], [], []

    def check_availability(self, start, end):
        args = {'start': start, 'end': end}
        self.attempted_calls.append(args)
        if self.calls or args != self.expected:
            raise CalendarError('Unplanned or additional live query blocked')
        self.calls.append(args)
        try:
            result = self.calendar.check_availability(start, end)
            self.results.append(result)
            return result
        finally:
            self.attempt_events = list(getattr(self.calendar, 'attempt_events', []))


def run_suite(suite, complete, calendar, *, progress=None, stop_requested=lambda: False):
    cases = validate_suite(suite)
    reference_now = datetime.now(ZoneInfo('America/Los_Angeles'))
    report = {'state': 'running', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'reference_now': reference_now.isoformat(), 'case_definitions': suite,
              'calendar_mode': 'live_readonly', 'semantic_review_required': True,
              'direct': [], 'results': []}
    def save():
        if progress:
            progress(report)
    save()
    try:
        # All three adapter checks must succeed before sending any model prompt.
        for c in cases:
            row = {'id': c['id']}
            report['direct'].append(row)
            try:
                result = check_local_availability(calendar, **c['expected_calls'][0]['arguments'])
                row['tool_result'] = result
                row['fixture_matches'] = fixture_matches(c, result, suite['fixtures']['busy_fixture'])
            except (CalendarError, KeyError, TypeError, ValueError) as error:
                row['error_type'] = type(error).__name__
                report['state'] = 'budget_exhausted' if stop_requested() else 'adapter_error'
                save()
                return report
            save()
            if not row['fixture_matches']:
                report['state'] = 'fixture_precondition_failed'
                save()
                return report
        for c, direct in zip(cases, report['direct']):
            wrapper = OneReadCalendar(calendar, c['expected_api_interval'])
            row = {'id': c['id'], 'logical_calendar_calls': wrapper.calls,
                   'attempted_calendar_calls': wrapper.attempted_calls,
                   'tool_events': [], 'fixture_comparison': 'not_observed'}
            report['results'].append(row)
            save()
            def observe(event):
                row['tool_events'].append(event)
                save()
            try:
                run = run_calendar_agent(c['prompt'], complete, wrapper, now=reference_now, on_event=observe)
                row.update(**grade_structure(c, run, wrapper), run=run)
                if wrapper.results:
                    row['fixture_comparison'] = ('same_intervals' if snapshot(wrapper.results[0]) == snapshot(direct['tool_result'])
                                                 else 'changed_intervals')
                save()
                if stop_requested():
                    report['state'] = 'budget_exhausted'
                    break
                if row['fixture_comparison'] == 'changed_intervals':
                    report['state'] = 'fixture_changed'
                    break
                if run['status'] != 'completed':
                    report['state'] = 'model_or_loop_error'
                    break
            except Exception as error:
                row['error_type'] = type(error).__name__
                report['state'] = 'agent_error'
                break
        else:
            report['state'] = 'completed'
    finally:
        save()
    return report


def public_summary(report, google_budget, model_budget):
    """Strict allowlist: never copy answers, dates, errors, Calendar IDs/URLs or raw data."""
    allowed_states = {'running', 'completed', 'adapter_error', 'fixture_precondition_failed',
                      'fixture_changed', 'model_or_loop_error', 'agent_error', 'preflight_error',
                      'budget_exhausted', 'runtime_error', 'interrupted'}
    return {'suite': 'calendar_live_readonly_v1',
            'state': report['state'] if report['state'] in allowed_states else 'preflight_error',
            'google_events_http_sends': google_budget.used, 'model_inference_attempts': model_budget.used,
            'oauth_refresh_count': 'not_instrumented_separate_auth_transport',
            'direct_checks_completed': sum(isinstance(r.get('fixture_matches'), bool) for r in report['direct']),
            'agent_cases_recorded': len(report['results']),
            'cases': [{'id': ident,
                       'fixture_precondition': next((r.get('fixture_matches') if isinstance(r.get('fixture_matches'), bool) else None for r in report['direct'] if r['id'] == ident), None),
                       'agent_structure': next((r.get('structural_pass') if isinstance(r.get('structural_pass'), bool) else None for r in report['results'] if r['id'] == ident), None),
                       'fixture_drift_observed': any(r.get('fixture_comparison') == 'changed_intervals' for r in report['results'] if r['id'] == ident),
                       'answer_review': next(('pending' if r.get('run', {}).get('status') == 'completed' else 'unavailable'
                                              for r in report['results'] if r['id'] == ident), 'not_attempted')} for ident in IDS],
            'semantic_pass_claim': False}


def private_directory(value):
    root = Path.cwd().resolve()
    allowed = root / 'reports' / 'runs'
    dest = Path(value).resolve()
    if allowed.resolve() != allowed or not dest.is_relative_to(allowed) or dest == allowed:
        raise ValueError('Private output must be a new directory under reports/runs')
    dest.mkdir(parents=True, mode=0o700, exist_ok=False)
    os.chmod(dest, 0o700)
    return dest


def write_private(path, value):
    # Atomic owner-only snapshots preserve the last complete report on interruption.
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-readonly', action='store_true', help='Explicit opt-in; requires separate execution approval')
    parser.add_argument('--cases', default='evals/calendar_live_readonly_cases.json')
    parser.add_argument('--private-dir', required=True)
    args = parser.parse_args(argv)
    if not args.live_readonly:
        parser.error('Live execution is disabled without --live-readonly')
    source = Path(args.cases).read_bytes()
    suite = json.loads(source)
    validate_suite(suite)
    output = private_directory(args.private_dir)
    google_budget, model_budget = Budget(), Budget()
    report = {'state': 'preflight_error', 'direct': [], 'results': []}
    manifest = {'cases_sha256': hashlib.sha256(source).hexdigest(), 'request_limit_each': LIMIT,
                'expected_sut': MODEL, 'client_parameters_changed': False,
                'oauth': 'Existing credentials only; connect may refresh. No interactive authorization or new scope.',
                'code_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(Path('src/harness').glob('*.py'))}}
    manifest['implementation_sha256'] = hashlib.sha256(
        json.dumps(manifest['code_sha256'], sort_keys=True).encode()).hexdigest()
    calendar, guard = None, None
    started = time.perf_counter()
    def summary(value):
        return {**public_summary(value, google_budget, model_budget),
                'elapsed_seconds': manifest.get('elapsed_seconds'),
                'implementation_sha256': manifest['implementation_sha256']}
    def save(value):
        nonlocal report
        report = value
        write_private(output / 'raw.json', {**value, 'events_http': guard.records if guard else []})
        write_private(output / 'summary.json', summary(value))
    try:
        client = BoundedClient(model_budget)
        if client.model != MODEL:
            raise ValueError('Configured SUT differs from the reviewed model')
        native = LocalClient(model=MODEL, base_url=client.base.removesuffix('/v1'), timeout=30)
        runtime = next(m for m in native.request('/api/v1/models')['models'] if m['key'] == MODEL)
        if len(runtime['loaded_instances']) != 1 or runtime['loaded_instances'][0]['config']['context_length'] != 8192:
            raise ValueError('Reviewed SUT must already be loaded with context 8192')
        manifest['runtime_before'] = runtime
        write_private(output / 'manifest.json', manifest)
        calendar = connect()  # Only reachable after opt-in and all local checks.
        endpoint = 'https://www.googleapis.com/calendar/v3/calendars/' + quote(calendar.calendar_id, safe='') + '/events'
        guard = ReadOnlyAdapter(calendar.session.get_adapter(endpoint), calendar.calendar_id, google_budget)
        calendar.session.mount('https://', guard)
        calendar.session.mount('http://', guard)
        report = run_suite(suite, client, calendar, progress=save,
                           stop_requested=lambda: google_budget.exhausted or model_budget.exhausted)
        manifest['runtime_after'] = next(m for m in native.request('/api/v1/models')['models'] if m['key'] == MODEL)
        manifest['runtime_unchanged'] = manifest['runtime_before'] == manifest['runtime_after']
        if not manifest['runtime_unchanged']:
            report['state'] = 'runtime_error'
    except KeyboardInterrupt:
        report['state'] = 'interrupted'
    except Exception as error:
        report['error_type'] = type(error).__name__
        if report['state'] != 'preflight_error':
            report['state'] = 'runtime_error'
    finally:
        if calendar:
            calendar.session.close()
        manifest['elapsed_seconds'] = round(time.perf_counter() - started, 3)
        save(report)
        write_private(output / 'manifest.json', manifest)
    # Only the allowlisted summary is printed. No private exception text or paths.
    print(json.dumps(summary(report)))
    return int(report['state'] != 'completed' or not manifest.get('runtime_unchanged') or
               not all(x.get('structural_pass') for x in report['results']))


if __name__ == '__main__':
    raise SystemExit(main())
