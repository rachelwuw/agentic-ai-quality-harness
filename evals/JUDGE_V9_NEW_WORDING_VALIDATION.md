# Frozen v9 new-wording validation

Status: completed once under unchanged v9. Four valid outputs, 3/4 aggregate labels matching authored expectations. v9-new-04 remains a false PASS; v9-new-02 also has incorrect per-criterion grades. [Separate evidence review](../reports/baseline/JUDGE_V9_NEW_WORDING_REVIEW.md). Judge remains advisory.

| Case | Authored expectation | Coverage |
|---|---|---|
| v9-new-01 | PASS | Chinese source and correctly converted target intervals. |
| v9-new-02 | FAIL | Indirect conversion claim, correct clock but wrong date. |
| v9-new-03 | PASS | Original interval with explicit denial of conversion. |
| v9-new-04 | FAIL | Correct Chinese conversion followed by a contradictory wrong interval. |

These four answers were authored after v9 was frozen and were not used to revise it. They reuse known dates and a controlled cal-08 trace, so this probes new wording only, not independent model accuracy or generalization to new dates. Labels are authored expectations pending Rachel review and are withheld from the Judge. Criteria use the same order as the original cal-08 run. Source answers, traces, v9 rubric and older results remain unchanged.

Each case is run once through the visible VS Code Terminal. No automatic retries, SUT generations, Google requests, weighted scores or runtime-setting changes are added. Preserve raw outputs and separate assisted review; count both missed failures and false failures, including invalid outputs.

Rubric SHA-256: `9d9203bd4f052323243fb35bca75b271092aad0b00a96ad37c5455e49b13b716`

Suite SHA-256: `261cbd9427d2c06641c5982bfe5ad62289491f233ce9c6ddba19d7af74ffca61`
