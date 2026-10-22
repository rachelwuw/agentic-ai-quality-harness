# v1 acceptance checklist — Python CLI Calendar agent

Planning checkpoint: October 21, 2026; implementation/evidence inspected at `0c2e4b3`. Current version remains `0.3.0.dev0`. This document is an acceptance plan, not a release declaration or authorization for real calls.

## Agreed delivery direction

The primary v1 path is the Python CLI with explicit `--renderer python --language en|zh-TW`: a local LLM chooses the read-only Calendar tool; Python validates/computes facts and renders a separate product answer. Keep raw `answer`, tool `events` and `product_output` distinct. Do not change default flags implicitly. LM Studio continues to host inference; its chat-box/MCP experience already exists, but its full integration/acceptance is a **v2 target**, not evidence inherited from CLI tests.

V1 supports complete, explicit date/start/end/IANA-zone requests on the dedicated test calendar. Unknown/error/unsupported outcomes must be honest and visible. A [conservative explicit-date gate](EXPLICIT_DATE_GUARD.md) now supplies a separate deterministic question before inference when a full date is absent/unrecognized. Product output remains unsupported; there is no raw model answer or multi-turn state. This does not verify user intent. Calendar writes, multi-turn chat and automatic Judge signoff are excluded.

## Acceptance and evidence map

`[ ]` means the final v1 gate is not yet satisfied, even where implementation exists.

| Gate | Evidence already implemented/recorded | Missing acceptance evidence |
| --- | --- | --- |
| [ ] Product contract | [Renderer contract](CALENDAR_RENDERER_PREVIEW.md), [CLI routing](CALENDAR_RENDERER_OPT_IN.md): rendered/unknown/unsupported, no silent raw fallback; timed/all-day/multiple-event limits. | Ratify exact release contract, including generic unsupported response/exit 1 for incomplete requests; do not describe that as a successful clarification UX. |
| [ ] Offline logic and CI | Current recorded 379 passing offline tests (342 at the earlier explicit-date-guard checkpoint, plus 37 fresh-protocol tests); [suite](../tests), [required CI](../.github/workflows/deterministic-tests.yml). Timezone/DST, validation, retries, source preservation and routing have tests. | Final candidate's full CI with no unexpected skips; updated count and commit. No extra arbitrary test-count target. |
| [ ] Intent, tool and Python facts | Historical [15-case baseline](../reports/baseline/CALENDAR_BASELINE_V7_RETRY_REVIEW.md): 14/15 strict structural passes, recovery recorded separately. | New reference-reviewed cases on the v1 candidate: inspect selected query separately from renderer fidelity. Review the separate controlled runner below before execution. |
| [ ] Product correctness/repeatability | [Three controlled cases](../reports/baseline/calendar-renderer-e2e-v1.json): structure/facts/assisted product checks passed once each. | Frozen new cases and repeated runs; no critical false availability/time/scope claims, wrong accepted queries, writes or raw fallback. Expected unknown/unsupported is not a failure merely because CLI exits 1. |
| [ ] Real Google integration | [One three-case renderer round](LIVE_RENDERER_OPT_IN.md#approved-live-renderer-round-v1-outcome), [public summary](../reports/baseline/calendar-live-renderer-attempt-v1-summary.json): fixture/structure passed; assisted product review passed. | Historical L1–L3 product outputs received Rachel's case-by-case approval, recorded privately. A separately approved fixed-version repeat with fixture preflight remains missing. Simulated API errors must not be called live-error coverage. |
| [ ] Human acceptance | [Rachel's signoff](../reports/baseline/CALENDAR_RENDERER_E2E_V1_HUMAN_SIGNOFF.md) covers exact winter-busy, summer-cross-day, noon-free product strings/hashes. | [Six diagnostic pilot outputs](../reports/baseline/V1_CONTROLLED_PILOT_003_HUMAN_SIGNOFF.md) now have case-level human approval. Fresh independent acceptance outputs and new fixed-version live outputs still need review; no transfer to raw LLM/new answers/general reliability. Preserve historical pending labels. |
| [ ] Judge boundary | Deterministic facts plus advisory Qwen; [criterion disagreements](../reports/baseline/JUDGE_V10_FRESH_REVIEW.md) preserved. | Release procedure must use fixed references/manual adjudication, not Judge PASS as approval. Full v10 baseline/Judge repeatability are research backlog, not prerequisites for this advisory-only release. |
| [ ] Reproducible release | [Setup](LOCAL_SETUP.md), configurable roles, private traces and source-control rules exist. | Complete dependency lock, clean-environment install/test verification, model/runtime manifest and fresh Google auth validation. Final CI, known-limitations review and Rachel release approval; no v1 tag/version bump yet. |

## Proposed thresholds and sequence

Preparation artifacts: [20 new acceptance-case proposals](../evals/proposals/V1_FRESH_ACCEPTANCE_CASES.md) and [environment rebuild evidence plan](V1_REBUILD_EVIDENCE_PLAN.md). The rebuild and fresh SUT acceptance runs have not been executed. The [versioned fresh runner](FRESH_ACCEPTANCE_RUNNER.md) now supports the twenty-case inventory through four explicitly selected batches; its literal references still require separate review before inference. Historical live L1–L3 outputs have Rachel’s private signoff; that approval does not transfer to the latest candidate.

1. Keep the [six-case pilot](../evals/proposals/V1_CONTROLLED_PILOT.md) and its signoff as regression evidence. Review the [fresh runner and literal references](FRESH_ACCEPTANCE_RUNNER.md), then freeze inputs/references/code/runtime before asking to execute one named batch.
2. Pilot is diagnostic, not held-out accuracy. If code/prompts are changed after inspecting it, retain these cases as regression evidence and use fresh, independently checked acceptance inputs.
3. A later **20-case x 3-round** candidate is a proposal, not an approved run: 100% of applicable critical checks must pass; optional presentation checks target at least 95%, with denominators stated per criterion and case outcome. Missing/truncated/incomplete outputs cannot disappear from counts. Report all repeats; no rerun-until-green. Independent reference review must precede inference; future adoption/tuning retires the set as held-out evidence.
4. Complete live review/repeat and clean-environment evidence, then assess the final commit against every gate. Zero unresolved critical defects in the declared scope. Small-sample results remain bounded evidence, not population accuracy.

## Identified engineering gap / implementation status

A [separate bounded pilot runner](CONTROLLED_RENDERER_PILOT.md) now implements this prerequisite without changing the old evaluator. It has only scripted offline evidence, not new SUT results. The original gap remains descriptive of the legacy entry point: `calendar_evaluate.evaluate()` calls `run_calendar_agent()` without `renderer_language`. Its `ControlledCalendar`/`grade_structure` use the old fixture model and one-call expectations. Existing agent/live opt-in support must be reused, not redesigned. The separate runner adds an explicitly selected, bounded controlled protocol with per-case fixtures/expected routing. It preserves existing runner defaults/labels, uses only fake Calendar adapters, and counts physical inference attempts including retries. Wrong tool arguments must fail independently even if the resulting renderer text is internally consistent.

No live SUT, Google or Judge run is authorized by this document. New runner work, experiment execution and PR merge/release approvals are separate checkpoints under [source-control workflow](../SOURCE_CONTROL.md).
