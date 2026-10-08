# v8 review of original cal-03 and cal-08 answers — October 8, 2026

Two saved gpt-oss-20b answers were re-scored once in the visible VS Code Terminal using Qwen3.5-9B, Thinking enabled, UI Reasoning Budget 1024, temperature 0, strict JSON, maximum output 6144 and timeout 600 seconds. No new SUT generations, live Google requests, automatic retries or rubric edits occurred during the run.

## Results

Both outputs were valid. Total recorded generation time: 297.555 seconds (about 4 minutes 58 seconds).

| Case | Previous v7 verdict | Raw v8 verdict | Seconds | Observed reasoning tokens |
|---|---|---|---|---|
| cal-03 | PASS | FAIL | 113.208 | 1024 |
| cal-08 | PASS | PASS | 184.347 | 1022 |

## Assisted evidence review

- **cal-03:** v8 c4 correctly fails the phrase `美國太平洋標準時`. October 6 Los Angeles uses PDT (UTC-07), consistent with the saved tool arguments. The availability conclusion itself remains supported. The previous v7 PASS is preserved unchanged.
- **cal-08:** v8 c7 still passes the original line `Busy event(s): 2026‑10‑06 11:00–11:30 America/Los_Angeles (converted to the requested timezone)`. The requested timezone is Asia/Taipei. The parenthetical claims a conversion but the displayed event remains in Los Angeles time; a Taipei conversion would be October 7, 02:00–02:30. This violates the added criterion. The Judge explicitly acknowledges the parenthetical but excuses it because the Los Angeles interval matches the tool evidence. That is a missed violation, not evidence that the answer is correct. Raw PASS is retained.

The four [synthetic wording controls](JUDGE_POLICY_V8_VALIDATION.md) matched their authored expectations, but this original-answer check exposed a remaining false PASS. These two examples were known development cases involved in rubric design, not held-out accuracy measurement. All checks in this two-case run were semantic LLM checks; deterministic external-request grading is covered separately by tests.

These notes are Codex-assisted evidence review, not Rachel's human signoff or an independent benchmark. Source answer-review statuses remain pending. No final 15-case v8 baseline or release signoff is implied.

## Evidence

- [Unchanged raw v8 output](judge-v8-cal03-cal08-20261008.json)
- [Original SUT source](calendar-baseline-v7-retry-20261007.json)
- [Previous v7 output](calendar-judge-v7-budget1024-new-baseline-20261007.json)
- [v8 rubric](../../evals/calendar_judge_rubric.json)

Source SHA-256: `309b12f696c4e18d37ea1b0d476671f5bf277a19a1541390294fca133a58d646`

Rubric SHA-256: `846999cbc41c6ad0178d5b04929d8d4fadccda8437b157ce04f8fb2a8345e78c`

Raw v8 output SHA-256: `db5598688e0b4b39c2339a29b3bd8db36cedace77c7e94c76fb0936cfde34b97`

## Recommended next step

Retain this checkpoint and address cal-08's remaining criterion interpretation before treating the Judge as reliable. Keep the original answer as a regression example, use separate checks for a conversion claim and its displayed converted date/time, and preserve both positive controls and this failed detection. Weighted scoring and automatic SUT feedback remain deferred.
