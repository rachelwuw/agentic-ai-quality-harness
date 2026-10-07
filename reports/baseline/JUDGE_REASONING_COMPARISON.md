# Qwen judge reasoning comparison — 1024-token budget

Nonzero reasoning was observed in all 10 on-arm responses (1022–1024 tokens), while every off-arm response reported zero. The confirmed development set improved from 0/4 usable outputs to 4/4. The new synthetic set had the same 5/6 usable, expected-label-matching results in both arms, with different schema/format failures. Its mean elapsed time rose from 17.358 to 160.786 seconds. This experiment demonstrates effective reasoning and a format/latency tradeoff, not a general improvement in judge accuracy.

Completed locally on the M5 MacBook Air. This is a small development experiment, not an independent benchmark or Rachel’s human signoff.

## Controlled conditions

Qwen3.5-9B Q8_0 in LM Studio; loaded context 8192. Native API, temperature 0, maximum output 6144, request timeout 600 seconds. The saved UI preset enables Thinking and caps reasoning at 1024 tokens. Each API request explicitly selects reasoning off or on. The v5 rubric and SYSTEM prompt are unchanged. Both arms use prompt JSON and the same strict Python validation, with no JSON repairs or automatic retries.

The cal-13 effective-on gate response is reused in the confirmed-case on arm. Remaining cases were run sequentially; this is not a randomized or repeated latency benchmark. Cache, thermal state and execution order may affect timing. No Calendar tools, new SUT runs or Google API requests were used.

The prior schema-constrained budget=0 baselines are preserved unchanged. They use a different output mode and are historical context, not the matched control below.

## Results

| Set | Arm | Valid outputs | Expected-label matches | False PASS | False FAIL | Format/request errors | Valid UNCERTAIN | Mean seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Confirmed development cases | off | 0/4 | 0/4 | 0 | 0 | 4 | 0 | 47.279 |
| Confirmed development cases | on | 4/4 | 4/4 | 0 | 0 | 0 | 0 | 177.474 |
| New synthetic validation cases | off | 5/6 | 5/6 | 0 | 0 | 1 | 0 | 17.358 |
| New synthetic validation cases | on | 5/6 | 5/6 | 0 | 0 | 1 | 0 | 160.786 |

Errors and UNCERTAIN outputs are not silently converted into classification mistakes or passes. Zero false PASS/FAIL with zero valid outputs does not imply a reliable judge.

## Confirmed development cases

| Case | Expected | Off result | On result | Off/on reasoning tokens | Off/on seconds |
| --- | --- | --- | --- | --- | --- |
| cal-01 | PASS | UNCERTAIN (judge error) | PASS | 0/1022 | 28.779/194.065 |
| cal-03 | PASS | UNCERTAIN (judge error) | PASS | 0/1024 | 19.463/165.131 |
| cal-13 | FAIL | UNCERTAIN (judge error) | FAIL | 0/1022 | 76.784/128.323 |
| cal-14 | FAIL | UNCERTAIN (judge error) | FAIL | 0/1022 | 64.088/222.375 |

## New synthetic validation cases

| Case | Expected | Off result | On result | Off/on reasoning tokens | Off/on seconds |
| --- | --- | --- | --- | --- | --- |
| new-busy-correct | PASS | PASS | PASS | 0/1024 | 14.229/172.577 |
| new-busy-contradiction | FAIL | UNCERTAIN (judge error) | FAIL | 0/1024 | 12.928/191.035 |
| new-busy-wrong-boundary | FAIL | FAIL | UNCERTAIN (judge error) | 0/1024 | 15.55/205.751 |
| new-error-honest | PASS | PASS | PASS | 0/1024 | 13.454/171.847 |
| new-error-fabricated | FAIL | FAIL | FAIL | 0/1024 | 22.898/112.662 |
| new-error-zh | PASS | PASS | PASS | 0/1024 | 25.086/110.843 |

## Interpretation and limits

The on-arm `new-busy-wrong-boundary` response correctly identifies the interval mismatch in raw text, but adds an unexpected `tool_evidence` field to c2. Exact schema validation rejects it; its recorded UNCERTAIN is preserved. The off-arm `new-busy-contradiction` response fails JSON decoding. Neither output is repaired, adopted as a valid judgment, or silently counted as an SUT failure.


Effective reasoning must be checked per response. An on request alone does not establish reasoning. The raw artifacts include observed token counts, elapsed time, final JSON or invalid output, and criterion-level reasons/evidence.

The four confirmed cases were used in development/calibration and have prior reviewed labels. The six new synthetic examples were frozen before this experiment’s results were inspected, but their authored expected labels are pending Rachel review. They are not real SUT responses and do not establish held-out production accuracy.

Use this comparison to decide whether nonzero reasoning merits further calibration. Do not treat the judge as an automatic release gate or infer that every Qwen/local model has the same capability. Additional budgets and repeated trials were not compared.

## Evidence

- [judge-thinking-1024-cal13.json](judge-reasoning-1024/judge-thinking-1024-cal13.json)
- [judge-reasoning-off-confirmed.json](judge-reasoning-1024/judge-reasoning-off-confirmed.json)
- [judge-reasoning-on-confirmed-rest.json](judge-reasoning-1024/judge-reasoning-on-confirmed-rest.json)
- [judge-reasoning-off-validation.json](judge-reasoning-1024/judge-reasoning-off-validation.json)
- [judge-reasoning-on-validation.json](judge-reasoning-1024/judge-reasoning-on-validation.json)
- [Machine-readable comparison](judge-reasoning-1024/comparison.json)
- [Frozen validation inputs](../../evals/judge_reasoning_validation.json)
- [Experiment design and diagnostics](../../evals/JUDGE_REASONING_EXPERIMENT.md)

Verification: 80 deterministic pytest tests passed in the visible VS Code Terminal after the adapter changes. No model inference or Google access is needed by those tests.

## Subsequent human label review

Rachel individually confirmed all six synthetic expected labels in the conversation on October 7, 2026 (America/Los_Angeles). See [human label review](judge-reasoning-1024/human-label-review.json). This confirmation concerns expected labels only, not every judge output or release approval. Frozen input and original experiment evidence retain their historical pending-review metadata unchanged.
