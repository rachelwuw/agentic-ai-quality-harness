# Frozen v10 fresh-case review — October 8, 2026

Four new authored cases completed in one attempt each with valid JSON. Aggregate agreement with the pre-run authored expectations was 3/4; one correct winter answer was falsely failed. Criterion agreement was 31/36. Two negative answers were detected, but criterion-level misses, uncertainties and scope disagreements remain. These small development counts do not estimate overall accuracy.

| Case | Pre-run expected | Judge | Seconds |
|---|---|---|---|
| v10-fresh-summer-positive | PASS | PASS | 128.594 |
| v10-fresh-summer-negative | FAIL | FAIL | 203.571 |
| v10-fresh-winter-positive | PASS | FAIL | 224.038 |
| v10-fresh-winter-negative | FAIL | FAIL | 243.611 |

Total recorded generation time: 799.814 seconds (about 13 minutes 20 seconds). Each response reported 1024 reasoning tokens. Same Qwen/qwen3.5-9b, Thinking, existing UI budget 1024, temperature 0, strict JSON, max output 6144 and timeout 600. All cases share the same nine-check layout and order. New date-specific criterion values were adapted and frozen before execution; this is not byte-identical criterion text to prior date-specific controls. Archived v10 rubric, source and implementation hashes remained unchanged through execution. No retries or outcome-driven tuning occurred. Submitted in the visible VS Code Terminal, completion verified from persisted output. No SUT generation or live Google request was made.

## Criterion disagreements preserved

| Case | Criterion | Pre-run expected | Judge |
|---|---|---|---|
| v10-fresh-summer-negative | c2 | FAIL | PASS |
| v10-fresh-summer-negative | c3 | PASS | UNCERTAIN |
| v10-fresh-summer-negative | c6 | PASS | FAIL |
| v10-fresh-winter-positive | c6 | PASS | FAIL |
| v10-fresh-winter-negative | c6 | PASS | FAIL |

- Summer negative c2 misses the later contradictory Taipei clock claim by citing only the initially correct event description. Other criteria catch the defect, so the aggregate FAIL masks this miss.
- Summer negative c3 is UNCERTAIN despite a reason stating optional query-window conversion was omitted, which the policy permits.
- Winter positive c6 is a clear false failure: its reason explicitly reconsiders the rule and concludes “So c6 should be PASS.” The preserved label remains FAIL. The answer retains correct PST event time without claiming conversion.
- Negative c6 labels disagree with the authored criterion separation. Both answers display the conversion in the requested Asia/Taipei timezone, so the pre-run c6 expectations were PASS for claim/label consistency; incorrect clock values were allocated to c2/c7. The Judge instead scores clock-value accuracy again in c6. This is criterion-scope overlap under the existing wording, not an additional aggregate false failure. Whether this separation is sufficiently clear remains a rubric interpretation question for human review. Pre-run labels were not revised to match the Judge.
- Winter negative c2/c7 correctly identify that December Los Angeles 18:00 PST maps to next-day Taipei 10:00, not 09:00.

[Raw output](judge-v10-fresh-20261008.json) retains checks, evidence, reasoning, usage and computed trace facts unchanged. [Comparison](judge-v10-fresh-comparison-20261008.json) records all expected/observed labels. Input and separate pre-run labels are in `evals/judge_v10_fresh_cases.json` and `evals/judge_v10_fresh_labels.json`; the label file is not provided to the Judge. The two summer/winter fixture pairs were authored with date/offset arithmetic verified before the run.

Source SHA-256: `79b3feeadf84acc07b4ea9bba3ec0115456e885ca2f7876f0ab5ca97fffdc08f`

Frozen rubric SHA-256: `7f3e2b5bd48c0a8309a8b41e336af76a88cb0a1e72de21a9c58504b19e1ea484`

Raw output SHA-256: `bc105a7184b21a8c9fe73fb7839b8d2505bc77fe28739b4e49a7e2a6f6747928`

## Limits and next step

Codex-assisted evidence review, not Rachel's human signoff. All authored labels and source answer_review statuses remain pending human review. These new dates and answers were not used to tune v10 before this run, but use known development defect patterns, the same author and paired traces. No independent held-out accuracy, repeated-run consistency, broader language performance or full v10 baseline reliability is established. Model, token budget, language and season causes cannot be isolated from four cases.

Keep v10 and this run as a checkpoint. Judge remains advisory: review FAIL/UNCERTAIN and sample PASS results. First review the winter positive c6 label/reason contradiction and confirm intended c6 versus c7 boundaries; any later design change should get its own version and fresh validation. Do not silently correct labels, rerun until green or claim the time-facts change solved Judge reliability.
