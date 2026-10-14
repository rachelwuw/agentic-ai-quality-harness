# Calendar overlap relationship candidate

This candidate addresses the partial-overlap/full-containment wording defect recorded
in `CALENDAR_LIVE_READONLY_REGRESSION.md`. It is not a demonstrated semantic fix.

`with_availability_time_facts` now supplies per-event `overlaps_query` and
`query_fully_within_event`, calculated by shared `interval_relationship` on UTC
instants. Endpoint-only adjacency is not overlap; identical intervals count as
containment. Whole original event intervals, availability, conversion behavior,
Judge rubric, model configuration and existing expected labels are preserved.
Unsupported/all-day events have no relationship flags, rather than guessed values.
The agent prompt instructs use of these facts without equating busy with containment.
Saved-trace analysis keeps its previous output schema and uses the same overlap math.

## Offline acceptance

- Partial overlap on either side and query surrounding event: overlap true,
  containment false.
- Query inside event or equal to event: both true.
- Adjacency on either side and disjoint intervals: both false.
- Compare absolute instants across offsets; preserve original and whole event times.
- Multiple events retain individual flags; no union/coverage claim is calculated.
- Facts reach the next model message. Unsupported events remain unknown.
- Full offline suite: 202 tests passed. Scripted models establish transport only.

## Proposed semantic check (requires Rachel approval before execution)

Start with four controlled cases, each with one fixture event and a fresh SUT
conversation; no Google calls. Use public synthetic dates independent of the live
fixture: event 2027-01-14 11:00–11:30 America/Los_Angeles (UTC-08:00).

| Query | Required semantic relationship |
| --- | --- |
| 11:15–11:45 | Busy, partial overlap; not fully contained (regression shape) |
| 10:45–11:15 | Busy, partial overlap on the other side (transfer) |
| 11:05–11:25 | Busy, fully inside event (positive control) |
| 11:30–12:00 | Free, endpoint-only adjacency (negative control) |

Run old main/checkpoint and candidate against the same four cases for comparison:
eight fresh conversations, normally 16 inference requests, approximately 2–4 minutes
based on previous timings; actual time may vary. Preserve all existing baselines
and save new controlled evidence under fresh names. Freeze runtime configuration
and record prompt/code versions; no prompt iteration on these results.

Review tool execution, Python relationship facts and final prose separately.
A candidate passes this small gate only if partial overlap is never described as
containment, the inside/adjacent controls remain correct, dates/offsets/scope remain
correct, and no phase errors are hidden. Judge remains advisory. One paired round
cannot establish repeatability or general reliability; any broader repeatability
study and real Google rerun need separate approval. PR merge also needs approval.
