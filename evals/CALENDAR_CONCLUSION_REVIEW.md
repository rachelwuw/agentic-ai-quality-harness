# Calendar conclusion-preservation candidate

New independent branch from main `c17be48`. Reuses only PR #11's implementation
checkpoint `e9e9e75` display facts/tests and adds a conclusion contract. Neither
PR #10's relationship flags nor PR #12's documentation is included. #10/#11's
branches and original negative reports remain untouched and unmerged. Reuse does
not mean the new combined candidate inherits #11's model-validation result.

## Change and limits

`with_availability_time_facts` adds `presentation.conclusion` under display version
`calendar-time-display-v2`, based solely on the adapter's explicit boolean result:
available/unavailable/unknown on the dedicated test calendar. Unsupported conversion
never overrides availability. The agent is instructed to answer the conclusion
first in the user's language, then the query and supported event time lines, and
explain conflicts. Free answers omit empty event rows. Busy alone does not imply
containment. No generated answer is postprocessed or silently repaired.

Original timestamp/display behavior, saved-trace facts, existing expected labels,
Judge rubric, model configuration, read-only Calendar behavior and old baselines
are unchanged. The conclusion is reported tool evidence, not independent calendar
verification or guaranteed truthful generated prose.

197 offline tests passed. Tests check exact reported available/busy/unknown states
despite unsupported all-day conversion, scope in the conclusion, display conversion
and preservation from #11, and transmission to the next model message. Scripted
responses establish transport; no model/Google call has occurred for this candidate.

## Proposed paired experiment — not yet approved

Compare PR #11 implementation `e9e9e75` and this candidate on three new controlled
cases, a fresh conversation per version/case, alternating order: six conversations,
normally 12 inference requests, estimated 1–3 minutes. This isolates whether the new
conclusion changes the prior candidate's omission behavior; main is not represented
by the PR #11 baseline. Freeze and record exact code/prompt hashes before execution.
Keep gpt-oss-20b, context 8192, temperature 0 and max_tokens 2048 unchanged; no Google,
Judge, extra repeats, prompt tuning or runtime changes. Save a fresh report, all
answers/errors and an independent Python fact check; do not overwrite older evidence.

| Case | Original fixture event | Query | Expected |
| --- | --- | --- | --- |
| winter-busy | 2027-12-08T19:00:00Z to 19:30:00Z | 2027-12-08 11:10–11:20 America/Los_Angeles | Unavailable; event converted to 11:00–11:30 -08:00 |
| summer-partial-cross-day | 2027-07-09T16:00:00-07:00 to 16:30:00-07:00 | 2027-07-10 07:15–07:45 Asia/Taipei | Unavailable; event next day 07:00–07:30 +08:00; partial overlap, not containment |
| noon-free | 2027-09-16T11:00:00-07:00 to 11:30:00-07:00 | 2027-09-16 12:00–12:30 America/Los_Angeles | Available; explicit noon query, numeric -07:00, no invented event |

Use identical English prompts asking to check the interval on the dedicated test
calendar and explain any conflict; do not instruct the user prompt to demand the
new conclusion format. Candidate gate requires all three complete answers to give
the correct explicit availability conclusion and scope, correct query/event values,
faithful original/converted labels, IANA zone/numeric offsets and correct relationship,
without PST/PDT, invented source regions, internal keys or omitted time endpoints.
Retain the existing exact-copy display requirement; assess any Unicode reformatting
separately from numerical correctness and do not silently relax the gate.

If PR #11 already passes these new cases, do not claim demonstrated improvement.
One round cannot establish repeatability/general reliability. Keep failed evidence
and do not rerun until green. Model execution and merge each require Rachel approval;
a future Google regression requires its own selected-version plan and authorization.

## Approved paired round v1 — local gain, full gate not met

Rachel approved merging documentation PR #12 and executing this six-conversation
study, not merging #13. Main became `ae2e311`; #13 was updated with its documentation
and required pytest passed before inference. Source/prompt files remained byte-equal
to implementation `01cf14c`. The tested candidate commit was
`d90772256e43180c3d3674c5a191254e868686b9`; comparator remained PR #11 `e9e9e75`,
which is a prior candidate, not main. The original preparation scope above describes
the pre-documentation-merge state. Cases, expectations and runtime were unchanged.

Six fresh alternating-version conversations completed in 40.05 seconds, with 12
first-attempt inference requests, zero Google/Judge calls and unchanged runtime.
Tool structure and independent fixed-fixture Python/display verification passed
6/6. Full controlled answers, code/prompt/plan hashes and assisted review are in
`reports/baseline/calendar-conclusion-paired-v1.json`; native runtime/request metadata
remain in ignored reports/runs/.

| Assisted criterion | PR #11 | #13 candidate |
| --- | --- | --- |
| Explicit correct availability conclusion | 1/3 | 3/3 |
| Explicit dedicated-calendar scope | 0/3 | 3/3 |
| English answer matching English request | 3/3 | 2/3 |
| Busy conflict explanation | 0/2 | 0/2 |
| Exact display-value copying | 1/3 | 0/3 |
| Complete gate | 0/3 | 0/3 |

Candidate restores busy conclusions/scope in both matched busy cases, a local
criterion gain. However, busy answers still omit a conflict/overlap explanation,
Unicode date hyphens break exact copying, and noon-free unexpectedly answers in
Spanish (including translating the interval separator). Numerical dates/offsets
remain correct. The Spanish conclusion is semantically correct, but fails the
user-language requirement; these dimensions are not conflated.

No labels, gate or prompt were changed, no results were repaired, and no extra runs
were performed. Findings are Codex-assisted, with Rachel semantic signoff pending.
Keep #13 draft/unmerged for review: this round supports availability/scope delivery
improvement only, not complete answer reliability or repeatability. No further
candidate or live Google execution is approved by this outcome.
