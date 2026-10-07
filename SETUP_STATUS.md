# Setup / verification status

Current checkpoint: October 6, 2026 — v0.1 development preview.

- Local gpt-oss-20b SUT and Qwen judge through configurable LM Studio API.
- Real read-only Calendar availability via Python agent and optional LM Studio MCP.
- 77 deterministic tests passed visibly; saved 15-case SUT trace passed structural checks.
- Judge v5 calibration: 12/12 agreement on tuned development examples; full saved-answer run: 11 raw PASS / 4 raw FAIL. Assisted review found judge mistakes; human signoff is pending.
- Review queue: reports/baseline/CALENDAR_REVIEW_V5.md.
- Event creation is not implemented. Full scheduling scope and complete clean-machine migration checks remain unfinished.
- This is a reproducible development checkpoint, not release acceptance. No GitHub remote/publication.

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
