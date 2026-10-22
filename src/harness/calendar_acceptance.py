"""References/routes for the versioned fresh controlled acceptance protocol.

No model, renderer or live Calendar is called to create reference answers here.
"""
import copy
from datetime import datetime

from .calendar_input import date_clarification
from .calendar_tools import LocalTimeError, resolve_local_interval
from .trace_facts import interval

SCHEMA = 'calendar-controlled-acceptance-v1'
IDS = tuple(f'v1a-{n:02}' for n in range(1, 21))
BATCHES = {1: IDS[:6], 2: IDS[6:12], 3: IDS[12:18], 4: IDS[18:]}


def routes(case):
    return case.get('routes', [case])


def select_batch(suite, batch):
    if type(batch) is not int or batch not in BATCHES:
        raise ValueError('Fresh acceptance requires an explicit batch 1..4')
    return [case for case in suite['cases'] if case['id'] in BATCHES[batch]]


def validate_suite(suite):
    if suite.get('schema') != SCHEMA or tuple(c['id'] for c in suite['cases']) != IDS:
        raise ValueError('Expected the versioned twenty fresh cases in order')
    now = datetime.fromisoformat(suite['reference_now'])
    if now.utcoffset() is None:
        raise ValueError('Frozen reference time requires an offset')
    for case in suite['cases']:
        if case['language'] not in ('en', 'zh-TW') or not isinstance(case['prompt'], str) or not case['prompt'].strip():
            raise ValueError('Invalid case prompt/language')
        mode = case['fixture']['mode']
        if mode not in ('busy_fixture', 'empty_fixture', 'none', 'raise_calendar_error'):
            raise ValueError('Only controlled fixtures are permitted')
        options = case['routes']
        if not isinstance(options, list) or not 1 <= len(options) <= 2:
            raise ValueError('Expected one route or two DST alternatives')
        if (len(options) == 2) != (case['id'] in ('v1a-06', 'v1a-07')):
            raise ValueError('Both predeclared DST routes must be retained only on DST cases')
        if any(not isinstance(r.get('id'), str) or not r['id'] for r in options) or len({r['id'] for r in options}) != len(options):
            raise ValueError('Route ids must be nonempty and unique')
        if len(options) == 2 and {r.get('expected_error') for r in options} != {None, 'dst_time_requires_clarification'}:
            raise ValueError('Only predeclared DST alternatives are allowed')
        signatures = []
        for route in options:
            calls, api, expected = route['expected_calls'], route['expected_api_interval'], route['expected']
            if calls in signatures:
                raise ValueError('Duplicate tool route')
            signatures.append(calls)
            if not isinstance(expected['lines'], list) or not all(isinstance(s, str) for s in expected['lines']):
                raise ValueError('Missing literal product reference')
            if not calls:
                if api is not None or route['reference_utc'] is not None or mode != 'none' or route.get('expected_error') is not None or expected != {
                        'status': 'unsupported', 'lines': [], 'available': None, 'event_local': None}:
                    raise ValueError('Invalid no-tool route')
                continue
            if len(calls) != 1 or calls[0]['name'] != 'check_availability' or set(calls[0]['arguments']) != {'start', 'end', 'time_zone'}:
                raise ValueError('One exact availability call is required')
            error = route.get('expected_error')
            try:
                start, end = resolve_local_interval(**calls[0]['arguments'])
            except LocalTimeError as exc:
                if error != 'dst_time_requires_clarification' or exc.code != error or mode != 'none' or api is not None or route['reference_utc'] is not None:
                    raise ValueError('Unexpected invalid local interval') from exc
            else:
                if error == 'dst_time_requires_clarification' or api != {'start': start, 'end': end}:
                    raise ValueError('Resolved query differs from reference')
                utc = interval(start, end)
                if route['reference_utc'] != {'start': utc['utc_start'], 'end': utc['utc_end']}:
                    raise ValueError('UTC endpoint reference differs from resolved query')
                if mode in ('busy_fixture', 'empty_fixture'):
                    if error is not None or expected['status'] != 'rendered':
                        raise ValueError('Invalid successful-tool reference')
                    endpoints, overlaps = None, False
                    if mode == 'busy_fixture':
                        busy = case['fixture']['busy']
                        event = interval(busy['start'], busy['end'], calls[0]['arguments']['time_zone'])
                        query = interval(start, end)
                        overlaps = event['utc_start'] < query['utc_end'] and event['utc_end'] > query['utc_start']
                        local = event['in_query_timezone']
                        if overlaps:
                            endpoints = [local[k]['datetime'] for k in ('start', 'end')]
                    if expected['available'] is not (not overlaps) or expected['event_local'] != endpoints:
                        raise ValueError('Event reference differs from fixture')
                elif mode != 'raise_calendar_error' or error != 'calendar_unavailable':
                    raise ValueError('A valid query requires an explicit Calendar fixture')
            if error and (expected['status'] != 'unknown' or expected['available'] is not None or expected['event_local'] is not None):
                raise ValueError('Invalid error reference')
            if not expected['lines']:
                raise ValueError('Missing literal product text')
        if any(route['expected_api_interval'] != options[0]['expected_api_interval'] for route in options):
            raise ValueError('Routes cannot authorize different Calendar operations')
        required = case['input_message']
        if (required is not None) != (case['id'] in ('v1a-15', 'v1a-16', 'v1a-17')):
            raise ValueError('Preserve the three explicit no-inference input-gate cases')
        decision = date_clarification(case['prompt'], case['language'])
        if required is not None:
            if mode != 'none' or len(options) != 1 or options[0]['expected_calls'] or not decision or decision['message'] != required:
                raise ValueError('Invalid deterministic input-gate reference')
        elif decision is not None:
            raise ValueError('A model case would be intercepted by the date gate')
        if (not isinstance(case['raw_review_criteria'], list) or not case['raw_review_criteria'] or
                not all(isinstance(s, str) and s.strip() for s in case['raw_review_criteria'])):
            raise ValueError('Raw answer review criteria are required')
    return suite['cases']


def grade(case, run, calendar, legacy_grade):
    """Grade only observed route; raw semantics/human acceptance remain pending."""
    import json
    actual = [{'name': e['name'], 'arguments': json.loads(e['arguments'])}
              for e in run['events'] if e['type'] == 'tool']
    chosen = next((r for r in case['routes'] if actual == r['expected_calls']), None)
    if chosen is None:
        return {'structural_checks': {'completed': run['status'] == 'completed', 'tool_arguments': False,
                                     'api_interval': False}, 'python_facts_match': False,
                'product_reference_match': False, 'input_gate_match': False, 'route': None,
                'automated_pass': False, 'raw_answer_review': 'pending', 'human_product_review': 'pending',
                'semantic_pass_claim': False}
    flattened = {**copy.deepcopy(case), **copy.deepcopy(chosen)}
    result = legacy_grade(flattened, run, calendar)
    required = case['input_message']
    validation = run.get('input_validation')
    gate_ok = (validation is None if required is None else
               isinstance(validation, dict) and validation.get('message') == required and
               validation.get('origin') == 'deterministic_input_validation' and validation.get('model_called') is False and
               run['answer'] == '' and run['events'] == [])
    result.update(input_gate_match=gate_ok, route=chosen['id'],
                  raw_review_criteria=copy.deepcopy(case['raw_review_criteria']))
    result['automated_pass'] = result['automated_pass'] and gate_ok
    return result
