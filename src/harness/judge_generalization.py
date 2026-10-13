"""Explicit opt-in, bounded development experiment; no SUT or Google calls."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from .calendar_judge import SYSTEM, review, local_complete
from .client import LocalClient
from .saved_trace import validate_source, validate_case

CASE_IDS = tuple('generalization-' + x for x in ('P1', 'P2', 'P3', 'P4', 'N1', 'N2', 'N3', 'N4'))
MODES = ('batch', 'c6', 'c7')
MODEL = 'qwen/qwen3.5-9b'


def schedule(source):
    items = validate_source(source)
    if tuple(x['id'] for x in items) != CASE_IDS:
        raise ValueError('Expected the eight approved cases in their fixed order')
    for item in items:
        if validate_case(item) or len(item['answer_review']['criteria']) != 9 or item['answer_review']['forbidden_behaviors']:
            raise ValueError('Invalid approved case or unexpected checks')
    return [(item, mode) for i, item in enumerate(items)
            for mode in MODES[i % 3:] + MODES[:i % 3]]


def run_request(item, mode, complete, rubric):
    criteria = None if mode == 'batch' else [item['answer_review']['criteria'][int(mode[1:]) - 1]]
    complete.last_metadata = {}
    result = review(item, [], complete, criteria=criteria,
                    deterministic_requirements=rubric['deterministic_requirements'], derive_facts=True)
    return {'id': item['id'], 'mode': mode,
            'target_mapping': {'c6': 'c6', 'c7': 'c7'} if mode == 'batch' else {mode: 'c1'},
            **result, 'generation': getattr(complete, 'last_metadata', {})}


def compare(report, labels):
    """Score only the 16 common targets; never count error placeholders as judgments."""
    rows = []
    indexed = {}
    for result in report['results']:
        key = (result['id'], result['mode'])
        if key in indexed:
            raise ValueError('Duplicate case/mode result')
        indexed[key] = result
    for ident in CASE_IDS:
        for criterion in ('c6', 'c7'):
            row = {'id': ident, 'criterion': criterion, 'expected': labels['labels'][ident]['criteria'][criterion]}
            for format_, mode, output_id in (('batch', 'batch', criterion), ('single', criterion, 'c1')):
                result = indexed.get((ident, mode), {})
                check = next((c for c in result.get('checks', []) if c['id'] == output_id), None)
                row[format_] = check if result.get('status') == 'reviewed' else None
                row[format_ + '_matches'] = bool(row[format_] and row[format_]['verdict'] == row['expected'])
            rows.append(row)
    counts = {format_: {'planned_targets': 16,
                       'available_targets': sum(r[format_] is not None for r in rows),
                       'matches': sum(r[format_ + '_matches'] for r in rows),
                       'false_pass': sum(bool(r[format_] and r['expected'] == 'FAIL' and r[format_]['verdict'] == 'PASS') for r in rows),
                       'false_fail': sum(bool(r[format_] and r['expected'] == 'PASS' and r[format_]['verdict'] == 'FAIL') for r in rows),
                       'uncertain': sum(bool(r[format_] and r[format_]['verdict'] == 'UNCERTAIN') for r in rows)}
              for format_ in ('batch', 'single')}
    paired = [r for r in rows if r['batch'] is not None and r['single'] is not None]
    improvements = [r['id'] + '/' + r['criterion'] for r in paired if not r['batch_matches'] and r['single_matches']]
    regressions = [r['id'] + '/' + r['criterion'] for r in paired if r['batch_matches'] and not r['single_matches']]
    complete = (report['state'] == 'completed' and len(indexed) == 24
                and all(r.get('status') == 'reviewed' for r in indexed.values())
                and len(paired) == 16)
    positives = [r for r in rows if '-P' in r['id']]
    negatives = [r for r in rows if r['expected'] == 'FAIL']
    costs = {format_: {'requests': len(selected := [r for r in report['results'] if (r['mode'] == 'batch') == (format_ == 'batch')]),
                       'elapsed_seconds': round(sum(r['generation'].get('elapsed_seconds', 0) for r in selected), 3),
                       'usage': {k: sum(r['generation'].get('usage', {}).get(k, 0) for r in selected)
                                 for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')}}
             for format_ in ('batch', 'single')}
    return {'scope': 'Same-author development validation; not independent accuracy or repeatability evidence',
            'counts': counts, 'paired_targets': len(paired), 'improvements': improvements, 'regressions': regressions,
            'gates': {'complete_24_valid': complete,
                      'at_least_two_improvements_zero_regressions': complete and len(improvements) >= 2 and not regressions,
                      'positive_8_and_expected_fail_5': complete and all(r['single_matches'] for r in positives + negatives),
                      'reason_evidence_review': 'pending_manual_review', 'cost_acceptance': 'pending_Rachel_review'},
            'costs': costs, 'targets': rows}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def runtime(client):
    native = LocalClient(model=MODEL, base_url='http://127.0.0.1:1234', timeout=30)
    value = native.request('/api/v1/models')
    candidates = [x for x in value['models'] if x.get('key') == MODEL]
    if len(candidates) != 1:
        raise ValueError('Expected exactly one Qwen runtime')
    model = candidates[0]
    if model.get('quantization', {}).get('name') != 'Q8_0':
        raise ValueError('Unexpected quantization')
    instances = model.get('loaded_instances', [])
    if len(instances) != 1 or instances[0]['config'].get('context_length') != 8192:
        raise ValueError('Unexpected loaded runtime/context')
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    source_path = Path('evals/judge_generalization_cases.json')
    labels_path = Path('evals/judge_generalization_labels.json')
    rubric_path = Path('evals/calendar_judge_generalization_rubric.json')
    source = json.loads(source_path.read_text())
    labels = json.loads(labels_path.read_text())
    rubric = json.loads(rubric_path.read_text())
    if source.get('state') != 'frozen_Rachel_approved' or labels.get('status') != 'Rachel_approved':
        raise ValueError('Execution requires approved inputs/labels')
    requests = schedule(source)
    paths = [source_path, labels_path, rubric_path, Path(__file__),
             Path('src/harness/calendar_judge.py'), Path('src/harness/client.py'),
             Path('src/harness/trace_facts.py'), Path('evals/calendar_judge_rubric_v10.json'),
             Path('evals/proposals/judge_generalization_cases_draft.json'),
             Path('evals/proposals/judge_generalization_labels_draft.json')]
    hashes = {str(p): sha(p) for p in paths}
    client = LocalClient(model=MODEL, base_url='http://127.0.0.1:1234/v1', timeout=600)
    initial_runtime = runtime(client)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    report = {'state': 'running', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'planned_requests': 24, 'retries': 0, 'source_hashes': hashes,
              'system_sha256': hashlib.sha256(SYSTEM.encode()).hexdigest(),
              'judge_model': MODEL, 'initial_runtime': initial_runtime,
              'settings': {'temperature': 0, 'thinking': True, 'ui_reasoning_budget': 1024,
                           'ui_reasoning_budget_verified': 'CUA before run', 'max_tokens': 6144,
                           'timeout_seconds': 600, 'constrained': True},
              'schedule': [{'id': i['id'], 'mode': m} for i, m in requests], 'results': []}
    complete = local_complete(client, thinking=True, max_tokens=6144, constrained=True)
    def save():
        (output / 'raw_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    save()
    try:
        for index, (item, mode) in enumerate(requests, 1):
            if any(sha(p) != digest for p, digest in hashes.items()):
                raise ValueError('Frozen study files changed')
            if runtime(client) != initial_runtime:
                raise ValueError('Runtime changed')
            print(f'[{index}/24] {item["id"]} {mode}: requesting', flush=True)
            result = run_request(item, mode, complete, rubric)
            result['request_index'] = index
            report['results'].append(result)
            save()
            usage = result['generation'].get('usage', {})
            reasoning = usage.get('completion_tokens_details', {}).get('reasoning_tokens')
            print(f'  {result["status"]} {result["verdict"]}, {result["generation"].get("elapsed_seconds")}s, reasoning={reasoning}', flush=True)
            if result.get('error_category') == 'transport_error':
                raise RuntimeError('Transport failure; no retry authorized')
            if not isinstance(reasoning, int) or reasoning <= 0:
                raise RuntimeError('Thinking metadata not observed; stop without retry')
        if any(sha(p) != digest for p, digest in hashes.items()):
            raise ValueError('Frozen study files changed')
        report['final_runtime'] = runtime(client)
        if report['final_runtime'] != initial_runtime:
            raise ValueError('Runtime changed')
        report['state'] = 'completed'
    except Exception as error:
        report['state'] = 'stopped'
        report['stop_reason'] = str(error)
        raise
    finally:
        save()
        (output / 'comparison.json').write_text(json.dumps(compare(report, labels), ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
