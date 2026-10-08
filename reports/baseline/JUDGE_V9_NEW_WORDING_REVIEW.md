# Frozen v9 new-wording review — October 8, 2026

Four valid single-attempt outputs completed under the unchanged v9 rubric. Aggregate labels matched 3 of 4 authored expectations. One false PASS remains: v9-new-04. Of the two authored FAIL examples, one was detected and one was missed; both authored PASS examples passed. This small development sample does not establish an accuracy rate for deployment.

## Results

| Case | Authored expectation | Raw verdict | Seconds | Reasoning tokens |
|---|---|---|---|---|
| v9-new-01 | PASS | PASS | 173.088 | 1024 |
| v9-new-02 | FAIL | FAIL | 275.985 | 1024 |
| v9-new-03 | PASS | PASS | 190.24 | 1024 |
| v9-new-04 | FAIL | PASS | 246.573 | 1024 |

Total recorded generation time: 885.886 seconds (about 14 minutes 46 seconds). Commands were submitted through the VS Code Terminal UI. Qwen3.5-9B was already loaded; Thinking was requested and every response reported 1024 reasoning tokens. Existing runtime settings were retained. Strict JSON, temperature 0, maximum output 6144 and timeout 600 seconds were used. No SUT generations, live Google requests, automatic retries or in-run rubric revisions occurred.

An initial UI dispatch was interrupted by a window-state change before a new output file existed. The command was subsequently submitted through the Terminal; no extra model attempt or quality retry is included. UI observations were intermittently stale; persisted run evidence verified completion.

## Assisted evidence review

- **v9-new-01:** PASS matches the authored expectation. The Chinese answer correctly supplies both source Los Angeles and target Taipei intervals.
- **v9-new-02:** Aggregate FAIL matches the authored expectation because the converted event date is wrong. However, individual grading is unreliable: c4 falsely FAILs despite the requested query interval being preserved; it confuses the event interval with the query interval. c6 is labelled FAIL even though its own lengthy reason concludes that checking only the test calendar should PASS. c8 also imports date arithmetic into a target-timezone consistency check even though the answer displays Asia/Taipei; c9 is the appropriate check for the incorrect converted date. Preserve these flaws rather than treating the correct aggregate as full criterion-level success.
- **v9-new-03:** PASS matches the authored expectation. The answer explicitly denies converting the displayed original event interval and keeps valid UTC-07 Los Angeles time.
- **v9-new-04:** False PASS. After the correct Taipei interval, the answer adds `不過台北的活動時間也可以寫成 10 月 7 日 11:00–11:30 Asia/Taipei。` This is a contradictory incorrect event interval. c2 and c9 should reject the incorrect claim; the Judge instead cites the earlier correct interval and ignores the later contradiction. No raw verdict is overridden.

## Limits and next step

These four answers were authored after v9 was frozen, but reuse the known cal-08 dates and controlled trace. This validates new wording only; it is not independent benchmarking, new-date generalization or new SUT behavior. Expected labels were withheld from the Judge. Criteria order matches original cal-08. Labels and source answer reviews remain pending Rachel's human review. This document is Codex-assisted evidence review, not human signoff.

The Judge should remain advisory. Before adding more rubric complexity, establish criterion-level expected labels and calibration evidence for the observed contradiction, scope and query/event confusion failures. Any later prompt or model-setting experiment should be a separate frozen version with retained raw results and independent validation. Do not tune this suite and then report it as untouched validation. No further model experiments, product features or weighted scoring were added in this run.

## Evidence

- [Raw output](judge-v9-new-wording-20261008.json)
- [Frozen new-wording inputs](../../evals/judge_v9_new_wording_cases.json)
- [Pre-run plan](../../evals/JUDGE_V9_NEW_WORDING_VALIDATION.md)
- [Earlier v9 targeted validation](JUDGE_POLICY_V9_VALIDATION.md)

Suite SHA-256: `261cbd9427d2c06641c5982bfe5ad62289491f233ce9c6ddba19d7af74ffca61`

Unchanged rubric SHA-256: `9d9203bd4f052323243fb35bca75b271092aad0b00a96ad37c5455e49b13b716`

Raw output SHA-256: `b09c763e815e81af717e89b05cdb02b606278a21b67043879455dafa14e3e8fc`
