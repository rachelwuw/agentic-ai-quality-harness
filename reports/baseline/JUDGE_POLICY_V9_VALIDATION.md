# Judge v9 event-conversion validation — October 8, 2026

Three single-attempt outputs were valid and matched authored expectations: FAIL / PASS / PASS. Total recorded generation time was 575.923 seconds (approximately 9 minutes 36 seconds). Pytest completed with 101 tests passing in 3.40 seconds.

## Runtime and scope

Commands were submitted through the VS Code Terminal UI. Qwen3.5-9B was already loaded in LM Studio. Thinking was requested, with the existing 1024 UI budget retained from v8; responses reported 1019–1024 reasoning tokens. Temperature 0, strict JSON output, maximum output 6144 and timeout 600 seconds were used. No CLI reload or runtime setting changes occurred. No new SUT generations, live Google requests, automatic retries or in-run rubric changes occurred.

The screen tool's snapshots remained on the older Terminal view during execution; command execution and completion were additionally verified from the newly written pytest output and run report. Do not infer that every intermediate result was captured visually.

| Case | Authored expectation | Raw verdict | Seconds | Observed reasoning tokens |
|---|---|---|---|---|
| cal-08 | FAIL | FAIL | 158.981 | 1019 |
| v9-conversion-correct | PASS | PASS | 214.183 | 1024 |
| v9-no-conversion | PASS | PASS | 202.759 | 1024 |

## Assisted evidence review

- **Original cal-08:** c8 and c9 correctly fail. The parenthetical claims conversion to Asia/Taipei while the event still displays October 6, 11:00–11:30 America/Los_Angeles. Its Taipei equivalent is October 7, 02:00–02:30. The original answer and tool trace were copied unchanged. Previous [v8 false PASS](JUDGE_V8_ORIGINAL_CASE_REVIEW.md) and raw output remain preserved.
- **Correct conversion control:** PASS correctly permits the equivalent Taipei event interval and confirms the claimed conversion matches the displayed target timezone, date and time.
- **No-conversion control:** PASS correctly permits an original Los Angeles event interval with no conversion claim; optional conversion is not required.

Some evidence strings in the no-conversion control quote rubric instructions rather than answer excerpts (c3 and c7). The final verdicts align with the answer, but this evidence-quality limitation is retained in raw output and should be checked in later validation.

## Limits

These are a known development failure and two authored positive controls on an existing controlled trace, not held-out accuracy. Expected labels remain authored expectations pending Rachel's human review and are withheld from the model prompt. These notes are Codex-assisted evidence review, not human signoff or an independent benchmark. All three cases use semantic LLM checks, not the separate deterministic external-request grader.

The original case obtains conversion checks from rubric additions after forbidden-behavior checks (c8/c9), whereas authored controls include them in their source criteria before forbidden checks (c6/c7). Requirements are equivalent but ordering differs, so this run is not a controlled test of criterion-order effects. No ordering changes were made after execution began.

This validates the targeted fix once; no stability estimate, full 15-case v9 baseline, SUT behavior fix or release gate is established. Weighted scores and feedback loops remain deferred.

## Evidence

- [Preserved raw output](judge-v9-conversion-validation-20261008.json)
- [Frozen focused inputs](../../evals/judge_policy_v9_cases.json)
- [Current v9 rubric](../../evals/calendar_judge_rubric.json)
- [Archived v8 rubric](../../evals/calendar_judge_rubric_v8.json)
- [Validation plan](../../evals/JUDGE_V9_VALIDATION.md)

Source SHA-256: `fe859aaef002db39ce0aa120a284a9781a26d92499e74f2e69aea5bacb88efc6`

Rubric SHA-256: `9d9203bd4f052323243fb35bca75b271092aad0b00a96ad37c5455e49b13b716`

Raw output SHA-256: `219da740422bcafb22a8b200607a52341a2f798d1996d8c68eb7d4e12e00df3a`

## Recommended next step

Review and preserve this development checkpoint. Before adding more product scope, validate frozen criteria on new examples that were not used to tune them, including evidence quality and false PASS/FAIL rates. Retain current known SUT defects separately from Judge quality.
