# Original/converted time display candidate

Independent branch from main checkpoint `c17be48`; does not include PR #10's
overlap/containment candidate. PR #10 remains draft and unmerged. Its approved
paired round exposed incorrect original-versus-converted labels and timezone/noon
presentation defects in both versions. This candidate addresses that presentation
scope without asserting improved semantic reliability.

`with_availability_time_facts` retains the existing conversion and raw event data,
adding `time_facts.presentation` (`calendar-time-display-v1`): a query line and
per-supported-event original/converted strings linked by `busy_index`. Original
strings preserve the exact supplied timestamp/offset, including Z if supplied;
converted/query strings include both ISO 24-hour endpoints and requested IANA zone.
Unsupported/all-day values produce no invented display event. The original facts
version and saved-trace output are unchanged; presentation has its own version.

The SUT prompt requests short labeled lines, translated labels and exact time values
without AM/PM, abbreviations, original-region inference or internal field names.
No output postprocessor rewrites or silently repairs generated answers. The LLM may
still fail to follow these instructions; offline tests do not establish improvement.
Judge rubric, model settings, expected labels and Calendar read-only behavior remain
unchanged. No Google or model inference occurred during implementation.

## Offline validation

194 tests passed, covering original-value preservation, summer/winter, cross-day
conversion, DST endpoints, noon/free-query display, unavailable/all-day conversion,
mixed supported/unsupported event index alignment, Z-preservation and transmission
of display facts to the next model request.

## Proposed new-case paired check — requires Rachel approval

Three controlled cases, each a fresh conversation on old main and this candidate:
six conversations, normally 12 inference requests, estimated 1–3 minutes. Alternate
version order. Record actual code/prompt versions and before/after runtime metadata;
preserve old baselines and save new evidence under new names. No Google or Judge
calls, runtime changes, prompt iteration or automatic additional repetitions.

| Case | Fixture event (original) | Query in requested zone | Expected |
| --- | --- | --- | --- |
| summer-utc-source | 2027-08-19T18:00:00Z to 18:30:00Z | 2027-08-19 11:10–11:20 America/Los_Angeles | Busy; original Z retained; event converted to 11:00–11:30 -07:00 |
| winter-cross-day | 2027-02-18T16:00:00-08:00 to 16:30:00-08:00 | 2027-02-19 08:10–08:20 Asia/Taipei | Busy; original -08:00 retained; event converted to next-day 08:00–08:30 +08:00 |
| noon-free | 2027-02-18T11:00:00-08:00 to 11:30:00-08:00 | 2027-02-18 11:30–12:00 America/Los_Angeles | Free; query ends at 12:00 -08:00, never midnight |

Use English prompts asking to check the stated interval on the dedicated test
calendar and explain conflicts. Synthetic fixtures are public and distinct from
the earlier evaluation cases. Human/assisted full-prose review must assess:

- Tool arguments/resolved interval/availability, independently checked Python
  display values, and generated answer quality as separate phases.
- Exact original source values, correctly labeled converted values, both dates,
  numeric offsets/IANA zone, correct availability and dedicated-calendar scope.
- No invented original region, PST/PDT, noon/midnight confusion or internal keys.
- Free query still reports its full interval/offset. Unsupported events remain
  unknown. No partial-overlap containment regression may be hidden if observed.

All candidate cases must meet these criteria for the small gate to pass. Compare
baseline failures explicitly; a baseline that already passes does not demonstrate
improvement. One paired round cannot establish repeatability/general reliability.
Retain negative evidence. Merge requires separate Rachel authorization.

## Approved paired round v1 — gate not met

Rachel approved the original three-case plan via the review chat. Main remained
`c17be487131d29397373649db22001811664d71c`; tested candidate was
`e9e9e75385fdb4757ccbaa0c0e815dec568d3ff5`. Six fresh alternating-version
conversations completed in 38.319 seconds, with 12 first-attempt inference requests,
zero Google/Judge calls and unchanged runtime (context 8192, temperature 0,
max_tokens 2048). Submitted system-prompt/code/plan hashes and full controlled
answers are in `reports/baseline/calendar-time-label-paired-v1.json`.
Native runtime metadata and request payloads remain in ignored reports/runs/.

Tool structure and independently checked Python time/display facts passed 6/6.
Candidate dates, endpoint values and offsets were numerically correct and no
PST/PDT or internal keys appeared. Both busy cases included original/converted
endpoints, whereas baseline omitted original ends and summer used PDT. However,
both candidate busy answers omitted the availability conclusion, conflict
explanation and dedicated-calendar scope. These omissions are answer regressions
relative to baseline's explicit busy conclusion. Candidate also reformatted ISO
values with Unicode hyphens/spaces (winter removed T), violating exact copying.
Noon/free remained correctly available on the dedicated test calendar; baseline
already rendered noon correctly, so no noon-fix claim is supported.

The complete candidate semantic gate passed 0/3. These are Codex-assisted findings,
not Rachel semantic signoff. Presentation gains do not establish full answer
quality improvement. No prompt tuning, extra repetitions or label changes occurred.

Recommendation: keep both #10 and #11 draft/unmerged as diagnostic evidence,
preserving branches and reports. Do not combine independent candidates and assume
their separate tests cover the combined version. Scope a later candidate around
preserving availability/scope while rendering time facts; do not implement or run
it without further approval. Defer selection of a live-test candidate until review.
