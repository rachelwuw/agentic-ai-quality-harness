# v8 timezone judge validation — October 8, 2026

Executed in the visible VS Code Terminal on the M5 MacBook Air. Qwen3.5-9B was loaded in LM Studio with Thinking enabled and the Reasoning Budget checkbox at 1024, verified in the UI before execution. Strict JSON output, temperature 0, maximum output 6144 and timeout 600 seconds were used. No Google API calls, new SUT generations, automatic retries, or in-run rubric changes occurred.

## Results

All four single-attempt outputs were valid and matched the frozen authored expectations. Raw verdicts: 2 PASS / 2 FAIL / 0 UNCERTAIN. Every response reported 1024 reasoning tokens. Total recorded generation time: 670.738 seconds (approximately 11 minutes 11 seconds).

| Case | Authored expectation | Raw verdict | Seconds | Reasoning tokens |
|---|---|---|---:|---:|
| v8-conversion-correct | PASS | PASS | 150.584 | 1024 |
| v8-conversion-wrong | FAIL | FAIL | 149.541 | 1024 |
| v8-daylight-correct | PASS | PASS | 179.176 | 1024 |
| v8-daylight-wrong | FAIL | FAIL | 191.437 | 1024 |

## Assisted evidence review

- Correct Taipei conversion passed: October 6, 11:00–11:30 Los Angeles PDT maps to October 7, 02:00–02:30 Taipei.
- Incorrect conversion failed c5: it retained the Los Angeles date and time while claiming conversion to Taipei; the reason explicitly identifies the required 15-hour shift.
- Correct PDT wording passed without requiring the optional query-window conversion.
- Incorrect PST wording failed c5: October Los Angeles uses PDT/UTC-07, matching the tool evidence. The criterion explanation identifies the actual label defect.

The checks and cited evidence support these narrow outcomes. These are Codex-assisted notes, not Rachel's human signoff. Expected labels remain authored expectations pending human review. The examples are synthetic wording variants built from an existing controlled trace and reflect issues that motivated v8; this is focused development validation, not independent held-out accuracy, a new SUT baseline, or proof of general Judge reliability.

None of these four cases contains a no-external-request requirement, so this model run does not validate that trace grader. Its behavior was covered separately by the previously recorded 101 deterministic tests. cal-09/cal-14 clarification defects, language/scope coverage and broader Judge errors remain open. Source answer_review statuses remain pending; raw Judge labels and outputs are preserved unchanged.

## Execution integrity

The initial command was mistakenly pasted into the VS Code rubric editor without executing. Both the inserted newline and pasted text were undone; the editor returned to an unmodified saved buffer. The on-disk rubric hash matched the frozen hash before the actual Terminal execution. No result file existed for that failed UI attempt. Terminal focus was then explicitly selected and the command executed once. This was input correction, not a quality retry.

## Evidence

- [Raw judge output](judge-v8-timezone-validation-20261008.json)
- [Frozen cases](../../evals/judge_policy_v8_cases.json)
- [v8 plan and trace-grading design](../../evals/JUDGE_V8_VALIDATION.md)

Raw output SHA-256: `13ab43150f39dcc64e47306fcfa85882f5d933f9cf47685c78220ec03364d5af`

Source SHA-256: `7674f3052bc836fd304bdc716b528a6b4cb85c9804e8a777b8b2c629e7afc7db`

Rubric SHA-256: `846999cbc41c6ad0178d5b04929d8d4fadccda8437b157ce04f8fb2a8345e78c`

Next: apply the frozen v8 rubric to saved cal-03 and cal-08 responses to verify that the actual known wording issues are detected, without regenerating or rewriting those answers. Verify cal-14 external-request facts separately through deterministic grading. Keep the Judge advisory and retain targeted human review.
