# Offline interval relationship sidecars

This selectively reuses #10's deterministic interval math, not its prompt/tool
payload additions. The original failed experiment and reports remain untouched.
It is evidence infrastructure, not a fix for model answers. Renderer implementation,
model/Google/Judge execution and PR merge are outside this task's authorization.

## Why a separate path?

`calendar_judge.review(..., derive_facts=True)` sends `derive_trace_facts(item)`
as `computed_trace_facts` to the Judge. Adding containment to that legacy output
would change model input even without changing the rubric or prompt. Instead:

```text
saved trace → derive_trace_facts (existing v1 shape)
                 ├→ existing Judge input, unchanged
                 └→ derive_interval_relations → new offline sidecar only
```

`trace_facts.interval_relationship` is a shared arithmetic consumer: the legacy
facts builder uses its overlap value only, preserving existing output; the offline
consumer uses both overlap and per-event containment. Both reuse `interval()` for
offset/order validation and UTC conversion. Model-facing availability tool facts,
system prompt, agent loop and Judge remain unchanged. No unused helper or second
timezone conversion implementation is introduced.

## Offline use

For an existing saved evaluation envelope with unique case IDs and boolean
`structural_pass` values (the existing `validate_source` contract):

```sh
python -m harness.interval_relations \
  --input reports/baseline/calendar-evaluation-post-fix-baseline.json \
  --output reports/runs/interval-relations-new.json
```

The CLI imports no model/Calendar client, uses no network and does not grade prose.
It refuses an existing output or an output matching the input; new output files
are owner-readable/writable (0600). Analyze private traces only into private local
directories; do not commit their sidecars. Existing commands and report files are
not changed. No automatic sidecar ingestion is added to any Judge/model path.

New schema: `calendar-offline-interval-relations-v1`, with source SHA-256 at the
CLI envelope level, and `source_facts_version` in each result. Observations carry
saved `event_index`, `reported_available`, issues and per-event `busy_index` flags:

- `overlaps_query`: strict half-open overlap; touching endpoints are false.
- `query_fully_within_event`: this individual event contains the whole query;
  equality and shared-endpoint containment count. Query surrounding a shorter
  event overlaps but is not contained by that event.
- Both flags are null with an issue when query/event evidence is unavailable,
  malformed, naive, non-positive, all-day/unsupported, or the tool reports an error.

Multiple events are evaluated separately: there is no union coverage calculation.
A missing/malformed busy array stays null with a diagnostic; a recorded empty list
stays empty. Neither implies free. `reported_available` remains saved reported
evidence, not a newly inferred availability or an independent API verification.
Missing/invalid display timezone does not invalidate a known offset-bearing UTC
instant; relations do not require inventing a timezone.

## Compatibility evidence

- Main `f073b0c` versus this change: v1 `derive_trace_facts` outputs matched on all
  109 public saved trace records inspected in tracked evals/baseline JSON files.
- A regression test freezes the entire Judge message payload captured on that main
  checkpoint using a fake completion function. Calling the offline consumer first
  must not mutate source evidence or change the captured messages.
- Existing v1 facts/tool schema versions remain unchanged. Only the new offline
  sidecar has a new schema/version; no historical reports are recomputed/overwritten.
- Boundary/unknown/CLI tests run offline, including a socket guard. They establish
  deterministic behavior and input compatibility, not semantic model reliability.

After this small PR is reviewed and separately approved, renderer design can be
considered as its own task. This change does not authorize expanding into it.
