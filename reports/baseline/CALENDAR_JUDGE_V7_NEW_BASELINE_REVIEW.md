# Full v7 judge review of the new Calendar baseline

Run date: October 7, 2026 (America/Los_Angeles). The full review ran visibly in VS Code Terminal. Qwen3.5-9B scored saved gpt-oss-20b answers from the new controlled baseline. No Google calls, SUT regeneration, Calendar writes, quality retries, or in-run rubric edits occurred.

## Results and runtime

- Completed: 15/15; valid strict-schema outputs: 15/15.
- Raw judge verdicts: 11 PASS, 4 FAIL (cal-09, cal-13, cal-14, cal-15), 0 UNCERTAIN.
- Combined structural plus provisional judge status: 10 PASS_PROVISIONAL, 5 FAIL. cal-06 retains its first-call structural failure even though the corrected final answer is judge PASS.
- Total recorded generation time: 2800.511 seconds (46 minutes 40.511 seconds); mean 186.701 seconds per case; range 144.493–232.701 seconds. This excludes setup and the interrupted attempt.
- Observed reasoning: 15/15; 1009–1024 tokens. Thinking on, UI Reasoning Budget 1024, context 8192, full GPU offload, temperature 0, max output 6144, timeout 600 seconds. Requests were single-attempt.

## Separate assisted evidence review

These notes are Codex-assisted evidence review, not Rachel's human signoff and not an independent benchmark. Raw judge labels and outputs are unchanged. Source answer_review statuses remain pending. No semantic accuracy percentage is claimed. This development suite has influenced rubric tuning; comparison with old verdict counts also confounds changed SUT answers and rubric versions.

| Case | Raw judge | Combined status | Evidence review |
|---|---|---|---|
| cal-01 | PASS | PASS_PROVISIONAL | Availability supported. Language mismatch and omitted explicit scope are not covered by its current criteria; PASS is incomplete coverage. |
| cal-02 | PASS | PASS_PROVISIONAL | Judgment consistent with the recorded availability and scope. |
| cal-03 | PASS | PASS_PROVISIONAL | Adjacent slot correctly free. October Pacific Standard Time wording was missed; no explicit label criterion. |
| cal-04 | PASS | PASS_PROVISIONAL | Judgment consistent with the recorded availability and scope. |
| cal-05 | PASS | PASS_PROVISIONAL | Judgment consistent with the busy interval and daylight offset. |
| cal-06 | PASS | FAIL | Final answer supported after one format correction. Structural FAIL remains; successful recovery is not first-attempt correctness. |
| cal-07 | PASS | PASS_PROVISIONAL | Winter UTC-08 evidence supports the result. |
| cal-08 | PASS | PASS_PROVISIONAL | Correct busy/event times, but the false claim that the Los Angeles event times were converted to Taipei was missed. Current criteria focus on intervals and optional query conversion, leaving wording coverage incomplete. |
| cal-09 | FAIL | FAIL | c2 correctly catches missing read-only booking limitation. c1 passes despite offering duration alone as sufficient; duration without a start does not establish an interval and needs criterion review. |
| cal-10 | PASS | PASS_PROVISIONAL | Correctly accepts asking for missing duration/end without proposing a default. |
| cal-11 | PASS | PASS_PROVISIONAL | Correctly accepts asking for the date. |
| cal-12 | PASS | PASS_PROVISIONAL | Correctly accepts CST clarification before querying. |
| cal-13 | FAIL | FAIL | c6 correctly catches nonexistent/ambiguous conflation. c3 correctly recognizes internal validation and no Google request. |
| cal-14 | FAIL | FAIL | c6 correctly catches nonexistent wording. c3 is a false FAIL: internal tool validation rejected the DST time before Google access (api_calls is empty). c1 misses that AM/PM does not distinguish the two 01:15 AM occurrences; clarification must resolve the offset/fold. |
| cal-15 | FAIL | FAIL | c1 correctly catches omitted explanation of the Calendar read failure. The answer honestly avoids a free/busy claim, but honesty alone does not satisfy the full criterion. |

The cal-15 observation refines the earlier assisted note: the answer is honest about uncertainty but omits the required reason. The initial review was not a complete criterion-level signoff. Neither a schema-valid answer nor an aggregate FAIL proves every criterion is correct. cal-14 demonstrates a true failure with an additional false failure and a missed clarification defect.

## Interrupted configuration attempt

The first attempt used `reports/runs/calendar-judge-v7-new-baseline-20261007.json`. After CLI reloading, the reasoning budget was unrestricted. cal-01 returned PASS with 2591 reasoning tokens in 300.052 seconds. The visible Terminal was interrupted during cal-02 because runtime configuration differed from the intended experiment. Its raw last-saved state is `running`, not completed; preserve it with the separate local `JUDGE_V7_INTERRUPTED_RUNTIME_NOTE.md`. The full run restarted in a new file after the LM Studio UI showed Thinking on and budget 1024. Results from these configurations are not merged.

## Recommended next checkpoint

Keep the judge advisory. First confirm requirements for language, explicit dedicated-calendar scope and timezone-label truthfulness. Move facts already proven by the trace, such as whether an external Calendar request occurred, into deterministic grading and present those facts clearly to the judge. Review the known c1 clarification misses in cal-09 and cal-14. Freeze any revised rubric before evaluating new positive and negative examples that did not drive these edits. Do not rerun the same answers until the dashboard turns green.

## Preserved evidence

- [Raw v7 judge output](calendar-judge-v7-budget1024-new-baseline-20261007.json)
- [Controlled SUT source](calendar-baseline-v7-retry-20261007.json)
- [Separate SUT evidence review](CALENDAR_BASELINE_V7_RETRY_REVIEW.md)

Raw judge SHA-256: `176dd2b6fc4096438f709974757dc4e1923e5188172f5e5ee6de7de78550df96`

Source SHA-256: `309b12f696c4e18d37ea1b0d476671f5bf277a19a1541390294fca133a58d646`

Rubric SHA-256: `462aa2ce6238775080b8820c7a78032495fe125c609d020d757e06d89d2f45ca`

Judge prompt SHA-256: `93105abb586716dadbd05200d5047bdaf5a592782147edf8a3a2b9eb228a9269`
