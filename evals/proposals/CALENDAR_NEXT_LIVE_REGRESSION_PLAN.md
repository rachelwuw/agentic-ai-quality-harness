# Proposed next live Calendar regression — not approved for execution

## Version decision first

Main checkpoint `c17be48` has the merged PR #9 runner and 193 passing offline
tests. PR #10 did not demonstrate semantic improvement; PR #11's time-label
candidate omitted busy conclusions/scope in both busy transfer cases. Recommend
retaining both candidates draft/unmerged. Do not combine them without testing the
new combined implementation. No candidate is selected for adoption by this plan.

Before requesting live execution, Rachel must review which exact commit to test.
Use unchanged main only if the purpose is explicitly a reference/integration check;
that would not validate an unmerged candidate or demonstrate a fix. A future
candidate must first meet its controlled-answer gate, preserve negative evidence,
and record exact code/prompt hashes. Reconfirm scope if runner/fixture/settings change.

## One round using the existing runner

After version selection and separate approval, use the existing three fixed cases
in `evals/calendar_live_readonly_cases.json`: overlap, endpoint adjacency, empty.
No new fixture writes or general calendar queries. Validate the existing dedicated
calendar fixture with three adapter reads before three fresh SUT conversations;
if preflight fails, stop and retain failure evidence rather than editing events.

- Expected: six Google events HTTP sends and six local model inference requests.
  Existing hard caps: 12 each including physical sends/model retries. OAuth refresh
  traffic is separate and not independently measured by this events budget.
- Estimated runner time: 1–3 minutes; earlier round took 41.826 seconds, excluding
  OAuth and human review. Timeouts/retries may lengthen or stop the run.
- Keep gpt-oss-20b, context 8192, temperature 0/max_tokens 2048 and runtime unchanged.
  Model must already be ready; no auto loading, configuration changes, Judge calls,
  additional runs or prompt/label tuning. OAuth-only interactive recovery needs
  separate approval if existing authorization cannot refresh.
- Use explicit `--live-readonly` with a new private directory under reports/runs/;
  never overwrite previous evidence. Capture before/after runtime and code hashes.
  Raw answers/traces/manifest stay private, with existing restrictive permissions.
  Publish only manually inspected allowlisted deidentified summaries.

## Separate review and stopping conditions

Report actual HTTP/tool execution and fixture drift, Python computed time facts,
and final-answer quality separately. Read-only success never implies semantic PASS.
Review query versus event interval, partial overlap versus containment, original
versus converted labels, both dates/offsets, explicit free/busy conclusion and
dedicated-calendar scope. Judge stays advisory and is not invoked in this round.

Interrupted/unattempted/error cases remain distinct from evaluated failures. Do not
rerun until green, change expected labels or hide failures. One round cannot show
repeatability or general reliability. Any code adoption/merge still requires the
task-branch → push → PR → required pytest → separately authorized merge workflow.

This plan does not authorize Google/model execution, Calendar writes or PR merging.
