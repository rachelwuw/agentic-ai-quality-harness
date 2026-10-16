# Bounded live runner renderer opt-in

## Current status — after the recorded experiment

[PR #18](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/18) was subsequently authorized and merged as `2e79e243bccbac5d531a82ae2d587d450f7bb0d7`. The proposal's “not executed” heading and closing “Keep PR #18 unmerged” instruction below preserve their original planning/authorization context. The approved execution is recorded in the outcome section; neither the prior execution nor merge approval authorizes a new run. Individual answer signoff remains pending.

Dependency: merged #17 (`16899ef`), based on #15 interval facts and #16 renderer.
This change only passes explicit renderer language into the existing Python agent
API. It adopts no rejected prompts or rubric changes and adds no MCP behavior,
Calendar writes, inference, queries or automatic live execution.

## Selection, compatibility and evidence

```sh
python -m harness.calendar_live_regression --live-readonly \
  --renderer python --language zh-TW \
  --private-dir reports/runs/live-renderer-new
```

This command performs real requests and is NOT approved to execute by the
engineering task. `--renderer python` and explicit `en`/`zh-TW` must be paired;
language applies to all three product outputs, independently of prompt language.
Validation occurs before case loading, output creation, runtime or OAuth access.
API `run_suite(..., renderer_language=None)` and CLI with no renderer flags retain
their previous schema and behavior, with no product_output or renderer summary.

Opt-in uses the SAME agent run's raw `answer`/events and adds `run.product_output`
from #17 with renderer version, language, status/reasons/limitations and provenance.
Tool/HTTP evidence and time facts remain alongside them. Rendering does not send
anything back into a model/Judge, alter expected labels, or establish intent parsing.
Unknown stays unknown; unsupported has no product answer or raw-prose fallback.
Opt-in requires all three renderer statuses to be rendered for CLI success, plus
the existing structural/runtime requirements; this is not semantic signoff.

The existing three fixture preflight reads, one exact query per agent case,
pre-send blocking, drift detection, physical-send/inference-attempt caps of 12 each,
runtime checks and interrupted-progress saving remain in place. No model-request
captures are added. Existing HTTP evidence remains private. Test payload captures
use deep copies at send time, not mutable message-array references.

## Private versus public

Existing new owner-only reports/runs/ directories and atomic 0600 files retain raw
Google/tool results, queries, model answers, product text and native runtime details.
Credentials stay in the existing auth storage, not reports/Git. Nothing uploads raw
data automatically. Existing baselines and private historical captures are untouched.

Only when renderer is requested, the strict public summary adds fixed per-case
`renderer_status` values and `renderer_counts`: planned=3 and counts for rendered,
unknown, unsupported, pending, unavailable, not_attempted. Counts always account for
all planned cases; missing/in-progress output is not a graded failure or PASS.
Unrecognized/private status values map to unavailable. No rendered/raw text, reasons,
limitations, dates, timezone, language, Calendar IDs, URLs or arbitrary fields are
exported. `semantic_pass_claim` stays false. Rendered is not semantic accuracy.

## Offline checks

Scripted/fake HTTP tests verify both languages, busy/free, permanent API error and
unknown, unsupported no-tool answers, early paired-flag validation, default/opt-in
raw run and model-message equality, equal six HTTP/six model attempts on normal
paths, request budgets/guards/drift, private files, interruption, unattempted counts
and product/status privacy canaries. No real model/Google/Judge request occurred.

## Proposed exact-version Google → agent → renderer round (not executed)

Use the exact delivery commit reported with this PR, after required pytest passes;
reject a changed source/runtime without review. Record HEAD, suite SHA and all code
hashes before execution. The three unchanged definitions are in
`evals/calendar_live_readonly_cases.json`; original criteria/labels stay untouched.

Fixture: existing dedicated-calendar event 2026-10-06 11:00–11:30
America/Los_Angeles (-07:00). Do not create/move events. Three direct preflight
reads must confirm it alone in overlap, and no events in the other windows.

| Fixed case | Actual query, LA -07:00 | Required product (explicit zh-TW for this round) |
| --- | --- | --- |
| live-overlap | 2026-10-06 11:15–11:45 | 不可用；活動原始/轉換區間 11:00–11:30；部分重疊、非完全包含 |
| live-adjacent | 2026-10-06 11:30–12:00 | 可用；相接不重疊，中午 12:00 不誤作午夜 |
| live-empty | 2026-10-06 12:00–12:30 | 可用；完整 query/offset/scope，不虛構活動 |

Keep existing prompts (English/Chinese/English) and explicitly select product
language zh-TW for all three. Normal budget: six Google events HTTP sends (three
preflight + three agent) and six inference requests. Existing hard caps: 12 each,
including retries/pagination/physical auth-retry events sends. OAuth refresh uses
separate uninstrumented auth transport; this is not a cap on all Google HTTP traffic.
No Judge requests, Calendar writes, auto model loading or runtime changes. Require
gpt-oss-20b context8192/temp0/max_tokens2048 unchanged. Estimate 1–3 minutes excluding
OAuth/human review; previous runner round was ~42s.

Stop preflight on OAuth/API failure, unavailable model or fixture mismatch; no
interactive reauthorization under this approval. Block wrong/extra agent reads;
existing runner stops on budget exhaustion, interval drift or incomplete model run.
Completed agent cases with errors/unsupported remain explicit and fail the final
checks; no added conversations, tuning or reruns. Save all partial evidence and
review for anomalies. Compare actual requests/tool selection, Python facts, raw LLM
quality and renderer product separately. Unknown/unsupported is never semantic PASS.

Use a fresh private directory; retain raw evidence locally. Review only allowlisted
deidentified summary for publication, without automatic upload. One round cannot
prove general reliability or real intent accuracy. Rachel must separately approve
these real calls and any PR merge; engineering authorization covers neither.

## Approved live renderer round v1 outcome

Rachel separately approved the fixed three-case plan at commit
`91966489575fa309d2688df435a498e66ccaf4e0`, without approving merge. The round
completed in 16.513 seconds: six actual Google events HTTP sends, six first-attempt
model inference requests, three adapter fixture checks and three agent structural
checks. All events responses succeeded, no interval drift was observed, and runtime
was unchanged. OAuth auth transport remains separate/uninstrumented; six events
sends is not a count of all Google HTTP traffic. No writes, reauthorization, settings
changes, Judge inference, tuning or additional runs occurred.

Actual HTTP query parameters were privately checked against the approved queries;
Python UTC/query/event facts were checked against fixed endpoint references.
Codex-assisted full product review passed for all three: correct reported
availability/scope, dates/offsets, faithful original/converted labels, partial
overlap rather than containment, noon/free and explicit Traditional Chinese.
Renderer status rendered=3 describes eligibility, not independent semantic signoff.
Rachel signoff and the original answer_review fields remain pending; no overall
semantic PASS is asserted and one round is not general reliability evidence.

Raw model prose remains separate/private: overlap supports busy/partial overlap
but omits the explicit query date; adjacent supports free/test-calendar scope with
no specific numerical time defect observed; empty supports free/date/time but omits
explicit dedicated-calendar scope. This does not establish that the original LLM
improved or that historical failures are fixed. Unknown/unsupported runtime paths
were covered offline and were not exercised by this successful live round.

Only the manually inspected allowlisted original summary is committed at
`reports/baseline/calendar-live-renderer-attempt-v1-summary.json`. It contains no raw
answers, product text, dates, offsets, Calendar IDs, URLs or credentials. Raw Google
and agent traces, original/product answers, native runtime manifest and assisted
review remain in the new ignored private directory, with original evidence intact.
No model request captures were added. Implementation hash in the summary ties it
to the unchanged tested source. Keep PR #18 unmerged pending explicit authorization.
