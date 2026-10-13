# Approved no-conversion-claim wording comparison

Rachel approved the exact six answers, reference facts and criterion labels in this chat, then separately authorized 24 local Qwen requests on October 12, 2026 (America/Los_Angeles). The prior PR #4 remains unmerged and unchanged. This study has an independent task branch based on main.

## One changed variable

Original c6/c7 ending: `No conversion claim satisfies this check.`

Clarified c6/c7 ending: `If the answer makes no event-conversion claim, return PASS for this check.`

All other requirement text, answers, traces, Python facts, system prompt, aggregation and runtime settings are identical between arms. The source retains original criteria; the clarified rubric provides only those two sentence replacements. Both rubric files use explicit opt-in version `calendar-answer-v12`. Default v10 remains unchanged. The runner reuses the existing `review` and strict-schema `local_complete`; it adds no alternative semantic evaluator.

Cases are new same-author synthetic development controls, not independently authored benchmark items. Summer fixture: LA July 20, 2027 09:00–09:30 UTC-07 equals Taipei July 21 00:00–00:30. Winter fixture: LA January 20, 2027 09:00–09:30 UTC-08 equals Taipei January 21 01:00–01:30. Each query overlaps from minute 15 to 30. These are controlled records, not private Google events or new SUT generations.

| Case | Contrast | c2 | c6 | c7 | Overall |
| --- | --- | --- | --- | --- | --- |
| A | Original LA event, no conversion claim | PASS | PASS | PASS | PASS |
| B | Correct winter conversion | PASS | PASS | PASS | PASS |
| C | Correct summer conversion expressed as 'In Taipei time' | PASS | PASS | PASS | PASS |
| D | Correct target numbers, contradictory LA label | FAIL | FAIL | PASS | FAIL |
| E | Winter conversion one hour early, correct target attribution | FAIL | PASS | FAIL | FAIL |
| F | Correct opening conversion followed by wrong restatement | FAIL | PASS | FAIL | FAIL |

c1/c3/c4/c5/c8/c9 pass in all cases. c3 allows omission of optional query-window conversion. Approved labels are separate and never sent to inference. Review approval covers inputs and execution, not model outputs or release signoff.

## Frozen execution

Balanced arm order: original round 1, clarified round 1, clarified round 2, original round 2 (ABBA). Case order A/D/B/E/C/F in every round. This reduces simple arm-versus-time confounding but is not randomization and does not eliminate order/cache effects. Each of 24 requests uses a fresh conversation and a single transport attempt. No outcome-based tuning, reruns, replacement errors or extra model probes.

Qwen/qwen3.5-9b, Q8_0, LM Studio 0.4.25+1, context 8192; UI Thinking on and enabled reasoning budget 1024 verified before execution. Temperature 0, strict JSON, max output 6144, timeout 600. Preserve returned reasoning counts separately from requested settings. All requests are sequential in one loaded-model session. No Google calls. Broader reload/runtime/language reliability is untested.

`run_judge_wording_study.py` validates fixtures and the exact sentence-only difference before freezing hashes. It snapshots runtime metadata and guards frozen input hashes between requests, checks runtime between blocks, and stops on transport or reasoning-configuration blockers without retry. Unique output directories prevent overwriting existing evidence.

```sh
python evals/run_judge_wording_study.py --output-dir reports/runs/UNIQUE-wording-study
python evals/compare_judge_wording_study.py --run-dir reports/runs/UNIQUE-wording-study \
  --labels evals/judge_wording_expected_labels.json --output reports/runs/UNIQUE-wording-study/comparison.json
```

The first command explicitly performs 24 live requests; it is not a pytest command. Replay requires fresh user authorization. The second command is offline and validates manifest hashes.

## Interpretation

Each arm has 12 planned requests and 108 planned criterion judgments. Report overall and criterion confusion, operational errors and valid semantic UNCERTAIN separately. Missing judgments stay unavailable; planned and valid-only denominators are both reported. Each arm has six overall and 54 criterion repeat pairs. Cross-arm round-matched comparisons expose improvements and regressions, with unavailable pairs counted separately.

Matching labels do not establish supported reasons. Review reason/verdict contradictions and invented evidence manually without rewriting raw judgments. Inspect c6/c7 error reductions, overall false PASS/false FAIL, new misses, consistency and generation time. A small development comparison cannot establish general reliability; no automatic default activation or release gate follows.

## Execution outcome

All 24 authorized attempts are now recorded. Request 23 failed with a transport HTTPError, triggering the frozen stop guard. After the user requested continuation and configuration/hashes were reverified, only unattempted request 24 ran; request 23 was never retried. The interrupted block remains unchanged alongside a separate resumed block and continuation audit. See [preserved result review](../reports/baseline/JUDGE_WORDING_COMPARISON_REVIEW.md). The comparator counts the failed judgment as unavailable and uses only the resumed block for final round totals.
