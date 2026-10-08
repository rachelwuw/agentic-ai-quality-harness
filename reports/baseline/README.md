# Selected regression evidence

These selected artifacts contain controlled Calendar fixtures, not private Google event data. The SUT baseline uses a real local gpt-oss-20b model and simulated Calendar API results. The historical post-fix baseline passed 15/15 structural checks. The latest baseline passed 14/15 after one recovered format error. Semantic signoff remains pending; see the versioned reviews below.

`judge-calibration-v2.json` records the real local Qwen3.5-9B Q8_0 judge calibration: 3/4 agreement. It incorrectly passes cal-13, so the judge is NOT validated for autonomous quality signoff. This failed calibration is intentionally retained. Runtime: 8192 context, full GPU offload, LM Studio Reasoning Budget 0. See evals/CALENDAR_JUDGE.md for procedure and limitations.

Historical source_path entries describe the original execution; the source snapshot is now preserved alongside this report. Hashes verify identical bytes. Routine outputs belong in reports/runs/ and are ignored. Promote only reviewed, sanitized evidence to this directory.

- `judge-calibration-v3.json`: failed 12-example per-criterion calibration; 1/12 label agreement, 11 UNCERTAIN output errors. Includes four saved answers and eight authored synthetic variants. Preserve for regression debugging; not semantic signoff.

- `judge-calibration-v4.json`: strict structured output; 12/12 valid responses, 11/12 label agreement, one missed failure (`judge-gap-invalid-option`). Development calibration, not autonomous signoff.

- `judge-calibration-v5.json` and `judge-prompt-v5.txt`: consistency instruction correction; 12/12 valid outputs and label agreement on the tuned development set. Includes synthetic labels pending human review; not general accuracy or autonomous signoff.

- `calendar-judge-v5-full.json` and `CALENDAR_REVIEW_V5.md`: full saved 15-answer judge review plus separate Codex-assisted evidence notes. Raw 11 PASS / 4 FAIL; suspected judge mistakes and pending human review mean this is not release signoff.

- [JUDGE_REASONING_COMPARISON.md](JUDGE_REASONING_COMPARISON.md) and `judge-reasoning-1024/`: matched native off/on experiment with four development cases and six frozen synthetic cases. Observed reasoning in every on response; new-set usable label agreement 5/6 in both arms, with different format/schema errors and higher on latency. Raw evidence and hashes are preserved; no human signoff or independent benchmark claim.

[Structured-output Thinking validation](JUDGE_STRUCTURED_THINKING_VALIDATION.md) retains the single-attempt six-case results and links Rachel's separate expected-label confirmation.

[Full 15-answer Thinking review](CALENDAR_THINKING_REVIEW_V5.md): all outputs valid and reasoning observed, raw 10 PASS / 5 FAIL, with persistent and newly observed criterion errors. Answer review remains pending. Old v5 results are preserved.

## Latest policy validation

- [v6 focused validation](JUDGE_POLICY_V6_VALIDATION.md): four authored synthetic examples matched expectations; not held-out accuracy.
- [v6 original-answer review](JUDGE_V6_ORIGINAL_CASE_REVIEW.md): cal-08 retained an incorrect FAIL with contradictory reasoning; cal-10 correctly failed the confirmed duration policy.
- [v7 interval validation](JUDGE_POLICY_V7_VALIDATION.md): the unchanged original cal-08 and two authored positive/negative examples matched 3/3 expectations after criteria splitting and explicit reference facts. Raw files are linked from each report. Prior false failures remain preserved.

These focused results are separate from the full 15-case baseline. They do not validate the latest SUT prompt or retry behavior through real model runs. Human answer review remains separate from assisted evidence analysis.

[Latest controlled SUT baseline](CALENDAR_BASELINE_V7_RETRY_REVIEW.md): 15 completed, 14/15 strict structural passes; cal-06 recovered after one format correction. Assisted review records language, scope, time-zone wording and DST findings. This is separate from live Google regression. Its full v7 judge review is linked below.

[Full v7 review of the latest baseline](CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md): 15 valid outputs, raw 11 PASS / 4 FAIL, combined 10 provisional passes / 5 failures. Known coverage gaps, criterion errors and missed clarification defects remain. Thinking budget verified at 1009–1024 observed tokens; generation time about 46m41s. Human answer review remains pending.

[v8 timezone validation](JUDGE_POLICY_V8_VALIDATION.md): four synthetic wording variants matched authored expectations in one attempt each; 4 valid outputs, observed Thinking budget 1024, about 11m11s. This is focused development validation, not held-out accuracy or human signoff.

[v8 original-case review](JUDGE_V8_ORIGINAL_CASE_REVIEW.md): cal-03 correctly FAIL; cal-08 remains a false PASS under the conversion criterion. Both raw outputs are preserved; this is focused development evidence, not general accuracy.

[v9 conversion validation](JUDGE_POLICY_V9_VALIDATION.md): the original cal-08 false conversion now FAILs; correctly converted and no-conversion controls PASS. Three valid outputs, about 9m36s. Targeted development validation only; source human review remains pending.

[v9 new-wording review](JUDGE_V9_NEW_WORDING_REVIEW.md): unchanged rubric, four valid outputs, 3/4 authored aggregate matches; contradictory Chinese claim missed and criterion-level errors retained. Not overall accuracy or human signoff.

[v9 criterion comparison](JUDGE_V9_CRITERION_COMPARISON.md): 36 authored labels; batch 31/36. Four selected errors scored separately: 3/4 match, one contradiction miss persists. Failure-selected diagnostic, not overall accuracy.

[v10 Python facts comparison](JUDGE_V10_TRACE_FACTS_REVIEW.md): 108 pytest tests passed; two known-negative single checks scored FAIL/FAIL as expected, including one prior miss. Same model/budget. Two positive controls subsequently passed all nine checks each; broader validation pending.

[v10 positive-control review](JUDGE_V10_POSITIVE_CONTROLS_REVIEW.md): two reused correct answers PASS on all nine checks each, valid JSON, observed reasoning tokens 1024 each; about 4m57s. No new false failures in these attempts; general reliability remains unverified.

[Frozen v10 fresh-case review](JUDGE_V10_FRESH_REVIEW.md): four new authored cases, 3/4 aggregate and 31/36 criterion matches to pre-run expectations. One correct winter answer falsely failed; label/reason contradiction and criterion-scope overlap preserved. About 13m20s; Judge remains advisory.
