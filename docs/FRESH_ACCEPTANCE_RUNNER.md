# Fresh controlled acceptance runner — versioned batches

## Current execution status — October 26, 2026

Rachel later authorized bounded autopilot: first-round missing batches plus one complete four-batch repeat. This budget is consumed: six new invocations, 40 new physical inference attempts, all forty case observations completed across two rounds on `cad0604`. The original approval table/next-step text below preserves the pre-execution context. See [results, raw defects and remaining human gates](V1_BOUNDED_CLOSEOUT.md); no further batch runs are authorized by that old table. Original reference metadata/labels remain unchanged.

Engineering delivery, October 21, 2026. Implements the reviewed case-inventory direction from [PR #28](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/28) which was merged into main on October 22, 2026, without changing its rebuild scope. No new real SUT/Google/Judge run has occurred. New [literal case/reference JSON](../evals/proposals/v1_fresh_acceptance_cases.json) is authored and offline-checked; exact reference/human review and execution approval are still separate prerequisites, not independent benchmark certification.

## Explicit protocol and batch selection

The existing entry point dispatches by schema:

- `calendar-controlled-renderer-pilot-v1`: original v1p-01–06, unchanged case bytes, defaults and grading; `--batch` is rejected.
- `calendar-controlled-acceptance-v1`: exactly ordered v1a-01–20, requires an explicit `--batch 1|2|3|4`; no implicit all-twenty run.

| Batch | Selected cases | Healthy inference estimate | Current approval |
| --- | --- | --- | --- |
| 1 | v1a-01–06 | 11–12 | Not approved to execute |
| 2 | v1a-07–12 | 11–12 | Not approved to execute |
| 3 | v1a-13–18 | 5; three deterministic date-gate cases use zero | Not approved to execute |
| 4 | v1a-19–20 | 3 | Not approved to execute |

Every batch retains the existing shared cap **18 physical inference attempts including retries**, orchestration deadline **600 seconds**, and unchanged request timeout/model parameters. No loop over batches, new cap increase, auto-loading, model/Judge swap or rerun-until-green is introduced. Estimates are not guarantees or execution authorization. The earlier 20 x 3 proposal is not implemented as an automatic study.

Command for later approval only; do not execute as part of installation/testing:

```sh
python -m harness.calendar_pilot --execute-controlled \
  --cases evals/proposals/v1_fresh_acceptance_cases.json --batch 1 \
  --private-dir reports/runs/v1-fresh-batch1-new
```

Suite validation and required batch selection happen before output/model construction. The original fake Calendar adapters, same-run raw/product capture, argument guard, physical request budget, runtime identity checks and atomic owner-only reports are reused. There is no Google/OAuth/Judge connection. Existing output directories are refused. Manifest records the full suite hash, source hashes, selected IDs/batch/protocol and runtime snapshots; reports distinguish selected planned rows from excluded inventory IDs. Not-attempted/incomplete rows remain in the selected denominator, including after a stop.

## Reference and route contract

New data explicitly records prompts, per-case fixtures, IANA local query arguments, resolved/UTC endpoints, converted event endpoints, literal product lines, raw-answer review criteria and deterministic input messages. References were transcribed from the proposed inventory and checked offline with existing date/zone logic; the renderer/SUT was not invoked to author golden answers. Shared arithmetic checks are not independent validation. Freeze/review the JSON, code and runtime identities before real inference; do not silently change references to match an observed answer.

Both DST cases retain exactly two predeclared alternatives:

1. No tool call: unsupported/null product; raw model clarification still requires review.
2. One exact original local-time `check_availability` call: Python rejects the DST gap/fold before any fake Calendar operation, returns `dst_time_requires_clarification`, and product is conservative unknown.

Different dates/offsets, extra calls or a chosen fold are not alternatives and are blocked before tool execution. Both routes authorize **zero Calendar operations**. Do not pick a route after seeing the result or delete one to tune a score. Runtime grading records the observed route independently of product status.

Cases 15–17 require the deterministic date gate: exact input message, no raw model answer, no tool event or inference attempt. Cases 18/19 (missing end/ambiguous zone) require no tool call but still depend on model clarification; the runner tests behavior, it does not add a new SUT guard for them. Case 20 is simulated CalendarError, not live-error coverage. Partial overlap, midnight/day changes, adjacency and original/converted endpoints have literal independent-of-model reference strings for comparison.

## Separate results; no semantic shortcut

Report structural checks, Python fact comparisons, product literal-reference matches, chosen route and input-gate match separately. Preserve raw LLM answer/events and product output from the same run. `automated_pass` means these automated contract checks matched; raw-answer and human-product review stay pending and `semantic_pass_claim=false`.

In particular, a DST no-tool answer saying "Free!" can satisfy no-tool/unsupported routing but is **not** a semantic pass: the raw criterion requires clarification, and human review must reject that claim. Null/unknown products cannot certify user-facing explanation quality. User-intent correctness, product fidelity, raw prose and Judge behavior are distinct dimensions; this change does not fix model behavior or validate intent generalization.

## Offline evidence

379 full pytest tests passed, including 37 new fresh-protocol tests. The earlier explicit-date-guard checkpoint had 342 tests; that historical result is retained in its implementation report. Socket-blocked fake Chat Completions/runtime responses cover all twenty inputs through actual agent/tool/renderer loops, both DST routes, fractional-hour/cross-day/boundary references, all four batches, required selection, immutable captures/private files, physical retry cap/deadline, interrupted partial rows, unsafe calls and legacy protocol preservation. No real model/Google/Judge calls occurred.

[Protocol validator/grading](../src/harness/calendar_acceptance.py) · [Shared runner](../src/harness/calendar_pilot.py) · [Tests](../tests/test_calendar_acceptance.py)

Next: review literal input/reference JSON and CI, freeze the candidate, then request approval for **one** named batch with concrete commit/output directory/budget. Keep unseen cases unused if a first-batch failure leads to SUT tuning. No current installation/dependency-lock or clean-environment claim is added by this runner work.
