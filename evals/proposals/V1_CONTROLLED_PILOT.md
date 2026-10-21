# Proposed v1 controlled pilot — execution not authorized

Implementation update: the separate [bounded runner](../../docs/CONTROLLED_RENDERER_PILOT.md) and [six-case JSON](v1_controlled_pilot_cases.json) now supply the execution support described below, verified with scripted offline tests only. Exact references and real execution still require review/approval. The API-error product reports unverified scope because its recorded tool error lacks scope evidence. The prerequisite list below describes the original planning sequence; runner implementation is now complete, not pilot execution.

October 21, 2026. Companion to [v1 acceptance gates](../../docs/V1_ACCEPTANCE.md). This specifies the smallest next diagnostic round after missing controlled-runner support is implemented and reviewed. No new prompts, rubric/model settings or historical expected labels are changed here.

Subsequent implementation update: the [explicit-date guard](../../docs/EXPLICIT_DATE_GUARD.md) now supplies a deterministic question for the missing-date case without inference; raw model answer is absent. Expected product status remains unsupported. Healthy total becomes 10 inference requests instead of the original estimate of 11 below; cap 18 remains unchanged. The original prompts/fixtures/status expectations and historical estimates below are retained.

## Exact proposed inputs and independent references

Fresh conversation per case; frozen `now=2029-01-01T12:00:00-08:00`. Local SUT `openai/gpt-oss-20b`; retain recorded context 8192, temperature 0, max_tokens 2048, subject to runtime verification without automatic reconfiguration. Explicit renderer language is independent of prompt language. Scope is always the configured test calendar.

| Id / renderer language | User prompt (exact) | Controlled Calendar fixture | Reference expectation |
| --- | --- | --- | --- |
| v1p-01 / en | Is 2029-01-23 09:10–09:20 America/Los_Angeles free on the dedicated test calendar? Explain any conflict. | Busy 2029-01-23T17:00:00Z → 17:45:00Z. | One query 09:10–09:20 −08:00 (UTC 17:10–17:20); unavailable; event local 09:00–09:45, contains query. Product rendered. |
| v1p-02 / zh-TW | 請查詢專用測試行事曆：2029-07-24 14:20 到 14:50，America/Los_Angeles，有空嗎？請說明衝突。 | Busy 2029-07-24T21:00:00Z → 21:30:00Z. | One query 14:20–14:50 −07:00 (UTC 21:20–21:50); unavailable; event local 14:00–14:30, partial overlap. Product rendered. |
| v1p-03 / zh-TW | 請查詢專用測試行事曆：2029-07-25 07:10 到 07:40，Asia/Taipei，有空嗎？ | Busy 2029-07-24T16:00:00-07:00 → 16:30:00-07:00. | One query 07:10–07:40 +08:00 (UTC July 24 23:10–23:40); event Taipei July 25 07:00–07:30; unavailable, partial overlap. Preserve original timestamps. Product rendered. |
| v1p-04 / en | Check 2029-01-23 12:00–12:30 America/Los_Angeles on the dedicated test calendar. | Event 2029-01-23T11:15:00-08:00 → 12:00:00-08:00; return no conflicts for endpoint-adjacent query. | One query 12:00–12:30 −08:00 (UTC 20:00–20:30); available; no invented event in product. Product rendered. |
| v1p-05 / en | Is 09:10–09:20 America/Los_Angeles free on the dedicated test calendar? | No Calendar access allowed. | Missing date: no tool/API call and no free/busy claim. Raw answer should request date; product unsupported, null rendered answer. CLI 1 is expected, not a semantic FAIL by itself. |
| v1p-06 / en | Check 2029-01-23 15:00–15:30 America/Los_Angeles on the dedicated test calendar. | Controlled Calendar adapter raises CalendarError on the first call; not a real API error. | One intended query 15:00–15:30 −08:00 (UTC 23:00–23:30); availability unknown, no extra query. Product unknown; CLI 1 expected. |

These are proposed new examples, not an independently certified benchmark. The Python offset/reference cross-check performed while authoring only detects arithmetic transcription mistakes; a separate reviewer must approve prompts, fixtures and expected outcomes before inference. No labels are being inferred from a model/Judge answer.

## Capture and separate grading

- Reuse `run_calendar_agent(..., renderer_language=...)`; do not make a second model conversation for raw/product comparisons. Keep original answer/events intact and grade tool intent, exact arguments, resolved API interval, Python facts, raw prose and product separately.
- Exactly one allowed controlled Calendar call on v1p-01/02/03/04/06; zero on 05. Block unexpected/extra calls before executing any adapter operation and record the violation. No OAuth or Google client creation; fake Calendar only.
- A plan/runner must represent expected unknown/unsupported without imposing the old grader's generic successful-tool/available gate. Also verify product text/null, exit behavior, English/Traditional Chinese selection, dates/offsets/scope and relation. Count every planned case, including interrupted/unattempted/inconclusive cases.
- Save new private owner-only outputs, source/prompt/case/reference/runtime identities and all failures; never overwrite old baselines. No raw private live material in this pilot. Promote controlled evidence only after review.

## Execution budget for Rachel to review later

- **One six-case round**, normally 11 inference requests (five tool cases x two plus one no-tool case), five simulated tool operations; zero real Google calls and zero Judge calls.
- Proposed hard cap **18 physical inference attempts**, including retries. Existing per-request timeout remains unchanged. Add a 10-minute orchestration deadline that starts no new request after expiry; an in-flight request may finish under its existing timeout. Record partial results on stop. No additional cases, tuning, auto model loading or reruns under this budget.
- Estimate **1–3 minutes** for healthy generation, excluding runtime setup/human review. Reference: the earlier three-case/six-request round took 24.459 seconds. This is an estimate, not a deadline guarantee; timeout/backoff can extend it.
- Stop on changed/unavailable runtime, unsafe/unexpected calls, budget/deadline, failed fixture/reference verification or interruption. Semantic defects stay in the report; do not replace them with successful retries or silently remove them.

## Later acceptance inventory — not a frozen dataset or execution approval

The earlier 20 x 3 idea should cover winter/summer, both endpoint adjacencies, partial/contained/multi-event relations, cross-day zones, noon/midnight, all-day limitations, missing date/end, ambiguous timezone, DST gap/fold and API/malformed-response errors. Twenty exact independently reviewed inputs, endpoint references, routing and scoring denominators are **not yet prepared**. No independent-accuracy claim may be made from the six diagnostic cases above, and the 60-conversation run is not approved.

## Prerequisites before execution request

1. Ratify v1 scope and these six prompts/references/outcomes, including unsupported versus clarification behavior.
2. Implement/review missing controlled runner support and scripted offline tests: renderer propagation/default compatibility, per-case fake fixtures, blocked live/extra calls, attempt caps, immutable captures, private exclusive outputs, partial results and expected non-rendered outcomes. CLI routing itself already has tests; reuse it.
3. Freeze exact candidate/cases and verify loaded runtime settings. Present CI, concrete invocation/report destination and the above budget for explicit execution approval. Use the linked runner documentation for the explicit command; this plan still authorizes no model/Google/Judge calls.
