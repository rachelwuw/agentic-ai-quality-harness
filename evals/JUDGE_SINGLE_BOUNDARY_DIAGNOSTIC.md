# Approved single-criterion boundary diagnostic — October 13, 2026

Rachel approved the design and explicitly authorized eight requests in this chat. Prior c6/c7 boundaries and D/E labels remain approved. PR #4 and #5 stay unmerged; this is an independent branch based on main.

| Fixed order | Original mapping | Expected | Purpose |
| --- | --- | --- | --- |
| 1 | D/c7 | PASS | Correct target numbers; wrong label belongs to c6 |
| 2 | E/c6 | PASS | Correct target attribution; wrong numbers belong to c7 |
| 3 | D/c6 | FAIL | Negative attribution control |
| 4 | E/c7 | FAIL | Negative numeric control |

Repeat this fixed order once, for exactly eight single-attempt local Qwen requests. No retries, Google access, SUT generation or tuning between rounds. `calendar_judge.main`, `review` and `local_complete` are reused. Explicit opt-in v13 only permits this rubric; the default remains v10.

Answers, prompts, API-call records and tool events are byte-equivalent fields from the approved wording-study source at commit f63939bc1dbc74eeeca5cdc70ff5601668aec427. The selected requirement text is copied exactly from the clarified v12 rubric. Only one requirement is supplied; the existing runner renumbers it c1. Source mappings preserve D/c7 etc. The criterion text still includes its original 'Draft c6/c7' prefixes and cross-references; no wording change is hidden in the diagnostic.

This format simultaneously changes check count, surrounding context, JSON schema size and criterion ID. It can test whether the format helps selected boundaries, but cannot isolate criterion count as the sole cause. Prior batch outputs are historical observations, not contemporaneous randomized controls. Reuse the existing v9 diagnostic method rather than implement a new evaluator.

Qwen/qwen3.5-9b Q8_0; context 8192; UI Thinking on and enabled budget 1024; temperature 0; strict JSON; max output 6144; timeout 600. Record returned reasoning counts separately. Verify source/rubric/system/implementation hashes before inference and after each round; runtime metadata must remain unchanged. Stop on runtime blockers without replacing failed requests.

Input: `judge_single_boundary_cases.json`. Approved labels are separate in `judge_single_boundary_labels.json` and never enter inference. `judge_single_boundary_batch_reference.json` retains selected D/E raw records from both clarified rounds plus full original-report hashes and commit paths; selection is explicit, not a complete baseline snapshot.

For replay only after separate authorization, use the existing judge CLI with `--rubric evals/calendar_judge_rubric_v13.json`, `--input evals/judge_single_boundary_cases.json`, `--thinking --max-tokens 6144 --timeout 600`, and distinct new output paths for each round. Do not overwrite evidence or retry until green.

Report planned and valid judgment denominators, operational errors versus semantic UNCERTAIN, four repeat pairs, positive/negative-control matches, each selected batch-to-single transition and reason/evidence consistency. Preserve raw labels, including contradictions; no automatic semantic repair. The expected sample is failure-selected development evidence, not independent accuracy or release signoff. No default-mode change follows automatically.
