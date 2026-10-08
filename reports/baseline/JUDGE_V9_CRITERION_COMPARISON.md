# v9 single-criterion diagnostic comparison — October 8, 2026

36 criterion-level expected labels were authored and frozen before single-criterion execution. The saved batch run matched 31/36 labels. Labels are Codex-authored expectations pending Rachel review, not human signoff.

Four known failed batch checks were selected for the minimum diagnostic comparison. Single-criterion requests matched 3/4 labels, versus 0/4 for the selected batch checks. Selection intentionally targets failures; these figures are not representative accuracy and must not replace the original full-run results.

| Source case/check | Authored expected | Batch verdict | Single verdict | Single seconds |
|---|---|---|---|---|
| v9-new-02 c4 | PASS | FAIL | PASS | 101.723 |
| v9-new-02 c6 | PASS | FAIL | PASS | 128.244 |
| v9-new-04 c2 | FAIL | PASS | PASS | 149.198 |
| v9-new-04 c9 | FAIL | PASS | FAIL | 177.629 |

## Assisted review

- v9-new-02 c4: false FAIL corrected to PASS. The query interval is preserved; the wrong event date belongs to another check.
- v9-new-02 c6: false FAIL corrected to PASS with a consistent reason. Saying only the test calendar was checked does not claim other calendars were checked.
- v9-new-04 c2: still false PASS. The Judge accepts the primary correct conversion and omits the later contradictory interval. Single-criterion scoring did not solve this check.
- v9-new-04 c9: false PASS corrected to FAIL. It explicitly identifies the later incorrect October 7, 11:00–11:30 Taipei interval. Its reason is more verbose than requested and briefly discusses a literal forbidden-date example, but ultimately grounds FAIL in the actual contradictory claim.

The fifth batch mismatch, v9-new-02 c8, remains labelled but was not included in this four-request experiment.

## Execution and limits

The existing runner was used through the VS Code Terminal UI, without implementation changes. Four valid single-attempt outputs; total recorded generation time 556.794 seconds (about 9 minutes 17 seconds). Qwen3.5-9B, Thinking requested, existing UI budget 1024, temperature 0, strict JSON, maximum output 6144 and timeout 600 were retained. Every output reported 1024 reasoning tokens. No new SUT generations, Google requests, automatic retries or rubric changes occurred. UI observations were intermittently stale; saved reports verified completion.

The selected requirement text, answer and trace are identical to their batch counterparts. Single requests change check count, surrounding criterion context, schema size and criterion ID (renumbered c1), so this is a request-format diagnostic, not proof that criterion count alone caused the difference. The two formats each have one observation per selected check and cannot establish repeatability. Separate requests also increase total compute: unchanged per-request budget does not imply unchanged total budget.

These are known development failures and post-hoc authored labels, not held-out validation or independent accuracy. Raw verdicts are preserved unchanged. Judge remains advisory; this review is Codex-assisted evidence review, not Rachel's signoff. No default scoring-mode change is made.

## Evidence

- [Frozen criterion labels](../../evals/judge_v9_criterion_labels.json)
- [Single-request inputs](../../evals/judge_v9_single_criterion_cases.json)
- [Raw single outputs](judge-v9-single-criterion-20261008.json)
- [Comparison data](judge-v9-criterion-comparison-20261008.json)
- [Original batch review](JUDGE_V9_NEW_WORDING_REVIEW.md)
- [Experiment plan](../../evals/JUDGE_V9_CRITERION_EXPERIMENT.md)

Input SHA-256: `fd01180181e527a3c22f1044402d119afd04d7482498cee7b03870abb9b57b0f`

Unchanged rubric SHA-256: `9d9203bd4f052323243fb35bca75b271092aad0b00a96ad37c5455e49b13b716`

Raw single-output SHA-256: `0a13eedb17bf728baf595a026f7aa22e91724f88ed7042f464c4a60e6a81ee30`

## Recommended next step

Review the expected labels, then keep the surviving c2 contradiction failure as a separate diagnostic. A small higher-reasoning-budget comparison on the same frozen single checks would test settings next; its results would remain development evidence and need fresh independent validation before any default-mode decision. Do not immediately rewrite more rubric clauses or expand product scope.
