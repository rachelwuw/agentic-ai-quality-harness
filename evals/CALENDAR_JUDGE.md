# Local Calendar answer judge

The judge reads existing saved answers, tool observations, API-call evidence and criteria. It has no Calendar tools, Google credentials or agent loop. SUT and judge identifiers must differ. Source traces and pending human reviews are not modified. Judge errors and malformed/truncated responses become UNCERTAIN, never PASS. No automatic retry or rerun-until-pass.

Use LM Studio to unload the SUT, then load the judge with an 8192-token context. Model weights remain outside Git. Run from the repository root in the recreated Python environment:

```sh
export SUT_MODEL=openai/gpt-oss-20b
export JUDGE_MODEL=qwen/qwen3.5-9b
export LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
python -m harness.calendar_judge --input evals/judge_calibration_cases.json --calibrate --output reports/runs/judge-calibration-v5.json
```

The current calibration has 12 labeled examples: four previously reviewed saved answers (cal-01/cal-03 PASS, cal-13/cal-14 FAIL) and eight authored synthetic variants. Labels apply only to the exact calibration input, verified by SHA-256. Synthetic labels await human review. This development calibration is not an accuracy benchmark. The rubric supplies precise DST facts because the current tool error groups nonexistent and ambiguous times. Expected labels are never sent to the model.

After calibration succeeds, omit `--calibrate` to review all saved cases. Inspect FAIL and UNCERTAIN and sample PASS. PASS_PROVISIONAL means both structural checks and judge review passed; it is not human signoff. The CLI exit code indicates judge execution/calibration health, not that every SUT answer passed. Reports include raw judge output, source/rubric hashes, model identifiers and requested generation settings. Thinking-disabled behavior must be verified in runtime output; the request alone does not guarantee it.

Routine judge outputs go to ignored `reports/runs/`. Selected reviewed, sanitized baselines can be promoted later under the migration plan. Do not copy virtual environments or OAuth tokens to the Mac Studio. Reinstall dependencies/runtime, download models and authenticate Google again. The standalone judge does not need Google authentication.

## Migration direction

Keep source/tests/evals/docs/project dependency files in Git. Exclude virtual environments, caches, weights, secrets and routine runs. Separate selected regression baselines from runs. Keep runtime endpoint and both model roles configurable. Add complete reproducible dependencies and expand doctor to check Python dependencies, runtime connectivity, both model availability and read-only Google connectivity. These remaining migration changes do not expand the Calendar product scope.

Runtime note: the first attempt timed out on cal-01 with unrestricted reasoning. In LM Studio Developer → model Inference → Reasoning, enable Reasoning Budget and set it to 0 for this judge. The OpenAI-compatible request parameter alone did not disable reasoning here. Preserve this runtime setting when migrating, or expect different latency/behavior. A single JSON Markdown fence is accepted; additional prose and invalid schemas remain errors.

Calibration history: after the parser/runtime corrections, v1 matched 3/4 labels and missed cal-13. The v2 prompt explicitly checks every suggested time and contradictions throughout the answer. Versioned run outputs preserve earlier failures; this is a prompt correction, not retry-until-pass.

Previous result: v2 calibration completed with 3/4 agreement; cal-13 was incorrectly judged PASS. Do not use this judge as autonomous signoff or run the full suite as an accepted semantic baseline yet. Selected controlled source and failed judge calibration are preserved in reports/baseline/ for clean-machine reproduction. Routine run outputs remain ignored. Human review remains pending in original traces.

## Criterion review v3

The model returns one judgment per requirement with a reason and evidence. Python requires exactly the expected IDs (no missing, duplicate or extra checks), then computes FAIL if any check fails; otherwise UNCERTAIN if any check is uncertain; otherwise PASS. Invalid output is UNCERTAIN. An observed tool/API failure is graded separately from the truthfulness of the answer about that failure.

The 12-example suite `evals/judge_calibration_cases.json` includes four previously human-reviewed saved SUT answers and eight authored synthetic answer variants. Synthetic variants are NOT new SUT runs and their author-defined labels await Rachel's review. They retain controlled tool evidence, with stale assistant messages removed. Expected labels and label provenance are not sent to the judge. Correct gap/fold answers are included to catch false failures; incorrect time alternatives, fabricated API success and an instruction-injection answer test missed failures. These examples are development calibration, not a held-out benchmark or evidence of general accuracy. `--ids` supports focused runs; partial calibration results are not full-suite calibration.

For full saved SUT review after calibration, use the controlled baseline as `--input` without `--calibrate`. The calibration SHA-256 guard only accepts the authored calibration source. Those historical calibration runs used Qwen with Reasoning Budget 0. Preserve all versioned results rather than rerunning until success.

## Observed v3 result

The visible local run on 2026-10-06 completed all 12 examples: 1 PASS, 0 FAIL, 11 UNCERTAIN; agreement with authored/reviewed labels was 1/12. Only `judge-api-error-honest` produced a valid matching judgment. Nine responses failed JSON decoding and two failed schema validation. These are judge output failures, not proof that the SUT answers failed. The run does not establish whether cal-13 missed-failure behavior improved. Preserve the raw output in `reports/baseline/judge-calibration-v3.json`. No automatic retries were used and the full 15-answer judge review was not run. Next fix output reliability (constrained JSON output or smaller per-criterion requests) before evaluating semantic accuracy. Do not repair malformed responses into PASS or use this judge for autonomous signoff.

## Structured output v4 result

The request now supplies a strict JSON Schema for the criterion array, permitted IDs/verdicts, exact count, required fields and nonempty string evidence. Python still rejects missing/duplicate IDs, malformed evidence, truncation and tool calls. Unsupported schema requests fail as UNCERTAIN; there is no unconstrained fallback or automatic retry. No new dependency was added.

The visible local v4 run completed 12/12 with valid output: 7 PASS, 5 FAIL, 0 UNCERTAIN. Agreement with calibration labels: 11/12 (development examples, not general accuracy). The four previously reviewed SUT answers all matched, including cal-13/cal-14 FAIL. The authored `judge-gap-invalid-option` was incorrectly passed: criterion c7 acknowledges that the proposed same-day 02:15 is invalid but marks PASS anyway. Thus structured output solved observed formatting failures, not semantic reliability. Keep human review and do not use the judge for autonomous signoff. The eight authored labels still await Rachel's review. No full 15-answer judge run was performed.

Evidence: `reports/baseline/judge-calibration-v4.json`. Previous v3 failures remain preserved. Deterministic checks: 77 passed in the visible terminal. Next inspect the c7 reasoning/verdict contradiction and validate any correction against both positive and negative cases, keeping this run unchanged.

## Consistency instructions v5 result

The prompt now explicitly treats requests to confirm an impossible option as offering that option, distinguishes rejection from suggestions, and requires each verdict to agree with its own reason/evidence. Calibration examples, expected labels, strict schema and parsing rules were unchanged. There is no keyword-based semantic override or automatic retry.

The visible local v5 run completed all 12 cases with valid outputs and 12/12 agreement: 6 PASS, 6 FAIL, 0 UNCERTAIN. The previous missed case `judge-gap-invalid-option` now fails c7 with evidence of the invalid same-day 02:15 option. Correct gap/fold answers still pass. This is development-set performance after prompt tuning, not held-out accuracy or autonomous signoff. Eight authored labels remain pending Rachel's review. Deterministic tests: 77 passed. The full 15-answer judge review has not run yet.

Preserved evidence: `reports/baseline/judge-calibration-v5.json` and `reports/baseline/judge-prompt-v5.txt`. Prior results remain unchanged. Next apply the calibrated judge to the saved 15-case SUT baseline as provisional review, inspect FAIL/UNCERTAIN and sample PASS, and later add unseen calibration examples before judging general reliability.

## Full saved-answer review v5

The visible 15-case run completed: 11 raw PASS, 4 raw FAIL, 0 UNCERTAIN, all outputs valid. This is not 11 confirmed passes: assisted review identifies suspected false FAIL cal-08 and missed FAIL cal-09; cal-10's reason is inaccurate about confirmation and duration policy needs review. cal-13/cal-14 known failures were caught. cal-02 scope wording needs review. Human signoff remains pending. See `reports/baseline/CALENDAR_REVIEW_V5.md` for the queue, answers, API parameters and reasons; raw scores remain unchanged in `calendar-judge-v5-full.json`. No new SUT run, automatic retries or Google calls were performed.

## Reasoning comparison

The current saved Thinking experiment preset uses a 1024-token budget. [Comparison results](../reports/baseline/JUDGE_REASONING_COMPARISON.md) retain the historical budget=0 evidence and compare explicit native off/on requests using an unchanged v5 prompt/rubric. This is a separate prompt-JSON experiment; the default OpenAI-compatible path continues to request strict JSON schema. No silent fallback or repair occurs.

Set `JUDGE_MODEL` to the loaded judge identifier and `LM_STUDIO_BASE_URL` to the configurable local `/v1` endpoint. In LM Studio, enable Thinking and set Reasoning Budget 1024 before testing the on arm. Always verify returned reasoning tokens; the requested setting alone is insufficient. Use a new output path for each recorded run.

```sh
python -m harness.calendar_judge --native --thinking --input evals/judge_calibration_cases.json --calibrate --ids cal-13 --max-tokens 6144 --timeout 600 --output reports/runs/thinking-verification-new.json
```

For a matched off arm, omit `--thinking` and select a different output filename; keep all other conditions fixed. For the frozen six-case synthetic input, use `evals/judge_reasoning_validation.json` without `--calibrate`. Its authored expectations are not sent to the judge and still need human review. Runtime metadata includes elapsed seconds even on a timeout and an observed/not_observed/unknown thinking verification marker. Invalid output remains UNCERTAIN, never an automatic pass or a retry-until-success. The native API does not document a finish-reason field, so prompt-JSON mode is an experimental path with strict post-validation rather than equivalent constrained decoding.

For the subsequently verified Thinking plus strict-schema configuration, omit `--native` and `--unconstrained`, and use `--thinking --max-tokens 6144 --timeout 600` under the saved 1024-token preset. Six synthetic cases returned valid matching verdicts with observed reasoning; see [validation evidence](../reports/baseline/JUDGE_STRUCTURED_THINKING_VALIDATION.md). This small validation does not make the judge an automatic release gate.

## v6 policy clarification (Rachel confirmed)

The default rubric is now calendar-answer-v6. cal-08 distinguishes the converted query window from the actual busy event. cal-10 requires asking for a user-supplied end time or duration; suggesting a default for confirmation is not accepted. The Calendar agent prompt and future evaluation criteria use this policy. Existing saved source answers and v5 results remain unchanged.

For saved traces, the runner applies case-specific `criteria_overrides` only to the judge request and records them and policy provenance in the new report. It does not rewrite the source. Original v5 is preserved as `evals/calendar_judge_rubric_v5.json`; use `--rubric evals/calendar_judge_rubric_v5.json` for historical scoring. The judge SYSTEM prompt is unchanged. v6 semantic behavior has not yet been validated with the local model.

Focused v6 validation returned valid JSON and matched all four authored synthetic expectations with observed reasoning. See [validation evidence](../reports/baseline/JUDGE_POLICY_V6_VALIDATION.md). This does not establish held-out accuracy or validate the updated SUT prompt.

## v7: separate interval checks

cal-08 now checks busy status, event times, optional query conversion, and the requested Taipei interval separately. Reference facts explicitly identify the overlap. Omitting the optional conversion is acceptable. v6 is archived in `calendar_judge_rubric_v6.json`; prior evidence is unchanged. Local model validation is pending; deterministic tests do not establish judge accuracy.
