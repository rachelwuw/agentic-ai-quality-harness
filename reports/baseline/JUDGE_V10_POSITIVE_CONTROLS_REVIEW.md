# v10 positive-control review — October 8, 2026

Two existing authored positive controls were evaluated once each with the unchanged v10 rubric. Both returned valid JSON and PASS on all nine checks. Assisted evidence review found the reasons consistent with the answers and computed trace facts: the converted control preserves October 7, 02:00–02:30 Asia/Taipei; the no-conversion control preserves October 6, 11:00–11:30 America/Los_Angeles (PDT), without claiming conversion.

| Control | Authored expectation | Judge | Checks | Seconds | Observed reasoning tokens |
|---|---|---|---|---|---|
| v9-conversion-correct | PASS | PASS | 9 | 130.74 | 1024 |
| v9-no-conversion | PASS | PASS | 9 | 166.266 | 1024 |

Total recorded generation time: 297.006 seconds (about 4 minutes 57 seconds). Qwen/qwen3.5-9b, Thinking enabled, existing UI reasoning budget 1024, temperature 0, strict JSON, maximum output 6144, timeout 600. Submitted in the visible VS Code Terminal; persisted results verify completion. No retry, new SUT generation or live Google call occurred. Expected labels were not included in the Judge payload. The runner provides the authored final answer and tool events, not the stale assistant messages retained in the original synthetic trace.

[Raw output](judge-v10-positive-controls-20261008.json). Input: `evals/judge_policy_v9_cases.json`, IDs `v9-conversion-correct` and `v9-no-conversion`. Criteria order comes from this existing input and differs from the two preceding single-criterion negative comparisons; these runs are not one uniform four-case accuracy measurement. Both controls also passed under v9; this is a check for newly introduced false failures, not a demonstrated gain on these controls.

Source SHA-256: `fe859aaef002db39ce0aa120a284a9781a26d92499e74f2e69aea5bacb88efc6`

Rubric SHA-256: `7f3e2b5bd48c0a8309a8b41e336af76a88cb0a1e72de21a9c58504b19e1ea484`

Raw output SHA-256: `138ff42a65b4b0f6b26ce85dfc3f7da699d7ae6c5a957c13d5d16de5b403ba06`

These are reused development controls with Codex-authored expectations, pending Rachel signoff. This is not held-out accuracy, repeatability evidence or independent human review. The two positive controls and preceding two negative checks behaved as expected on these particular attempts; Judge remains advisory and full v10 baseline reliability is unverified. No source answer_review status or prior raw output was changed.

Next: freeze v10 and assess a small balanced set of fresh positive and negative answers under the same criterion layout and settings. Record criterion-level false passes, false failures, unknowns, output failures and latency before deciding on broader use.
