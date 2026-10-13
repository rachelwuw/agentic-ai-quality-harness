"""Compare preserved wording-study reports; no model or network access."""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


def confusion(values):
    counts = {}
    for expected, observed in values:
        key = expected + ' -> ' + (observed or 'UNAVAILABLE')
        counts[key] = counts.get(key, 0) + 1
    return counts


def compare(reports, labels):
    rows = []
    for arm in ('original', 'clarified'):
        for round_number in (1, 2):
            report = reports[(arm, round_number)]
            assert report['state'] in {'completed', 'completed_with_transport_error'}
            assert len(report['results']) == 6
            assert {x['id'] for x in report['results']} == set(labels)
            for item in report['results']:
                expected = labels[item['id']]
                valid = item['status'] == 'reviewed'
                checks = {c['id']: c for c in item['checks']} if valid else {}
                if valid:
                    assert set(checks) == set(expected['criteria']) and len(item['checks']) == 9
                rows.append({'arm': arm, 'round': round_number, 'id': item['id'],
                    'status': item['status'], 'error_category': item.get('error_category'),
                    'expected': expected['overall'], 'observed': item['verdict'] if valid else None,
                    'operational_verdict': item['verdict'], 'generation': item['generation'],
                    'criteria': [{'id': cid, 'expected': verdict, 'observed': checks.get(cid, {}).get('verdict'),
                        'reason': checks.get(cid, {}).get('reason'), 'evidence': checks.get(cid, {}).get('evidence')}
                        for cid, verdict in expected['criteria'].items()]})
    summary = {}
    for arm in ('original', 'clarified'):
        selected = [r for r in rows if r['arm'] == arm]
        criteria = [c for r in selected for c in r['criteria']]
        durations = [r['generation']['elapsed_seconds'] for r in selected]
        pairs = []
        for ident in labels:
            a, b = [next(r for r in selected if r['id'] == ident and r['round'] == i) for i in (1, 2)]
            pair = {'id': ident, 'overall_available': a['observed'] is not None and b['observed'] is not None,
                    'criteria': []}
            pair['overall_consistent'] = pair['overall_available'] and a['observed'] == b['observed']
            for first, second in zip(a['criteria'], b['criteria']):
                available = first['observed'] is not None and second['observed'] is not None
                pair['criteria'].append({'id': first['id'], 'available': available,
                    'consistent': available and first['observed'] == second['observed']})
            pairs.append(pair)
        summary[arm] = {'planned_requests': 12, 'valid_outputs': sum(r['observed'] is not None for r in selected),
            'operational_errors': sum(r['observed'] is None for r in selected),
            'semantic_uncertain': sum(r['observed'] == 'UNCERTAIN' for r in selected),
            'planned_criteria': 108, 'available_criteria': sum(c['observed'] is not None for c in criteria),
            'criterion_matches': sum(c['observed'] == c['expected'] for c in criteria),
            'overall_matches': sum(r['observed'] == r['expected'] for r in selected),
            'overall_confusion': confusion((r['expected'], r['observed']) for r in selected),
            'criterion_confusion': {cid: confusion((c['expected'], c['observed']) for c in criteria if c['id'] == cid)
                for cid in labels[next(iter(labels))]['criteria']},
            'overall_repeat_available': sum(p['overall_available'] for p in pairs),
            'overall_repeat_consistent': sum(p['overall_consistent'] for p in pairs),
            'criterion_repeat_available': sum(c['available'] for p in pairs for c in p['criteria']),
            'criterion_repeat_consistent': sum(c['consistent'] for p in pairs for c in p['criteria']),
            'duration_seconds': {'sum': sum(durations), 'median': statistics.median(durations),
                'maximum': max(durations), 'exploratory_p95_nearest_rank': sorted(durations)[math.ceil(.95*len(durations))-1]},
            'repeat_pairs': pairs}
    transitions = []
    for round_number in (1, 2):
        for ident in labels:
            a, b = [next(r for r in rows if r['arm'] == arm and r['round'] == round_number and r['id'] == ident)
                    for arm in ('original', 'clarified')]
            for first, second in zip(a['criteria'], b['criteria']):
                transitions.append({'round': round_number, 'id': ident, 'criterion': first['id'],
                    'expected': first['expected'], 'original': first['observed'], 'clarified': second['observed']})
    return {'scope': 'Approved same-author synthetic development comparison, not independent accuracy or release signoff',
        'summary': summary, 'rows': rows, 'cross_arm_criterion_pairs': transitions,
        'cross_arm_improvements': sum(t['original'] is not None and t['clarified'] is not None and
            t['original'] != t['expected'] and t['clarified'] == t['expected'] for t in transitions),
        'cross_arm_regressions': sum(t['original'] is not None and t['clarified'] is not None and
            t['original'] == t['expected'] and t['clarified'] != t['expected'] for t in transitions),
        'cross_arm_available': sum(t['original'] is not None and t['clarified'] is not None for t in transitions),
        'cross_arm_common_matches': {arm: sum(t['original'] is not None and t['clarified'] is not None and
            t[arm] == t['expected'] for t in transitions) for arm in ('original', 'clarified')},
        'cross_arm_unavailable': sum(t['original'] is None or t['clarified'] is None for t in transitions)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run = Path(args.run_dir)
    output = Path(args.output)
    assert not output.exists(), 'Do not overwrite prior comparisons'
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((run / 'manifest.json').read_text())
    for name, digest in manifest['sha256'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    assert Path(args.labels).resolve() == (root / 'evals/judge_wording_expected_labels.json').resolve()
    complete = json.loads((run / 'execution_complete.json').read_text())
    assert complete['requests'] == 24 and complete['post_run_hashes'] == manifest['sha256']
    paths = complete.get('report_paths', {})
    assert paths in ({}, {'original-round2.json': 'resumed-original-round2.json'})
    if paths:
        continuation = json.loads((run / 'continuation.json').read_text())
        assert hashlib.sha256((run / 'original-round2.json').read_bytes()).hexdigest() == continuation['original_block_sha256']
        assert continuation['completed_attempts_before_resume'] == 23 and continuation['request_to_execute'] == 24
        resumed = json.loads((run / 'resumed-original-round2.json').read_text())
        blocked = json.loads((run / 'original-round2.json').read_text())
        assert resumed['results'][:5] == blocked['results'] and len(resumed['results']) == 6
        assert resumed['results'][-1]['id'] == 'wording-F'
    reports = {(arm, i): json.loads((run / paths.get(f'{arm}-round{i}.json', f'{arm}-round{i}.json')).read_text())
               for arm in ('original', 'clarified') for i in (1, 2)}
    result = compare(reports, json.loads(Path(args.labels).read_text())['labels'])
    result['manifest'] = manifest
    names = [f'{arm}-round{i}.json' for arm, i in reports] + list(paths.values())
    result['raw_sha256'] = {name: hashlib.sha256((run / name).read_bytes()).hexdigest() for name in names}
    result['report_paths'] = paths
    result['comparator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({arm: {k: v for k, v in stats.items() if k != 'repeat_pairs'}
                      for arm, stats in result['summary'].items()}, indent=2))
    print('Cross-arm improvements:', result['cross_arm_improvements'], 'regressions:', result['cross_arm_regressions'])


if __name__ == '__main__':
    main()
