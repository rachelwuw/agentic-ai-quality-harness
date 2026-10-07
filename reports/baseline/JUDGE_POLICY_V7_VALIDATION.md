# Calendar judge v7 interval validation

The v6 composite cal-08 criterion was split into busy status, event interval, optional query conversion, and preservation of the requested interval. Explicit reference facts state the overlap. Both rubric wording and reference facts changed; this run does not isolate which change caused improvement.

Original cal-08 plus two authored positive/negative examples were reviewed once locally, with Thinking requested, temperature 0, strict JSON schema, max tokens 6144 and timeout 600 seconds. No new SUT or Google execution occurred.

| Case | Evidence-review expectation | Judge | Seconds | Reasoning tokens |
|---|---|---|---:|---:|
| cal-08 | PASS | PASS | 137.704 | 1021 |
| v7-query-event-correct | PASS | PASS | 183.79 | 1024 |
| v7-event-wrong | FAIL | FAIL | 196.448 | 1024 |

All three outputs validated and matched the expectations, with observed reasoning. The original cal-08 now passes with consistent reasons; the incorrect event interval fails c2. Total inference time: 517.942 seconds. No automatic retries occurred. 82 deterministic pytest tests passed in the visible VS Code Terminal before the model run.

This is Codex-assisted evidence review, not Rachel's individual answer signoff. Original source review statuses remain pending. These are development examples, not held-out accuracy. The source answer, v6 false FAIL and raw judge output are preserved. The updated SUT prompt still requires separate evaluation.

Raw output: [judge-policy-v7-20261007.json](judge-policy-v7-20261007.json)

Raw SHA-256: `b178f0209e6a1cb415888096044d6312ed5645ba2c8231e2cd2c53cfcafa3383`
