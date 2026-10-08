# Judge v8: trace facts and timezone wording

Status: implemented; 101 deterministic tests passed in the visible VS Code Terminal (3.50 seconds). The four frozen synthetic examples were scored on October 8: valid outputs and 4/4 matching authored expectations (PASS/FAIL/PASS/FAIL). [Result review](../reports/baseline/JUDGE_POLICY_V8_VALIDATION.md) preserves raw evidence. This focused development check does not establish general Judge reliability.

## Minimal change

`No Google API request may occur` is scored directly from the saved `api_calls` list. Empty list is PASS; a recorded request is FAIL; missing or malformed trace is UNCERTAIN. A local `check_availability` invocation is not an external request. Controlled fixtures record simulated external requests, not actual Google traffic. This establishes facts within the recorded trace; it is not independent network auditing.

The v8 report marks each check's grader as `deterministic_trace` or `llm_judge`. The deterministic requirement is removed from the checks sent to Qwen. Python merges the two sources and computes the aggregate verdict. Invalid judge output leaves semantic checks UNCERTAIN while retaining independent trace failures. Historical v5/v6/v7 execution behavior is preserved when their rubrics are explicitly selected.

v8 adds criteria to cal-03 and cal-08 for truthful timezone labels and claimed conversions. October Los Angeles is PDT (UTC-07). The 11:00–11:30 Los Angeles event converts to 02:00–02:30 on the next day in Taipei. Optional conversions may be omitted, but a claimed conversion must match the displayed time and timezone. Language and explicit scope policy changes are not included in this revision; those coverage questions remain open. Clarification defects in cal-09 and cal-14 are not solved by this patch.

## Frozen validation cases

| Case | Authored expectation | Difference under test |
|---|---|---|
| v8-conversion-correct | PASS | Correct next-day Taipei event conversion. |
| v8-conversion-wrong | FAIL | Claims Taipei conversion while leaving Los Angeles date and clock values unchanged. |
| v8-daylight-correct | PASS | Correct Pacific Daylight Time wording. |
| v8-daylight-wrong | FAIL | Calls the October event Pacific Standard Time. |

These are newly authored wording variants on an existing controlled trace, not newly generated SUT answers or an independent held-out benchmark. Labels are authored expectations pending Rachel's review. Expected labels are withheld from the model prompt. Freeze these bytes before execution; compare positive and negative examples and retain every result rather than retrying until PASS.

## Visible validation procedure

After verifying LM Studio Thinking enabled and Reasoning Budget 1024, run in the visible VS Code Terminal:

```sh
JUDGE_MODEL=qwen/qwen3.5-9b LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1 .venv/bin/python -u -m harness.calendar_judge --thinking --input evals/judge_policy_v8_cases.json --max-tokens 6144 --timeout 600 --runtime-note "Thinking on; UI budget 1024 verified; inspect observed tokens" --output reports/runs/judge-v8-timezone-validation.json
```

The runner does not automatically compare these non-calibration labels. Review each verdict and criterion reason against the table above, including the two expected PASS controls. Use a fresh output filename for every intentional run. Source human-review status stays pending.

Suite SHA-256: `7674f3052bc836fd304bdc716b528a6b4cb85c9804e8a777b8b2c629e7afc7db`

Rubric SHA-256: `846999cbc41c6ad0178d5b04929d8d4fadccda8437b157ce04f8fb2a8345e78c`

v7 is archived unchanged at `evals/calendar_judge_rubric_v7.json`. Earlier results remain unchanged.

Original-answer follow-up completed: cal-03 correctly FAIL, cal-08 still falsely PASS under the conversion criterion. [Evidence review](../reports/baseline/JUDGE_V8_ORIGINAL_CASE_REVIEW.md). Do not infer reliability from the four synthetic controls.
