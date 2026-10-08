# Calendar SUT baseline after prompt and retry changes

Run date: October 7, 2026. Executed visibly in VS Code Terminal on code checkpoint 3b97db3 with documentation edits pending. Real local gpt-oss-20b was loaded with context 8192 and full GPU offload. The controlled runner freezes reference time at October 5, 2026, 12:00 America/Los_Angeles. No Google access or Calendar writes occurred.

All 15 conversations completed. Existing strict structural checks passed 14/15. cal-06 initially emitted an invalid end timestamp, corrected it once using tool feedback, then queried the expected interval and returned a supported answer. Its raw structural FAIL is preserved. The correction succeeded within the policy, while the grader still measures exact first-call behavior; recovery and first-attempt correctness must be reported separately.

## Assisted evidence review

These are Codex-assisted notes, not Rachel's human signoff or LLM-judge scores. Source answer_review statuses remain pending. A structural PASS does not imply a correct final answer. No overall semantic pass rate is asserted.

| Case | Raw structure | Review observation |
|---|---|---|
| cal-01 | PASS | Availability and event interval correct; answers a Chinese prompt in English and omits explicit dedicated-calendar scope. |
| cal-02 | PASS | Availability, overlap and test-calendar scope supported. |
| cal-03 | PASS | Availability correct; calls October Los Angeles time Pacific Standard Time, but the actual query correctly uses UTC-07. |
| cal-04 | PASS | Availability, interval and test-calendar scope supported. |
| cal-05 | PASS | Availability and UTC-07 daylight time wording supported. |
| cal-06 | FAIL | First end timestamp malformed; one correction succeeded and final answer is supported. Existing strict grader counts the first bad call, preserving structural FAIL. This is observed recovery, not 15/15 first-attempt success. |
| cal-07 | PASS | Availability and winter standard-time wording supported. |
| cal-08 | PASS | Busy conclusion and event interval correct, but claims the displayed Los Angeles event times were converted to the requested Taipei zone; they were not. |
| cal-09 | PASS | Requests missing information, but does not explain read-only booking limitation. Duration alone cannot establish a start time. Examples are not a confirmed default duration. |
| cal-10 | PASS | Asks for end time or duration without proposing a default; matches the confirmed policy. |
| cal-11 | PASS | Asks for date; no availability claim. |
| cal-12 | PASS | Asks which CST timezone is intended; no availability claim. |
| cal-13 | PASS | Requests clarification but still conflates a nonexistent spring-forward time with an ambiguous time. |
| cal-14 | PASS | Conflates nonexistent and duplicated fall-back time. Suggesting AM versus PM does not distinguish the two 01:15 AM occurrences; introduces unsupported alternatives. |
| cal-15 | PASS | Honestly reports inability to determine availability after controlled API failure. |

All recorded model requests succeeded on their first transport attempt. This run observed one argument correction, but did not exercise real transport retries. Controlled Calendar API failure is separate from a live network error. Existing DST findings remain important even though those cases avoid actual Calendar API access.

Next: score these saved answers with v7 as provisional evidence and inspect the known language, scope, timezone-label and DST issues. Define first-attempt and recovered-success metrics before changing the grader; do not overwrite or relabel this raw baseline. Retain targeted human review and add unseen judge validation examples before making reliability claims.

Raw controlled trace: [calendar-baseline-v7-retry-20261007.json](calendar-baseline-v7-retry-20261007.json)

Raw SHA-256: `309b12f696c4e18d37ea1b0d476671f5bf277a19a1541390294fca133a58d646`

Evaluation definition SHA-256: `c0f8ebe2d5d9c82912803cdc01069f6ad4d8fec38a5a59e7ed93bb2bcc7d8bee`

## Subsequent v7 judge review

The [full v7 review](CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md) completed with 11 raw PASS / 4 FAIL. It also exposed a stricter cal-15 finding: the answer does not explicitly explain that the Calendar read failed, although it honestly avoids an availability claim. The assisted observations above were not criterion-level human signoff. Raw source answers and pending review statuses remain unchanged.
