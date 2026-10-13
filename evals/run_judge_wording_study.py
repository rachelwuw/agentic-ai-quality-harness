"""Frozen 24-request local wording study; labels never enter inference."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from harness.calendar_judge import SYSTEM, local_complete, review
from harness.client import LocalClient
from harness.saved_trace import validate_case, validate_source
from harness.trace_facts import derive_trace_facts

ROOT = Path(__file__).resolve().parents[1]
FILES = ['evals/judge_wording_cases.json', 'evals/judge_wording_expected_labels.json',
         'evals/calendar_judge_wording_original.json', 'evals/calendar_judge_wording_clarified.json',
         'evals/run_judge_wording_study.py', 'src/harness/calendar_judge.py',
         'src/harness/trace_facts.py', 'src/harness/saved_trace.py', 'src/harness/client.py',
         'evals/calendar_judge_rubric.json']
SCHEDULE = [('original', 1), ('clarified', 1), ('clarified', 2), ('original', 2)]


def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}


def runtime():
    with urlopen('http://127.0.0.1:1234/api/v1/models', timeout=5) as response:
        data = json.load(response)
    model = next(x for x in data['models'] if x['key'] == 'qwen/qwen3.5-9b')
    assert model['quantization']['name'] == 'Q8_0'
    assert len(model['loaded_instances']) == 1
    assert model['loaded_instances'][0]['config']['context_length'] == 8192
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, help='New, unique ignored run directory')
    args = parser.parse_args()
    source = json.loads((ROOT / FILES[0]).read_text())
    validate_source(source)
    assert [x['id'] for x in source['results']] == ['wording-' + x for x in 'ADBECF']
    rubrics = {arm: json.loads((ROOT / f'evals/calendar_judge_wording_{arm}.json').read_text())
               for arm in ('original', 'clarified')}
    for item in source['results']:
        assert not validate_case(item), item['id']
        assert len(item['answer_review']['criteria']) == 9
        original = item['answer_review']['criteria']
        clarified = rubrics['clarified']['criteria_overrides'][item['id']]
        for index, (first, second) in enumerate(zip(original, clarified)):
            expected = first.replace('No conversion claim satisfies this check.',
                'If the answer makes no event-conversion claim, return PASS for this check.') if index in (5, 6) else first
            assert second == expected
        facts = derive_trace_facts(item)
        assert facts['tool_observations'][0]['busy_intervals'][0]['overlaps_query']
    frozen = hashes()
    model = runtime()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'state': 'frozen_before_inference', 'recorded_at': datetime.now(timezone.utc).isoformat(),
        'approval': source['approval'], 'schedule': SCHEDULE, 'order': 'ADBECF',
        'planned_requests': 24, 'planned_criterion_judgments': 216,
        'sha256': frozen, 'system_prompt_sha256': hashlib.sha256(SYSTEM.encode()).hexdigest(),
        'runtime': model, 'lm_studio_version': '0.4.25+1', 'cli_commit': '69d945a',
        'ui_verified': {'thinking': True, 'reasoning_budget_enabled': True, 'reasoning_budget': 1024},
        'temperature': 0, 'max_tokens': 6144, 'timeout_seconds': 600,
        'scope': 'Approved same-author synthetic development comparison, not independent benchmark; one loaded-model session; ABBA order limits but does not eliminate order effects.'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    count = 0
    for arm, round_number in SCHEDULE:
        assert hashes() == frozen, 'Frozen files changed'
        assert runtime() == model, 'Runtime configuration changed'
        report = {'state': 'running', 'arm': arm, 'round': round_number,
            'rubric_version': rubrics[arm]['version'], 'manifest': 'manifest.json',
            'source_sha256': frozen[FILES[0]], 'system_prompt_sha256': manifest['system_prompt_sha256'],
            'rubric_sha256': frozen[f'evals/calendar_judge_wording_{arm}.json'],
            'judge_model': 'qwen/qwen3.5-9b', 'temperature': 0, 'human_review_required': True,
            'results': []}
        path = output / f'{arm}-round{round_number}.json'
        path.write_text(json.dumps(report, indent=2) + '\n')
        complete = local_complete(LocalClient(model='qwen/qwen3.5-9b', timeout=600),
                                  thinking=True, max_tokens=6144, constrained=True)
        for item in source['results']:
            assert hashes() == frozen, 'Frozen files changed'
            count += 1
            print(f'[{count}/24] {arm} round {round_number}: {item["id"]} requesting', flush=True)
            complete.last_metadata = {}
            scored = review(item, [], complete,
                criteria=rubrics[arm]['criteria_overrides'].get(item['id']),
                deterministic_requirements=rubrics[arm]['deterministic_requirements'], derive_facts=True)
            generation = dict(complete.last_metadata)
            usage = generation.get('usage', {})
            generation['reasoning_tokens'] = usage.get('completion_tokens_details', {}).get('reasoning_tokens')
            report['results'].append({'id': item['id'], 'structural_pass': item['structural_pass'],
                                      **scored, 'generation': generation})
            path.write_text(json.dumps(report, indent=2) + '\n')
            print(f'[{count}/24] {scored["status"]} {scored["verdict"]}; seconds={generation.get("elapsed_seconds")}; reasoning={generation["reasoning_tokens"]}', flush=True)
            if scored.get('error_category') == 'transport_error' or generation['reasoning_tokens'] != 1024:
                report['state'] = 'blocked_runtime'
                path.write_text(json.dumps(report, indent=2) + '\n')
                raise RuntimeError('Runtime/transport blocker; preserve request without replacement or retry')
        report['state'] = 'completed'
        path.write_text(json.dumps(report, indent=2) + '\n')
    assert count == 24 and hashes() == frozen
    (output / 'execution_complete.json').write_text(json.dumps({'requests': count, 'state': 'completed',
        'post_run_runtime': runtime(), 'post_run_hashes': hashes()}, indent=2) + '\n')
    print('Completed exactly 24 single-attempt requests.', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
