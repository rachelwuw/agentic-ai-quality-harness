# Judge v9: independent event-conversion checks

Status: implemented and evaluated once. 101 pytest tests passed in 3.40 seconds. The three focused outputs were valid and matched authored expectations (FAIL/PASS/PASS), with observed Thinking 1019–1024 tokens. [Separate evidence review](../reports/baseline/JUDGE_POLICY_V9_VALIDATION.md). This is targeted development validation, not overall reliability.

v8 missed the original cal-08 conversion claim. Its [raw output and separate review](../reports/baseline/JUDGE_V8_ORIGINAL_CASE_REVIEW.md) remain unchanged. v8 is archived at `calendar_judge_rubric_v8.json`; the default rubric is now `calendar-answer-v9`.

## Minimal change

The event-interval criterion now allows either the original Los Angeles interval or its correct Taipei equivalent. This avoids rejecting a valid conversion solely because it uses a different timezone.

Three independent additional cal-08 checks cover Pacific daylight wording, consistency of a conversion claim with the displayed target timezone, and accuracy of the converted event date and clock values. A parenthetical claim counts as a claim. Merely matching the original tool interval does not excuse a false conversion statement. Optional conversions may be omitted. cal-03's v8 criterion and all other policies are retained.

No new agent behavior, weighting, feedback loop, live Calendar requests or runtime settings are added.

## Frozen focused suite

| Case | Authored expectation | Source |
|---|---|---|
| cal-08 | FAIL | Original saved SUT answer; copied without edits. |
| v9-conversion-correct | PASS | Authored correct Taipei conversion using the same controlled trace. |
| v9-no-conversion | PASS | Authored original Los Angeles interval without a conversion claim. |

The suite is `judge_policy_v9_cases.json`. Labels are withheld from the model prompt and pending Rachel's human review. This is development regression validation on a known defect and authored controls, not held-out accuracy. Freeze the source and rubric before running; preserve the first output for each example without retrying until labels match.

## Visible execution

Run pytest in the VS Code Terminal first. Then verify the existing LM Studio Thinking and budget settings and run:

```sh
JUDGE_MODEL=qwen/qwen3.5-9b LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1 .venv/bin/python -u -m harness.calendar_judge --thinking --input evals/judge_policy_v9_cases.json --max-tokens 6144 --timeout 600 --runtime-note "Thinking on; UI Reasoning Budget 1024; inspect observed tokens" --output reports/runs/judge-v9-conversion-validation-20261008.json
```

The runner records scores but does not automatically compare these non-calibration labels. Review criterion reasons as well as aggregate verdicts. Preserve raw bytes separately from assisted evidence notes. Source human-review status remains pending.

Suite SHA-256: `fe859aaef002db39ce0aa120a284a9781a26d92499e74f2e69aea5bacb88efc6`

Rubric SHA-256: `9d9203bd4f052323243fb35bca75b271092aad0b00a96ad37c5455e49b13b716`
