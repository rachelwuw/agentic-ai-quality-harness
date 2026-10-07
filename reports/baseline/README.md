# Selected regression evidence

These selected artifacts contain controlled Calendar fixtures, not private Google event data. The SUT baseline uses a real local gpt-oss-20b model and simulated Calendar API results. All 15 structural checks passed; semantic signoff remains pending, with known failures in cal-13 and cal-14.

`judge-calibration-v2.json` records the real local Qwen3.5-9B Q8_0 judge calibration: 3/4 agreement. It incorrectly passes cal-13, so the judge is NOT validated for autonomous quality signoff. This failed calibration is intentionally retained. Runtime: 8192 context, full GPU offload, LM Studio Reasoning Budget 0. See evals/CALENDAR_JUDGE.md for procedure and limitations.

Historical source_path entries describe the original execution; the source snapshot is now preserved alongside this report. Hashes verify identical bytes. Routine outputs belong in reports/runs/ and are ignored. Promote only reviewed, sanitized evidence to this directory.

- `judge-calibration-v3.json`: failed 12-example per-criterion calibration; 1/12 label agreement, 11 UNCERTAIN output errors. Includes four saved answers and eight authored synthetic variants. Preserve for regression debugging; not semantic signoff.

- `judge-calibration-v4.json`: strict structured output; 12/12 valid responses, 11/12 label agreement, one missed failure (`judge-gap-invalid-option`). Development calibration, not autonomous signoff.

- `judge-calibration-v5.json` and `judge-prompt-v5.txt`: consistency instruction correction; 12/12 valid outputs and label agreement on the tuned development set. Includes synthetic labels pending human review; not general accuracy or autonomous signoff.

- `calendar-judge-v5-full.json` and `CALENDAR_REVIEW_V5.md`: full saved 15-answer judge review plus separate Codex-assisted evidence notes. Raw 11 PASS / 4 FAIL; suspected judge mistakes and pending human review mean this is not release signoff.

- [JUDGE_REASONING_COMPARISON.md](JUDGE_REASONING_COMPARISON.md) and `judge-reasoning-1024/`: matched native off/on experiment with four development cases and six frozen synthetic cases. Observed reasoning in every on response; new-set usable label agreement 5/6 in both arms, with different format/schema errors and higher on latency. Raw evidence and hashes are preserved; no human signoff or independent benchmark claim.

[Structured-output Thinking validation](JUDGE_STRUCTURED_THINKING_VALIDATION.md) retains the single-attempt six-case results and links Rachel's separate expected-label confirmation.
