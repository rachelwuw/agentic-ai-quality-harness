# Approved wording comparison — October 12, 2026

The authorized 24 single-attempt requests have been executed: 23 yielded valid judgment JSON, one returned a transport HTTPError. On 99 round-matched criterion pairs available in both arms, original and clarified each match 93 approved labels. There are zero observed label improvements and zero regressions. This small study does not demonstrate that replacing the ambiguous sentence improves semantic reliability.

Rachel approved exact A-F answers, fixture facts and expected labels, then separately authorized 24 requests. These approvals cover inputs and execution, not outputs, default activation, release signoff or merging PR #4. This report is Codex-assisted evidence review awaiting Rachel's review.

## Controlled change and execution

Original c6/c7 end in `No conversion claim satisfies this check.` Clarified replaces that sentence with `If the answer makes no event-conversion claim, return PASS for this check.` Other criterion text, answers, tool records, Python facts, system prompt, aggregation and settings are shared. Default v10 remains unchanged. The explicit opt-in version is calendar-answer-v12; this is an independent branch based on main and does not merge the v11 PR.

Case order A/D/B/E/C/F in all blocks. Arm order original-1, clarified-1, clarified-2, original-2 (ABBA). Each request has a fresh conversation and no retry. This balanced order limits simple time confounding but does not eliminate order/cache or environment effects. Cases remain same-author synthetic development controls, not new SUT answers or independent benchmark data.

Runtime: Qwen/qwen3.5-9b Q8_0; LM Studio 0.4.25+1; context 8192; UI Thinking on, enabled reasoning budget 1024; temperature 0; strict JSON; max output 6144; timeout 600. All 23 valid responses reported 1024 reasoning tokens. Server parallel capacity is 4 but calls were sequential. No Google requests, SUT generation, outcome-driven tuning or replacement calls occurred.

## Transport interruption and continuation

Request 23 (original round 2, C) failed with HTTPError after 195.556 seconds. The existing judge records `judge_error` / `transport_error`, null raw output and unavailable reasoning metadata. The study guard stopped before F. HTTP status/body and root cause were not captured; do not describe this as a confirmed timeout or a semantic failure.

After the user's continue instruction, the server was running and idle; API runtime metadata matched the initial manifest, hashes remained unchanged, and UI Thinking/budget were reverified. Only unattempted request 24 (original round 2, F) was executed. Failed C was not retried. This gap limits uninterrupted-session conclusions even though recorded configuration matches.

The original `original-round2.json` remains untouched with state `blocked_runtime` and five results. `resumed-original-round2.json` copies those exact five results and appends only F. The continuation audit records original file hash, pre-resume configuration and authorization. Completion records exactly 24 attempts. The comparator verifies the unchanged prefix and selects the resumed report without counting duplicate records. All original and resumed files are preserved.

## Results and denominators

| Measure | Original | Clarified |
| --- | --- | --- |
| Attempted / planned requests | 12/12 | 12/12 |
| Valid outputs | 11/12 | 12/12 |
| Operational transport errors | 1 | 0 |
| Valid semantic UNCERTAIN | 0 | 0 |
| Overall matches, planned denominator | 11/12 | 12/12 |
| Overall matches, valid-only denominator | 11/11 | 12/12 |
| Criterion matches, planned denominator | 93/108 | 102/108 |
| Criterion matches, valid-only denominator | 93/99 | 102/108 |
| Repeat overall labels | 5/5 available; one pair unavailable | 6/6 |
| Repeat criterion labels | 45/45 available; nine pairs unavailable | 54/54 |
| Request time sum | 2071.310 seconds | 2291.187 seconds |
| Median request | 178.2805 seconds | 191.327 seconds |
| Maximum / exploratory nearest-rank p95 | 203.450 seconds | 213.396 seconds |

Total recorded request time: 4362.497 seconds (72m42.497s), excluding setup, review and interruption gap. The maximum/p95 values are exploratory with only 12 observations per arm. Neither arm produced an overall false PASS or false FAIL among valid outputs. Missing C is operationally unavailable, not a correct or incorrect semantic label.

**Common available comparison:** 99/108 round-matched criterion pairs; 93/99 matches for each arm; improvements 0, regressions 0, unavailable pairs 9. The apparent 102 versus 93 difference on planned totals is entirely the missing original C judgment, not observed semantic improvement. All available criterion labels are equal across arms and repeat rounds. Available repeated raw JSON strings are identical within arm (original 5/5, clarified 6/6), including mistakes.

| Case | Expected overall | Valid outputs in both arms | Persistent disagreements |
| --- | --- | --- | --- |
| A: original LA event, no conversion claim | PASS | PASS | None |
| B: correct winter conversion | PASS | PASS | None |
| C: correct 'In Taipei time' summer event | PASS | PASS; original-2 unavailable | None in labels |
| D: correct target numbers, contradictory LA label | FAIL | FAIL | c7 expected PASS, observed FAIL |
| E: wrong winter clock, correct target attribution | FAIL | FAIL | c6 expected PASS, observed FAIL |
| F: correct opening followed by wrong restatement | FAIL | FAIL | c6 expected PASS, observed FAIL |

## Reason/evidence review

- **D c7:** original reasoning incorrectly associates correct target numbers with LA; clarified reasoning acknowledges numbers match Taipei but still fails because of the LA label. Attribution belongs to c6. Correct overall FAIL hides the c7 error.
- **E/F c6:** both arms score numeric time mistakes under attribution, despite the explicit numeric-only boundary of c7 and the instruction not to score numbers in c6. Clarified E explicitly acknowledges that c6 focuses on attribution and still fails it for numeric mismatch.
- **E c3 contradiction persists in reasons:** clarified c3 is labelled PASS while its reason ends `Thus FAIL.` This repeats in both clarified rounds. The answer's event conversion is confused with the optional query-window conversion. Original E c3 also says the check fails on accuracy while marking PASS and asserting a satisfaction condition. Those reasons are not reliable explanations of the matching label.
- **C conversion interpretation:** both arms pass c6/c7 partly by asserting no explicit conversion claim, although `In Taipei time` expresses the equivalent event in the target zone. The label matches, but this does not establish that an incorrect implicit conversion would be caught. Such a negative is not included here.
- c3 reasons for D/F also confuse event conversion with query-window conversion. Correct labels must not be treated as validation of their reasons.

No raw labels or reasons were repaired. Sentence ambiguity is removed in the clarified input, but this experiment shows no label improvement on these controls. The previous v11 false failures are not causal controls: dates and answers differ. The new original A/B already pass, reducing the study's ability to demonstrate improvement for that earlier failure pattern.

## Recommended decision

Do not activate v12 as a reliability fix or claim Judge accuracy improved. Keep advisory judging and deterministic facts. Preserve this negative result as reviewable evidence; PR #4 remains unmerged.

Before authorizing another long run, agree which output is actually needed: broad factual correctness versus independently trustworthy subcriteria. Current c2 catches the negative cases while narrow c6/c7 scope is not obeyed. The existing [v9 single-criterion diagnostic](JUDGE_V9_CRITERION_COMPARISON.md) already found 3/4 selected failures improved, with a contradiction miss remaining; it did not establish stability. Reuse that existing method only if independent c6/c7 judgments are actually required, with a narrowly scoped extension to these boundaries rather than rebuilding the evaluator. Such an extension would require a separate hypothesis/design, fresh frozen positive and negative labels (including implicit conversion), and an explicit cost bound; it is not implemented or authorized here. No further model requests or model changes follow automatically.

## Evidence and reproduction

- [Study design](../../evals/JUDGE_WORDING_COMPARISON.md)
- [Frozen source](../../evals/judge_wording_cases.json), [approved labels](../../evals/judge_wording_expected_labels.json)
- [Manifest and input/runtime hashes](judge-wording-20261012/manifest.json)
- [Original round 1](judge-wording-20261012/original-round1.json), [original interrupted round 2](judge-wording-20261012/original-round2.json)
- [Clarified round 1](judge-wording-20261012/clarified-round1.json), [clarified round 2](judge-wording-20261012/clarified-round2.json)
- [Continuation audit](judge-wording-20261012/continuation.json), [resumed final block](judge-wording-20261012/resumed-original-round2.json), [completion audit](judge-wording-20261012/execution_complete.json)
- [Full comparison, reasons, confusion counts and repeat pairs](judge-wording-20261012/comparison.json)
- [Exact one-request continuation script, retained as text](judge-wording-20261012/continuation-script.txt)

Offline comparison is reproducible with `evals/compare_judge_wording_study.py` against the preserved directory and a new output path. Replaying inference requires separate authorization and a new run directory. 161 local deterministic pytest tests passed, including request-count/payload/isolated-change guards and unavailable-denominator/regression accounting. These tests make no model or Google calls. CI evidence is separate from semantic evidence.
