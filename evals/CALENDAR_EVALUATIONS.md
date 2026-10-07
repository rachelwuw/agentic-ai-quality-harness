# Calendar evaluation cases

These 15 cases evaluate the read-only Calendar Assistant, separately from the original QA prototype `cases.json`. Definitions and exact expected arguments are in `calendar_cases.json`. All cases start as **not_run**: creating this dataset is not a model evaluation result. Earlier smoke runs are documented in `../LIVE_CALENDAR_REVIEW.md` and do not count as executing this suite.

## Case inventory

| ID | Scenario | Expected answer | Execution mode |
| --- | --- | --- | --- |
| cal-01 | overlap_zh | Busy | controlled_and_live |
| cal-02 | overlap_en | Busy | controlled_and_live |
| cal-03 | adjacent_after | Free | controlled_and_live |
| cal-04 | adjacent_before | Free | controlled_and_live |
| cal-05 | contained_interval | Busy | controlled_and_live |
| cal-06 | cross_midnight | Free | controlled_and_live |
| cal-07 | winter_offset | Free | controlled_and_live |
| cal-08 | different_zone | Busy | controlled_and_live |
| cal-09 | missing_start_and_duration | Clarify / unknown | controlled |
| cal-10 | missing_duration | Clarify / unknown | controlled |
| cal-11 | missing_date | Clarify / unknown | controlled |
| cal-12 | ambiguous_timezone | Clarify / unknown | controlled |
| cal-13 | dst_gap | Clarify / unknown | controlled |
| cal-14 | dst_fold | Clarify / unknown | controlled |
| cal-15 | calendar_api_failure | Clarify / unknown | controlled |

## How to run and review

1. Use a fresh conversation for each case. Evaluate Python agent and LM Studio MCP separately; their loops and prompts differ.
2. For controlled runs, freeze the reference time at `2026-10-05T12:00:00-07:00`. Keep the real local model and use controlled Calendar responses for repeatability. Use the Calendar runner below; the existing prototype evaluator cannot consume this schema.
3. For live runs, verify the dedicated test calendar has the busy fixture and no other busy events in each requested interval. Relative-date cases are controlled only: LM Studio's real clock must not be mistaken for the frozen clock.
4. Compare tool name/arguments and the resulting API timestamps against the JSON expectations. The MCP adapter may omit `time_zone` when its default is America/Los_Angeles; normalize that default before comparison. JSON key order does not matter.
5. For DST gap/fold cases, either immediate clarification with no tool call, or one rejected local-time tool call followed by clarification, passes. Neither may reach Google. For all other missing-information cases, availability tools must not be called.
6. Review the whole final answer against every semantic criterion and forbidden behavior. A busy answer with a heading saying “free time” fails answer consistency. Do not grade only by keywords.
7. Record entry point, model/runtime, actual clock, prompt, tool arguments/results, final answer, pass/fail, and reason. Store runtime traces under ignored `reports/` and never include OAuth credentials.

`controlled_and_live` means the same case can be checked with a controlled Calendar adapter or real Calendar data. API failures are controlled only; do not alter credentials or permissions to provoke an outage. The assistant cannot create events in any case.

## Grading boundaries

These cases cover bilingual requests, conflict boundaries, cross-midnight dates, summer/winter offsets, another IANA zone, missing information, ambiguous abbreviations, DST gaps/folds, and API failure. They are a starter dataset, not proof of general scheduling reliability. Repeat runs and paraphrases should be added after the baseline. The Calendar-specific runner provides structural checks and a pending manual answer-review field; no LLM judge is used.


## Calendar runner

Run from the repository root:

```sh
.venv/bin/python -m harness.calendar_evaluate --ids cal-01 cal-03 cal-10 --output reports/calendar-evaluation-smoke.json
# Full baseline (15 real local-model cases):
.venv/bin/python -m harness.calendar_evaluate --output reports/calendar-evaluation.json
```

This uses the real LM Studio local model and controlled Calendar responses. It never connects to Google or changes events. It freezes the reference clock, begins a fresh agent conversation per case, checks exact tool arguments and resolved API intervals, and validates availability/unknown outcomes. Progress is saved after each case. Exit code 1 indicates structural failures; code 0 means only structural checks passed, never semantic approval.

Review each saved answer against `answer_review.criteria` and `forbidden_behaviors`; mark its review pass/fail and add notes in a copy of the report. The runner does not convert manual review into an automatic overall pass. LM Studio chat MCP and live Google integration remain separate manual checks. The JSON dataset retains `not_run` as a template; actual execution status belongs in each report.
