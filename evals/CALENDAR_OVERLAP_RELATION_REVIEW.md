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

## Approved paired round v1 outcome

Rachel approved execution. Eight fresh conversations completed in 59.405 seconds,
with 16 first-attempt inference requests, zero Google calls and unchanged runtime.
Alternating version order by case reduced a simple ordering confound. Baseline was
`c17be487131d29397373649db22001811664d71c`; candidate was
`b4e86292ce75a468d465b3af32ff439af7ebb7cb`. Controlled full-answer evidence and
submitted system-prompt hashes are in
`reports/baseline/calendar-overlap-paired-v1.json`; runtime metadata/request payloads
remain in the ignored `reports/runs/calendar-overlap-paired-v1/` directory.

- Tool structure: 8/8 passed. Python times and candidate relationship flags were
  independently compared against the fixed fixture/query endpoints, without using
  the relationship helper as the verification oracle: 8/8 verified.
- Both versions gave correct availability and neither described partial overlap as
  full containment in this round. Candidate explicitly distinguished partial overlap
  from containment, but the baseline defect did not reproduce. Improvement is not
  demonstrated; the inside/adjacent controls were not contradicted on availability.
- Candidate still used PST on three busy cases, mislabeled recomputed UTC values as
  original timestamps on partial-left/inside, and omitted the offset on adjacent.
  Inside also exposed an internal flag name in prose. Baseline retained related
  source-label issues and rendered adjacent's noon endpoint as 12:00 AM.
- The complete semantic acceptance gate was **not met**. These are Codex-assisted
  findings, with Rachel semantic signoff pending; no Judge inference, additional
  repetitions, prompt tuning or Google rerun occurred. Keep PR unmerged for review.

Next decision: review whether the candidate facts warrant retaining as infrastructure,
then separately scope original-versus-converted labeling and answer presentation.
Do not claim this one paired round establishes a reliability improvement.
