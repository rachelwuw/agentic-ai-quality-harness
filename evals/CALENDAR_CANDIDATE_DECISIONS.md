# Calendar candidate convergence decision

This is an evidence/decision checkpoint, not adoption of candidate code. Main
remains the merged read-only implementation from #8/#9 plus documentation #12.
No model or Google/Judge calls were made for this review, and no old report was
edited. Historical review documents retain the state and recommendations at the
time of their experiments; this decision document supplies the current disposition.

## Disposition

| PR | Decision | Reason |
| --- | --- | --- |
| #10 | Close as completed diagnostic experiment; retain branch and evidence | Correct deterministic relation facts, but baseline containment failure did not reproduce and full semantic gate failed. No demonstrated answer improvement. |
| #11 | Close as superseded experiment; retain branch and evidence | Time presentation helped some dimensions but omitted busy conclusions/scope. #13 already reuses its implementation; no reason to maintain #11 as a separate active candidate. |
| #13 | Sole remaining draft candidate; do not merge as a complete fix | Paired comparison against #11 improved explicit availability 1/3→3/3 and scope 0/3→3/3; full gate remains 0/3, with explanation omissions, formatting failures and Spanish output for an English request. |

Closing a PR does not merge/delete its branch or erase results. Retaining #13 does
not commit to adoption or authorize further tuning/runs. Do not open another
independent SUT candidate until this candidate's disposition and next scope are
agreed. An evidence-only PR can be reviewed separately without changing SUT behavior.

## What is worth retaining or considering for selective adoption?

| Component | Recommendation | Verification and limits |
| --- | --- | --- |
| #10 `trace_facts.interval_relationship` and boundary tests | Reusable deterministic infrastructure; strongest selective-adoption candidate | UTC comparisons distinguish overlap/containment and adjacency. Prefer a separately scoped infrastructure change with offline checks; no claim that the prompt fixes prose. Do not mix this into #13 now. |
| #10 relationship prompt additions | Retain as experimental evidence; do not adopt whole prompt | Correct Python facts reaching the model did not establish a semantic gain in the paired round. |
| #11/#13 `with_availability_time_facts` display strings and preservation tests | Preserve implementation/tests, but adoption remains conditional | Uses existing conversion, original offsets and stable busy indices. Output still reformats values; added display text can affect model behavior. Not independently established as better than main across the full contract. |
| #13 `presentation.conclusion` and availability/unknown tests | Retain as the current candidate's useful idea | Preserves reported boolean/unknown and scope despite unsupported event conversion. Local conclusion gain is against #11, not a direct comparison with main. Duplicate tool facts do not guarantee faithful prose. |
| #11/#13 strict time-only/exact-copy prompt bundle | Do not adopt as a complete fix | #11 omitted core conclusions; #13 repairs those locally but still omits explanations and regresses language in one case. Keep exact-copy failures separate from numeric time correctness. |
| Full controlled reports, code/prompt hashes and review criteria | Preserve centrally now | Negative results and local gains remain inspectable even if candidate PRs close. Assisted review is distinct from Rachel semantic signoff. |

No implementation listed above is adopted by this document. Code adoption still
requires a concrete scoped diff, relevant offline checks, and any separately
approved model evidence, followed by required CI and authorized merge. Deterministic
infrastructure may be worthwhile on its own; it need not be sold as a semantic fix.

## Preserved original evidence

These files are copied byte-for-byte from the named source commits, including all
answers/failures. Only previously public synthetic controlled evidence is copied;
private Google traces, credentials and native runtime/request metadata remain local.

| Experiment | Source commit | Review | Full controlled results |
| --- | --- | --- | --- |
| #10 overlap | `60a6a006790d4a964c3ed065703b058a120b4aca` | [Review](CALENDAR_OVERLAP_RELATION_REVIEW.md) | [Results](../reports/baseline/calendar-overlap-paired-v1.json) |
| #11 display | `56f11ed890de8165f2885be2d5894cfed6b4f525` | [Review](CALENDAR_TIME_LABEL_REVIEW.md) | [Results](../reports/baseline/calendar-time-label-paired-v1.json) |
| #13 conclusion | `4f10da6c3e60387382b90a8d1b19302ff95839e1` | [Review](CALENDAR_CONCLUSION_REVIEW.md) | [Results](../reports/baseline/calendar-conclusion-paired-v1.json) |

Each experiment uses different cases/comparators. Do not pool their gate counts as
an accuracy metric: #10/#11 compared with old main; #13 compared with #11 candidate.
One paired round does not establish repeatability or general reliability. Do not
rewrite labels, relax the frozen gates or rerun until green.

## Single next decision

First review this evidence-only checkpoint. Then decide whether to continue #13
as the single answer-contract candidate or retire it too. The required contract is
explicit availability/scope, correct query and original/converted event facts,
relationship explanation and user language. A new prompt, parser or deterministic
renderer is not authorized by this convergence review. Future changes should be
evaluated as one exact version rather than combinations of independently tested
branches. Defer Google regression until that version is selected and approved.
