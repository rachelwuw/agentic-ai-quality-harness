# v9 criterion-level diagnostic comparison

Status: completed once. 36 authored expected labels frozen; four single-criterion outputs were valid and matched 3/4 selected labels, versus 0/4 selected batch labels. [Evidence review](../reports/baseline/JUDGE_V9_CRITERION_COMPARISON.md). Labels are Codex-authored, pending Rachel review, not human signoff.

The existing batch output agrees with 31/36 authored criterion labels. Mismatches: v9-new-02 c4, c6, c8 (false FAIL); v9-new-04 c2, c9 (false PASS). This is retrospective development analysis, not an independent benchmark.

Four single-criterion requests select v9-new-02 c4/c6 and v9-new-04 c2/c9. They cover query/event confusion, scope negation, and missed contradictory event intervals. c8 is labelled and retained but not run in this minimum diagnostic sample.

Use the existing runner with `judge_v9_single_criterion_cases.json`, unchanged v9, same Qwen model, Thinking request, 1024 budget, temperature 0, strict JSON, maximum output 6144, timeout 600. Every request is single-attempt; no Google calls or new SUT generations. Identical answer, trace and requirement text are retained. Expected labels remain in a separate file and are not included in the model prompt.

The selected check is renumbered c1 by the existing runner, so this changes check count, surrounding criterion context, schema size and identifier. This is a diagnostic comparison of request formats, not proof that criterion count alone caused any improvement. A single sample per format cannot estimate stability. Both formats retain the same per-request token budget; total compute across separate calls can be larger.

Preserve original batch labels and raw single outputs, including errors. Compare each check with its frozen expected label and inspect reason/evidence consistency. Do not call this held-out validation after using the cases to tune the system.
