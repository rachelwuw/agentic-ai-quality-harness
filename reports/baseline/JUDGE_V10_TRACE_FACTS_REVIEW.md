# v10 Python trace-facts comparison — October 8, 2026

Implemented deterministic trace-fact preparation for semantic answer review. 108 pytest tests passed in 3.36 seconds. Two single-attempt Qwen outputs were valid and matched the authored expected FAIL labels. The previously missed event-instant contradiction was detected in this run; the converted-clock/date check remained correct.

| Check | Authored expected | Prior v9 single verdict | v10 verdict | Prior seconds | v10 seconds |
|---|---|---|---|---|---|
| v9-new-04-c2 | FAIL | PASS | FAIL | 149.198 | 124.561 |
| v9-new-04-c9 | FAIL | FAIL | FAIL | 177.629 | 165.98 |

Total v10 recorded generation time: 290.541 seconds (about 4 minutes 51 seconds). Both responses reported 1024 reasoning tokens. The original inputs, requirement text, system prompt, model, Thinking request, existing 1024 UI budget, temperature 0, strict JSON, maximum output 6144 and timeout 600 were retained. The v10 user context adds computed facts and usage instructions. Commands were submitted through the VS Code Terminal UI; UI snapshots were intermittently stale, with persisted outputs verifying completion.

## What changed

Python derives facts from the saved tool trace independently of answer text and labels: recorded external request count, reported availability, offset-aware UTC query/event intervals, ZoneInfo conversion to query timezone (including abbreviation), and strict event/query overlap. Separate tool observations preserve their source event indices. Missing/invalid offsets or target zones and unsupported all-day events are marked unavailable rather than guessed.

Qwen judges whether every relevant answer claim agrees with those facts. It still interprets language, omitted information, conversion claims and contradictions. Python facts are not automatic natural-language PASS/FAIL grades, nor independent network auditing. Existing deterministic request-count grading remains separate.

Computed event facts correctly preserve the LA event as October 6, 11:00–11:30 UTC-07 and convert it to October 7, 02:00–02:30 Asia/Taipei. Both v10 reasons identify the later incorrect claim of October 7, 11:00–11:30 Taipei, rather than accepting the earlier correct conversion alone.

## Validation and limits

Tests cover cross-day conversion, winter/summer offsets and abbreviations, adjacency, invalid or missing evidence, all-day unsupported data, answer independence, optional legacy context and retention of facts on invalid Judge output. Initial pytest had two failures due to the new tests assuming the first trace event was a tool event; event selection was corrected, then all 108 passed. No model retries occurred.

Archived v9 rubric bytes are preserved. Explicit historical rubrics do not opt into new facts. No new framework, model, runtime settings, SUT behavior, live Google requests, weighted scoring, commit or push was added.

This comparison uses two known negative development checks only. It cannot establish false-failure rates, full-suite accuracy or stability. Facts and instructions were added together, so any change cannot be attributed to arithmetic alone. Correct semantic verdicts are still advisory. Expected labels remain Codex-authored, pending Rachel review; this is assisted evidence review, not human signoff or independent benchmarking.

## Evidence

- [Raw v10 outputs including computed facts](judge-v10-trace-facts-20261008.json)
- [Previous v9 single outputs](judge-v9-single-criterion-20261008.json)
- [Design and procedure](../../evals/JUDGE_V10_TRACE_FACTS.md)
- [Archived v9 rubric](../../evals/calendar_judge_rubric_v9.json)
- [Frozen criterion labels](../../evals/judge_v9_criterion_labels.json)

Source SHA-256: `fd01180181e527a3c22f1044402d119afd04d7482498cee7b03870abb9b57b0f`

v10 rubric SHA-256: `7f3e2b5bd48c0a8309a8b41e336af76a88cb0a1e72de21a9c58504b19e1ea484`

Raw output SHA-256: `67ac4645c424d055db2f308ac2f7878d1fb6d879c4f04184ec2725f245ad5bd4`

Trace-facts implementation SHA-256: `5bfddf88a7c9464413d2b716c5682d8ebb66a9c2fcfefa6b48c8dc60471745e5`

## Recommended next step

Validate positive controls under the same frozen v10 context to check for false FAILs before running a broader baseline. Retain known failure cases and require criterion-level evidence review. A larger reasoning budget is not needed for this first facts-assisted comparison and was not changed.
