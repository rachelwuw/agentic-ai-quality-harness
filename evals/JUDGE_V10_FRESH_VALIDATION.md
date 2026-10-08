# Frozen v10 fresh-case validation

Four new authored answers and tool fixtures were prepared before execution: summer Chinese positive/negative and winter English positive/negative. Both pairs cross a date boundary from Los Angeles to Taipei. The negative answer retains a correct statement but adds an incorrect event-conversion claim. All cases use the same nine-check order and policy semantics; date-specific values are adapted from the existing conversion controls. New case criteria are frozen before running, with no outcome-driven tuning.

Input: `judge_v10_fresh_cases.json`. Separate expected criterion labels and pre-run hashes: `judge_v10_fresh_labels.json`. Archived rubric: `calendar_judge_rubric_v10.json`, byte-identical to current v10. Python ZoneInfo arithmetic verified summer/winter offsets and target dates before execution. Labels are Codex-authored expectations pending Rachel review; they are not passed to the Judge. These new development examples use known defect patterns, not an independent held-out benchmark.

Run once per case with existing Qwen, Thinking enabled, UI budget 1024 retained, temperature 0, strict JSON, max output 6144, timeout 600. Inspect observed reasoning tokens. Record every criterion, false pass, false failure, uncertainty, invalid output and latency. No live Google call or new SUT generation. Preserve outcomes and do not modify rubric/labels to improve the result. Full baseline and repeatability remain separate.

Completed once per case: four valid outputs, 3/4 aggregate and 31/36 criterion matches. One false aggregate FAIL. [Evidence review](../reports/baseline/JUDGE_V10_FRESH_REVIEW.md). No rubric or expectation changes after execution.
