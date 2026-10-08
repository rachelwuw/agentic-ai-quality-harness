# Proposed v11 judge boundary study — review before execution

**Design only. No model experiment has been run.** These materials do not activate a new rubric. v10 cases, rubric, labels and raw outputs remain unchanged. Draft answers and expectations are Codex-authored, not Rachel’s human signoff, not new SUT outputs and not a held-out benchmark.

## Why change the boundary

The [frozen v10 fresh report](../../reports/baseline/JUDGE_V10_FRESH_REVIEW.md) records 3/4 overall agreement but only 31/36 criterion agreement. c6 incorrectly failed the correct winter answer while its reason concluded “So c6 should be PASS.” Negative c6 labels also scored clock accuracy allocated to c7. Summer c2 ignored a later contradiction and c3 was uncertain about an allowed omission. Preserve all of those findings; do not change old labels to fit the model.

## Proposed policy requiring Rachel confirmation

| Check | Proposed boundary | Positive example | Negative example |
| --- | --- | --- | --- |
| c6: claim / timezone attribution | A claimed event conversion must be attributed to its claimed target zone. Numeric accuracy belongs to c7. No claimed conversion passes. Attribution may be an explicit label or unambiguous adjacent wording. | “Converted to Taipei: Jan 19, 09:00–09:30 Asia/Taipei.” Also allow correct LA-only event reporting with no conversion claim. | “Converted to Taipei: Jan 19, 09:00–09:30 America/Los_Angeles.” c6 fails because of the label, even if numeric Taipei values are correct. |
| c7: converted date / clock | Compare every claimed conversion’s date and clock against Python facts. An explicit conversion claim establishes the target even if a conflicting display label is present. No claim passes. | Jan 18, 2027, 17:00–17:30 LA converts to Jan 19, 09:00–09:30 Taipei. | Jan 19, 08:00–08:30 Taipei for that winter event: c7 FAIL, c6 PASS. |
| c2: event factual accuracy | Intentionally remains a broader factual check covering every assertion about the event. It can fail alongside c7. Do not infer criterion independence from aggregate FAIL. | All clauses preserve the event instant. | An initially correct conversion followed by a conflicting restatement. |
| c3: optional query conversion | Omitting a query-window conversion satisfies the check. A conversion that is offered must be correct. | Correct event reporting, no LA query-window conversion. | An incorrect LA query-window conversion. |

A reason/verdict contradiction is a separate review defect. Do not repair the verdict automatically or use keyword detection as proof of semantic correctness. Preserve raw JSON, flag the suspected contradiction for assisted review, and require human resolution before treating a disputed label as authoritative. A syntactically valid judgment can still be wrong.

## Reviewable cases and proposed labels

[Draft case traces and exact answers](judge_v11_cases_draft.json) · [Separate expected labels](judge_v11_expected_labels_draft.json). Labels must never be passed to the judge. All fixtures are simulated and authored; no private Calendar data.

| Case | Main contrast | c2 | c3 | c6 | c7 | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| A | Summer event retained in LA; no conversion claimed | PASS | PASS | PASS | PASS | PASS |
| B | Correct winter conversion to Taipei | PASS | PASS | PASS | PASS | PASS |
| C | Correct summer event conversion; optional query conversion omitted | PASS | PASS | PASS | PASS | PASS |
| D | Correct summer target clock numbers, but LA display label contradicts Taipei conversion claim | FAIL | PASS | FAIL | PASS | FAIL |
| E | Wrong winter converted clock, correctly attributed to Taipei | FAIL | PASS | PASS | FAIL | FAIL |
| F | Correct opening conversion followed by a contradictory summer event restatement | FAIL | PASS | PASS | FAIL | FAIL |

Other proposed c1/c4/c5/c8/c9 labels are PASS in every case; exact requirements are included in the draft cases. For D, c7 deliberately checks numeric values for the explicitly claimed Taipei target while c6 catches the contradictory LA attribution; c2 catches the broader inconsistency. Confirm this allocation explicitly. These six cases focus on the identified boundaries, not complete rubric coverage.

## Fixed execution design after approval

- Create a new `calendar-answer-v11` rubric only after policy and label review. Leave the active/default v10 rubric unchanged until explicitly approved. Record source, rubric, system prompt and implementation hashes before running.
- Same Qwen model/quantization as saved v10; record the exact exposed model identifier and artifact/runtime version. Temperature 0; Thinking on; UI reasoning budget 1024; context 8192; strict JSON; max output 6144; per-request timeout 600 seconds. Verify observed reasoning tokens and runtime settings after load. Load SUT and judge in turn; no Google tools or credentials for judging.
- Six saved synthetic answers, two independent single-attempt rounds: **12 requests / 108 expected criterion judgments**. Fixed order A, D, B, E, C, F in both rounds. No conversational carryover, retries, early stopping on green or label tuning between rounds. Keep timeouts/invalid output rather than replacing them.
- Save both rounds to unique ignored run paths. Promote selected sanitized evidence without overwriting earlier reports. A later change needs a new design/version and new validation; these cases become development evidence once inspected.

## Metrics and decision boundary

Report overall false PASS (expected FAIL → observed PASS), false FAIL (expected PASS → observed FAIL), valid semantic UNCERTAIN and operational input/output/transport errors separately. Use approved labels only; otherwise mark comparisons provisional. Show case-level and criterion-level confusion tables, including c2/c3/c6/c7.

Criterion agreement: matching approved labels / 108 planned judgments, with valid-output coverage reported separately; unavailable judgments cannot inflate agreement. Report agreement on valid judgments as a second, explicitly conditional measure. Compare the six repeat pairs overall and all 54 criterion pairs; unavailable pairs are reported, not counted as consistent. Record contradictions between reasons and labels through evidence review, separately from numerical agreement.

Report per-request duration, total duration, median, maximum and exploratory p95 (12 requests is a small sample), observed reasoning/output tokens and timeout counts. A matching aggregate verdict does not establish trustworthy criteria. No automatic release gate or general accuracy claim follows from this study; the judge remains advisory.

## Estimated time and approvals pending

Saved v10 fresh responses took 128.594–243.611 seconds each. At that range, 12 requests require about **26–49 minutes of generation**; allow **30–55 minutes** including loading and inspection. This is an estimate, not a guarantee. If every request reaches its 600-second timeout, request time alone can reach 120 minutes. Stop and report any runtime/environment blocker rather than rerunning failed cases.

Rachel must confirm (1) c6/c7 allocation, especially D, (2) optional conversions and no-claim PASS, and (3) each proposed expected-label row. Then separately decide whether to run the 12-request study. This commit authorizes no long model experiment.
