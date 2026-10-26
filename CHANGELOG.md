# Changelog

## 1.0.0 — October 26, 2026

- Release the read-only Calendar Availability Agent through the Python CLI with explicit Python renderer and English/Traditional Chinese output. Preserve raw model answer, tool trace, product output and provenance separately.
- Retain three testing layers: offline deterministic pytest/CI, opt-in real Google/OAuth integration, and real local-model controlled evaluations with deterministic grading, advisory Qwen experiments and human review.
- Record 379 offline tests, twenty controlled cases repeated twice (40/40 automated contract matches; 20/20 product/route/input-message pairs), and a bounded three-case live round with six events sends and six model attempts. These are bounded checks, not overall accuracy.
- Include a 46-wheel hash lock and verified Mac arm64/Python 3.12 environment/build procedure; distinguish the new 1.0.0 wheel from historical 0.3.0.dev0 artifacts.
- Record Rachel's scoped consolidated acceptance and v1.0.0 approval in a separate [addendum](reports/baseline/V1_RELEASE_ACCEPTANCE.md). Preserve original pending/semantic labels, private live evidence and failures.
- Keep limitations explicit: read-only dedicated calendar, opt-in renderer, unsupported/missing-input boundaries, incomplete clarification, raw LLM defects, advisory Judge and separate MCP acceptance. No PyPI publication or new-machine/production-readiness claim.

## 0.3.0.dev0 — Development Preview, October 15, 2026

- Add offline interval relations and deterministic Calendar rendering, explicitly opt-in through the Python agent and bounded live runner (#15–#18). Preserve raw answers, tool traces and separate product output; default/MCP behavior remains unchanged.
- Preserve retired #10/#11/#13 candidate evidence without adopting their prompt implementations.
- Record three controlled real-SUT cases and one three-case Google read-only round. Assisted product checks passed; raw LLM defects remain, Rachel’s answer signoff is pending, and Judge remains advisory. Renderer fidelity is not user-intent accuracy or production reliability.
- Current offline verification: 283 pytest tests passed. This version/documentation update runs no new model, Google or Judge experiment.
- Unknown/unsupported, multi-query and correction limits remain explicit. Calendar writes, complete dependency locking and clean-machine migration remain deferred. Historical labels, pending statuses, rubrics and dated reports are unchanged.


## Engineering follow-up — October 8, 2026

- Reorganize the public README, add sanitized saved-evidence demos and separate runtime details. Keep Calendar availability read-only and Judge advisory.
- Add deterministic-only Python 3.12 GitHub Actions with required MCP dependencies.
- Diagnose malformed saved inputs by case/field; distinguish output and transport errors from semantic UNCERTAIN. Preserve independent trace evidence and historical rubric behavior.
- Verification: 143 deterministic tests passed in a recreated environment; no skips. No new SUT inference, Judge experiment or live Calendar call. See [verification](reports/baseline/ENGINEERING_CHECKPOINT_20261008.md).

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
