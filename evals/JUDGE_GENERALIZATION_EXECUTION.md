# Approved new-case development validation

Rachel approved the exact eight draft answers, trace facts, criterion labels (including implicit conversion), gates and 24-request execution on 2026-10-13. The original drafts remain in `evals/proposals/`; approved copies are `judge_generalization_cases.json` and `judge_generalization_labels.json`. Output review, cost acceptance, mode activation and PR merge require separate decisions.

Run only explicitly, from the repository root, with the existing environment and verified local LM Studio runtime:

```sh
.venv/bin/python -m harness.judge_generalization --output-dir reports/runs/judge-generalization-20261013
```

The output directory must not exist. There is no retry/resume option. The bounded runner uses the existing `review` and `local_complete` functions. Each of eight cases receives one nine-check batch request and one request per c6/c7; the latter use output ID c1. The three modes rotate in the approved fixed order. Saved tool calls are synthetic evidence; the runner imports no Calendar client and never generates a SUT answer.

The model is pinned to loopback Qwen `qwen/qwen3.5-9b`, Q8_0, context 8192, temperature 0, Thinking on, strict JSON, max output 6144, timeout 600 seconds. The checked 1024 Thinking budget must be verified in the LM Studio UI before execution; native model metadata does not expose that setting. Positive observed reasoning tokens confirm that reasoning occurred, not enforcement of an exact budget. Runtime metadata is checked before every request; frozen input/runtime changes or transport failure stop the experiment without retries. Schema errors remain available as errors, not semantic UNCERTAIN judgments.

`raw_report.json` is saved before execution and after each response, retaining raw JSON, reasons/evidence, reasoning content, usage, timings and input/code hashes. `comparison.json` compares only the 16 common c6/c7 targets per format, excludes invalid-output placeholders and keeps planned/available counts. `compare()` reports complete-output, paired improvement/regression and control gates. Reason/evidence validation needs a separate assisted manual review of all 32 target judgments. Expected labels are never passed to the model.

`tests/test_judge_generalization.py` verifies the complete schedule and actual mocked request payloads, preservation of evidence/facts, label exclusion, ID mapping, and incomplete/regression scoring. Pytest makes no live model or Google requests.

This one-round, nonrandomized, same-author synthetic study cannot establish repeatability, independent accuracy, or performance on real SUT/Google traces. Check count, context, schema and IDs change together. Default v10 and the deterministic/semantic division are unchanged.
