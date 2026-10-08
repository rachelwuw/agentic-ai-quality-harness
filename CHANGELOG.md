# Changelog

## 0.2.0.dev0 — Development Preview, October 8, 2026

- Add deterministic facts derived from saved Calendar traces: offset-aware intervals, conversions, overlap and recorded request count. Unknown or unsupported evidence stays unknown.
- Separate direct trace checks from Qwen's semantic answer review. Preserve facts, grader provenance, raw outputs and historical rubrics.
- Record overall and criterion-level label comparisons, including errors hidden by correct aggregate verdicts. No automatic Judge retries or silent label correction.
- Latest deterministic verification: 108 passing tests. Frozen v10 fresh cases: 3/4 overall and 31/36 criterion matches against authored expectations. Known label/reason contradiction, false failure and criterion-scope overlap remain; Judge is advisory.
- Calendar is still read-only. Recent Judge runs use saved evidence; controlled agent evals use simulated Calendar APIs; earlier live Google reads are separate integration evidence.
- Full v10 baseline, independent accuracy, human signoff, repeatability and clean-machine Mac Studio migration are not established.

This is a local source checkpoint, not a production release. Model weights, credentials, tokens, private live traces and disposable run outputs are excluded from Git.

## v0.1 — Earlier development checkpoint

Read-only Calendar assistant, custom Python agent loop, LM Studio SUT, MCP adapter, controlled agent evaluations and initial local Judge infrastructure. See the baseline index for dated evidence and known failures.
