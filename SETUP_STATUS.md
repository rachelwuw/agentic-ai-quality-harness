# Setup / verification status

Current checkpoint: October 8, 2026 — v0.2 Development Preview.

- GitHub repository: [rachelwuw/agentic-ai-quality-harness](https://github.com/rachelwuw/agentic-ai-quality-harness). Prior code checkpoint `3b97db3` was pushed to `main`. The v0.2 work follows it; a local commit does not imply a GitHub push.
- Local gpt-oss-20b SUT and Qwen judge through a configurable LM Studio API, loaded in turn.
- Real read-only Calendar availability via Python agent and optional LM Studio MCP. October 7 live Python regression verified overlap, adjacency and free intervals against Google; all three availability conclusions were correct, but overlap omitted explicit test-calendar scope. Raw live traces and assisted review stay in ignored `reports/runs/`; no live failure/retry or MCP-host regression was performed.
- 108 deterministic tests passed in the latest recorded visible VS Code Terminal run. Transport retries and the Python correction budget are implemented; Judge remains single-attempt.
- The latest controlled 15-case SUT baseline completed after prompt/retry changes: 14/15 strict structural passes, with successful one-correction recovery on cal-06. Assisted review identified remaining language, scope, time-zone wording and DST issues; semantic review is pending. See [new baseline review](reports/baseline/CALENDAR_BASELINE_V7_RETRY_REVIEW.md).
- Latest full v7 Judge review: 15 valid outputs, 11 raw PASS / 4 FAIL; combined 10 PASS_PROVISIONAL / 5 FAIL including cal-06 structural failure. Thinking observed at 1009–1024 tokens; about 46m41s generation time. Known criterion errors and coverage gaps remain. [Evidence review](reports/baseline/CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md).
- Historical full v5 judge reviews: budget=0 returned 11 raw PASS / 4 FAIL; Thinking returned 10 raw PASS / 5 FAIL. Neither is semantic signoff.
- v6 focused synthetic check matched 4/4 expectations, but original cal-08 was still falsely failed. cal-10 correctly failed under the confirmed missing-duration policy.
- v7 split interval criteria and explicit reference facts: original cal-08 and two positive/negative examples matched 3/3 expectations. Development validation, not held-out accuracy or Rachel's individual answer signoff.
- Judge v8 implemented: external-request fact graded from trace; timezone wording criteria added. 101 deterministic tests passed in 3.50 seconds. Four synthetic Qwen cases completed on October 8 with valid outputs and 4/4 matching authored expectations; about 11m11s. This is focused development evidence, not overall accuracy. [Plan](evals/JUDGE_V8_VALIDATION.md).
- Current evidence: [baseline index](reports/baseline/README.md). Source answer-review statuses remain pending.
- Event creation, full dependency locking, expanded doctor checks and clean-machine Mac Studio validation remain pending.

Latest v10 evidence: Python derives time/tool facts; Qwen judges claims. Two reused positive controls passed; four fresh cases matched 3/4 overall and 31/36 criterion expectations, including a false FAIL with contradictory reasoning. Full v10 baseline and human signoff are pending. [Review](reports/baseline/JUDGE_V10_FRESH_REVIEW.md).

The dated entries below are historical records; earlier counts and next steps describe their date, not current completion.

- Project: /Users/rachelwu/dev/agentic-ai-quality-harness.
- Python 3.12.14 virtual environment, Git repository, and VS Code Python setup prepared.
- 21 deterministic pytest tests previously passed using scripted model responses.
- Two mock tools and 15 initial evaluation cases prepared.
- One gpt-oss-20b MXFP4 GGUF artifact installed and SHA-256 verified; temporary download parts removed.
- LM Studio GUI loaded the model and produced a local chat response.
- Missing LM Studio internal temp directory repaired.
- Local API started on http://127.0.0.1:1234 with local-network serving disabled.
- Python harness doctor successfully listed openai/gpt-oss-20b.
- First real agent run completed: get_requirement(REQ-2), then run_test_suite(reset), then final answer.
- Model accurately reported mock passed=2 and failed=1, but used “Failed: 1” instead of the requested literal “failed=1”. This is a formatting finding, not a failed tool execution.
- Original trace: reports/first-live-run.json.
- Full 15-case QA prototype evaluation baseline remains pending; these cases do not cover Calendar behavior.
- No GitHub remote or publication yet.

The model is real and local; tool results are fixed mock data. A completed run does not imply every evaluation criterion passed.

## Approved new scope — October 5, 2026

- System Under Test: Calendar Scheduling Assistant with real availability lookup and event creation.
- Dedicated test calendar; own single events only; explicit confirmation before creation.
- Preserve the local model, custom loop, trace, and deterministic mock testing approach.
- Add real Calendar integration tests and scheduling evaluations incrementally.
- README.md, PROJECT_SCOPE.md, and ARCHITECTURE.md updated to the approved direction.
- No Calendar code, OAuth setup, or account connection has been implemented in this documentation update.
- Next: configure Google Calendar API authorization and identify the designated test calendar.


## October 5, 2026 — Google Calendar read-only connection

- Dedicated private test calendar and Google Cloud Calendar API configured.
- Desktop OAuth client stored outside the repository; OAuth completed in the browser.
- Installed optional Calendar authorization dependencies in the project virtual environment.
- Ran `python -m harness.calendar_setup` visibly in VS Code Terminal.
- Real Calendar API read succeeded: 0 events in the next 7 days. No events created or modified.
- Read-only scope: `calendar.events.owned.readonly`; token stored outside the repository with owner-only permissions.
- Existing 21 deterministic QA prototype tests still pass; this does not validate Calendar scheduling behavior.
- Next: implement the first real `check_availability` tool and then connect the scheduling agent loop. Event creation and confirmation logic are still planned.


## October 5, 2026 — Real availability tool

- Implemented `CalendarTools.check_availability` in `src/harness/calendar_tools.py`.
- Verified in visible VS Code Terminal: 37 deterministic tests passed (21 existing QA tests + 16 new Calendar tests).
- Real Google read for October 6, 2026, 10:00–10:30 America/Los_Angeles (UTC−07:00): `available: true`, empty busy intervals.
- No events created or modified. Only the configured test calendar was checked.
- Live conflict detection against an actual busy event has not yet been verified; conflict handling currently has simulated API coverage.
- Scheduling agent/model integration, write permission, confirmed creation, and Calendar evaluations remain planned.


## October 5, 2026 — Local model + real Calendar tool

- Added `calendar_agent.py`, reusing the custom loop through injectable system prompt, tools, and executor.
- 41 deterministic tests passed visibly in VS Code Terminal.
- Ran a real Chinese availability question through gpt-oss-20b at `127.0.0.1:1234/v1`.
- Model called `check_availability` with the correct October 6, 2026, 10:00–10:30 UTC−07:00 timestamps.
- Real Google Calendar returned available=true with no busy intervals; model correctly answered that the test calendar is free.
- Trace: `reports/calendar-agent-first-live.json`. No events created or modified.
- This is one successful live case, not a full Calendar evaluation suite. Clarification, live conflicts, and adversarial behavior remain to evaluate. Confirmed event creation is still planned.


## October 5, 2026 — LM Studio chat MCP connection

- Optional official MCP Python SDK installed (1.30.0).
- Configured local stdio server `rachel-calendar-readonly`; previous empty LM Studio MCP configuration backed up.
- Exposes only `check_availability` and `get_current_time`; no write tool.
- LM Studio Integrations enabled and a real Chinese query completed through MCP on the configured test calendar.
- Correct UTC conversion observed: October 6, 10:00–10:30 Los Angeles → 17:00–17:30 UTC.
- Model reported free time; no event writes. Approval remains per tool call.
- 44 deterministic tests passed in the visible VS Code Terminal.
- LM Studio owns this chat loop; Python harness traces remain a separate entry point.


## October 5, 2026 — First live Calendar QA review

- Created one busy UI fixture on Agentic Harness Test: October 6, 11:00–11:30 America/Los_Angeles. Agent permissions remain read-only.
- Three real local-model cases: overlap FAIL, adjacency FAIL due to wrong queried interval, missing-information clarification PASS.
- Model used UTC−08:00 instead of UTC−07:00 for both explicit October Los Angeles intervals.
- Correct-offset direct real API checks passed: overlap busy, exact adjacency free.
- Details and original trace locations: LIVE_CALENDAR_REVIEW.md. Fixture retained for repeatable tests.
- Next: fix and regression-test time-zone conversion before event creation.


## October 5, 2026 — Time-zone regression fixed

The Python agent and MCP adapter now accept local `YYYY-MM-DDTHH:MM:SS` start/end values plus an IANA `time_zone` (for example, `America/Los_Angeles`). Python `zoneinfo` resolves UTC offsets before the Calendar API call. Offset-bearing local input, invalid zones, DST gaps, and ambiguous DST folds are rejected; the assistant must clarify rather than guess. The low-level Calendar CLI still accepts explicit RFC3339 instants.

Validation: 52 deterministic tests passed, including summer/winter offsets, rejected wrong-offset input, DST gaps/folds, and a DST-crossing interval. Real local-model reruns correctly queried October 6 with UTC−07:00: 11:15–11:45 busy; 11:30–12:00 free. Traces: `reports/calendar-overlap-fixed.json` and `reports/calendar-adjacent-fixed.json`. These validation runs used background execution after visible Terminal control became unavailable. No calendar writes occurred.

Restart the `rachel-calendar-readonly` MCP integration (or LM Studio) and begin a new chat to load the updated tool schema. The Python entry point is live-tested; the reloaded LM Studio chat entry point has deterministic adapter coverage but has not yet been live-retested. Model interpretation of dates/times still needs broader evaluation.


## Calendar evaluation runner

- Added controlled Calendar runner with real local model, frozen clock, structural graders, per-case traces, incremental progress saving, and pending manual semantic review. No Google API access.
- 56 deterministic tests passed. Three real-model smoke cases (cal-01 overlap, cal-03 adjacency, cal-10 missing duration) passed structural checks; report: reports/calendar-evaluation-smoke.json. Full 15-case baseline remains pending.
- Verification ran in the background, not in the visible VS Code Terminal.


## Format-error feedback repair

- Model-facing validation now distinguishes invalid formatting, invalid dates/zones/intervals, and DST clarification. Formatting feedback includes a valid example and explicit cross-midnight support; the agent is instructed to retry formatting without changing user intent. Shared MCP validation returns the same structured errors before connecting to Google.
- Verified visibly in VS Code Terminal: 58 deterministic tests passed, including a scripted malformed-then-corrected cross-midnight retry and DST clarification without API calls.
- Real local-model controlled reruns cal-06/cal-13/cal-14 passed structural checks 3/3; trace: reports/calendar-format-feedback-fixed.json. Full baseline not rerun. Semantic DST explanations still require improvement. LM Studio MCP must be restarted to load the changes; GUI entry point not live-retested.

Original-answer follow-up: v8 correctly failed cal-03 but still passed cal-08 despite its false conversion claim. Two valid single-attempt outputs, about 4m58s. [Review and preserved raw results](reports/baseline/JUDGE_V8_ORIGINAL_CASE_REVIEW.md). Judge reliability remains unresolved.

- v9 focused validation completed: 101 pytest tests passed in 3.40s; three valid single-attempt Judge outputs matched authored expectations (FAIL/PASS/PASS), about 9m36s. [Review](reports/baseline/JUDGE_POLICY_V9_VALIDATION.md). This is development validation; human signoff and broader reliability remain pending.

Frozen v9 new-wording validation completed: 4 valid outputs, 3/4 authored aggregate matches, one false PASS on a contradictory Chinese event interval and additional criterion-level errors. [Evidence review](reports/baseline/JUDGE_V9_NEW_WORDING_REVIEW.md). Judge remains advisory; no overall reliability or human signoff is established.

Criterion-level diagnostic: 36 authored labels, 31/36 original batch matches. Four selected failed checks scored separately matched 3/4; one contradiction check still misses. This is failure-selected development evidence, not accuracy. [Comparison](reports/baseline/JUDGE_V9_CRITERION_COMPARISON.md). Default scoring mode is unchanged; Judge remains advisory.

- v10 adds Python-computed time/tool trace facts for semantic review. 108 pytest tests passed; two known-negative single checks scored FAIL/FAIL as expected under unchanged model/budget settings. [Review](reports/baseline/JUDGE_V10_TRACE_FACTS_REVIEW.md). Positive controls and broader reliability remain pending; Judge stays advisory.
