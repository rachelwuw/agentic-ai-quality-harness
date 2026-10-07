# Judge reasoning experiment

Rubric and SYSTEM prompt remain calendar-answer-v5. Existing baselines are preserved.

The runner supports --thinking, --max-tokens, --runtime-note and --unconstrained. The OpenAI-compatible adapter records elapsed seconds, usage, finish reason and the returned reasoning channel. The native adapter records elapsed seconds, token stats and reasoning output; the native API does not document a finish-reason field. Timeouts also retain elapsed seconds in new runs. A requested setting is not proof that reasoning occurred: check reasoning_tokens and returned reasoning content. Errors remain UNCERTAIN; no automatic retries.

Initial environment: local Qwen3.5-9B, 8192 context, Enable Thinking on, explicit Reasoning Budget 2048. Output allowance 6144 leaves space for reasoning plus final JSON for these short examples.

The first strict-schema attempts reported zero reasoning tokens even with thinking requested. They are diagnostic attempts, not a valid thinking-on comparison. Further probes distinguish API control from structured-output effects.

Six new synthetic examples in judge_reasoning_validation.json were frozen before inspecting the experiment results. They test busy interval boundaries, contradictory answers, fabricated API success and Chinese error disclosure. Their expected labels are authored expectations pending Rachel review, never sent to the judge. They are neither real SUT runs nor an independent benchmark.

Fair comparison requires the same output mode and token allowance on both arms. If strict JSON schema prevents reasoning, compare both arms in prompt-JSON mode, count parser errors separately, and do not attribute changes solely to reasoning when sampling or formatting changes.

## Diagnostic attempts (not the comparison)

| Saved output in reports/runs/ | Observation |
| --- | --- |
| judge-v5-thinking-calibration.json | Interrupted early; observed responses reported zero reasoning tokens. |
| judge-thinking-probe.json | cal-13: FAIL, 24.683 seconds, zero reasoning tokens. |
| judge-thinking-no-schema-probe.json | cal-13: invalid JSON, 49.05 seconds, zero reasoning tokens. |
| judge-native-thinking-probe.json | cal-13: invalid JSON, zero reasoning-output tokens. |
| judge-native-saved-preset-probe.json | cal-13: request timed out at the earlier 180-second client limit; no returned token stats. |

The no-schema and native probes also returned zero reasoning tokens. Therefore strict JSON constraints alone have not been established as the cause. An unrestricted saved preset led to a timeout, which is also not evidence of successful reasoning. The new judge timeout is configurable (default 600 seconds); the SUT client keeps its 180-second default.

The effective-on gate is a returned reasoning-token count greater than zero, recorded as `thinking_verification: observed`. A Thinking request, saved preset, longer latency, or nonempty UI activity alone does not satisfy that gate. Format errors, timeouts and uncertain verdicts must be reported separately from false PASS and false FAIL.

Completed: effective reasoning was verified and the matched four-case development comparison plus six-case synthetic validation ran once per arm. The cal-13 verification response was reused. Final adapter verification: 80 deterministic tests passed in the visible VS Code Terminal. See [the comparison report](../reports/baseline/JUDGE_REASONING_COMPARISON.md) for counts, latency and preserved raw evidence.

Native request fields and token-stat interpretation follow [LM Studio's Chat API documentation](https://lmstudio.ai/docs/developer/rest/chat). The locally installed qwen/qwen3.5-9b model.yaml declares Enable Thinking default true; this does not establish the current effective API configuration.

## Effective-on gate verified

After Rachel set Enable Thinking on and a 1024-token reasoning budget, the setting was saved in the local preset. The native cal-13 verification probe returned 1022 reasoning-output tokens, 1644 total output tokens, valid criterion JSON, and FAIL in 128.323 seconds. This establishes observed reasoning for that response, not for every future response.

Matched comparison: native API, prompt JSON with strict post-validation, temperature 0, maximum output 6144, timeout 600 seconds. The off arm requests reasoning off; the on arm requests reasoning on under the saved 1024-token budget. The cal-13 gate response is retained for the confirmed-case on arm rather than rerun. Each case gets one attempt; failed JSON is not repaired or retried. The older schema-constrained budget=0 baseline is historical context, not the matched control.

Confirmed-case subset: cal-01, cal-03, cal-13, cal-14 (existing development/calibration examples with previously reviewed labels). New validation: all six frozen synthetic examples, expected labels pending human review. No new SUT execution or Google API access occurs.

## Subsequent structured-output validation

Rachel individually confirmed the six synthetic expected labels on October 7, 2026. The frozen source retains its historical pending metadata; [the separate human review record](../reports/baseline/judge-reasoning-1024/human-label-review.json) records the confirmation.

The strict-schema OpenAI-compatible adapter, with Thinking requested under the saved 1024-token budget, subsequently returned 6/6 valid outputs matching these labels. All six responses reported 1024 reasoning tokens. Mean latency was 129.470 seconds. One attempt per case; gate response reused. API transport differs from the earlier native comparison, so this does not isolate the effect of schema enforcement. See [the preserved report](../reports/baseline/JUDGE_STRUCTURED_THINKING_VALIDATION.md). No code or rubric changes were needed for this validation.
