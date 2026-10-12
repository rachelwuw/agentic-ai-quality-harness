# Approved v11 boundary and repeatability study

Rachel approved the c2/c6/c7 boundaries and all six A-F criterion-label rows in the chat on October 12, 2026 (America/Los_Angeles), including D: c2 FAIL, c6 FAIL, c7 PASS. Rachel separately authorized the 12-request experiment. This approval covers study policy and expected labels, not model judgments or release signoff.

The original proposal and draft files remain unchanged. Approved copies are `judge_v11_cases.json` and `judge_v11_expected_labels.json`; the separate opt-in rubric is `calendar_judge_rubric_v11.json`. The default rubric remains v10. The shared runner only gains explicit v11 version support; its prompt, deterministic grading, trace-fact logic, transport and aggregation remain unchanged.

## Frozen design

Six synthetic saved answers, order A/D/B/E/C/F, two sequential rounds. Each request has a fresh conversation and a single transport attempt. Nine semantic checks per request give 108 planned judgments. The existing deterministic-request grader remains configured; no case in this targeted study requires zero simulated requests. Expected labels are read only for the subsequent comparison, never for inference.

Use Qwen/qwen3.5-9b, Qwen3.5-9B-Q8_0.gguf, context 8192, Thinking on, enabled UI reasoning budget 1024, temperature 0, strict JSON, max output 6144, timeout 600. Observed UI settings and returned reasoning counts are separate evidence. Current LM Studio is 0.4.25+1 (CLI commit 69d945a). The API reports parallel capacity 4, but study requests are sequential.

Historical v10 reports do not pin the exact model artifact/runtime version. Consequently, this study cannot establish byte-identical historical runtime or isolate a causal effect of the rubric change versus v10. It measures boundaries and repeatability in the recorded current environment.

## Procedure

Freeze source/rubric/label/prompt/implementation hashes before inference, verify Python-derived fixture facts, then run the existing CLI twice into distinct ignored files:

```sh
JUDGE_MODEL=qwen/qwen3.5-9b python -m harness.calendar_judge --thinking \
  --rubric evals/calendar_judge_rubric_v11.json --input evals/judge_v11_cases.json \
  --max-tokens 6144 --timeout 600 --runtime-note 'Record verified runtime settings here' \
  --output reports/runs/UNIQUE-round1.json
```

Repeat once with a unique round2 path, keeping inputs and runtime fixed. Do not tune between rounds, replace errors, or rerun until green. Stop on a runtime/environment blocker. No SUT regeneration, Calendar tools or Google API calls occur.

## Reporting

Report valid-output coverage separately from semantic UNCERTAIN and operational errors. Compare expected versus observed overall and each criterion; show both matches/108 planned judgments and agreement conditional on available judgments. Compare six overall repeat pairs and 54 criterion repeat pairs, counting unavailable pairs separately. Report time, reasoning/output usage, timeouts and evidence-reviewed reason/verdict contradictions without rewriting raw verdicts.

The cases are approved synthetic development controls, not independent benchmark examples. A later independently authored and human-labelled frozen set is needed before making broader reliability claims. Judge remains advisory.
