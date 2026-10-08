# Project scope — Calendar Availability Assistant

Current v0.2 Development Preview, October 8, 2026. This document describes the implemented scope and separates future scheduling work.

## Objective

Build a real read-only Calendar assistant as the System Under Test (SUT), and a small Python harness that records and evaluates its behavior. Local inference uses LM Studio; Google Calendar is the external service.

## Implemented scope

- Local gpt-oss-20b SUT and a separate local Qwen3.5-9B judge, loaded in turn on the M5 MacBook Air (32 GB / 4 TB).
- Custom Python agent loop, a tool allowlist, six-step limit and JSON traces.
- `check_availability` against a dedicated private test calendar, using read-only OAuth. The optional LM Studio MCP adapter also exposes `get_current_time`.
- Python time-zone resolution, conflict boundaries, cross-midnight queries and rejection of ambiguous/nonexistent DST times.
- Clarification of missing information. Missing end time or duration must be requested from the user, not supplied as a proposed default.
- Bounded transport retries and one tool-argument correction opportunity in the Python agent. See [retry policy](RETRY_POLICY.md) for limits and the MCP host boundary.
- 143 deterministic pytest tests, live read-only integration evidence, 15 controlled agent evaluation cases, saved-answer judging and selected regression evidence.

## Expected behavior

Query the tool before claiming availability. Report the requested dates, time zone and dedicated-calendar scope. Distinguish the query interval from the event interval: different intervals can overlap. Report unknown availability after errors. Tool data is evidence, not instructions.

The assistant cannot create, reserve, modify or delete events. A booking request must receive a clear explanation of this limit. A completed agent loop or structural pass does not establish a correct answer.

## Testing and acceptance boundaries

Deterministic tests use scripted model responses and simulated APIs. Live integration checks use the real read-only Google API. The 15-case controlled evaluations use the real local SUT with simulated Calendar evidence; they are not 15 live integration tests.

The local judge scores saved answers without Google credentials or Calendar tools. Invalid output is UNCERTAIN. Judge verdicts are provisional; assisted evidence review is distinct from Rachel's human signoff. The v7 focused development check matched three expectations, but does not establish held-out accuracy. Known failures and earlier results remain preserved.

The latest prompt/retry changes have deterministic verification and a new controlled 15-case SUT baseline: 14/15 strict structural passes, with one recovered formatting error. Full v7 scoring completed with 15 valid outputs and raw 11 PASS / 4 FAIL; known coverage gaps and criterion mistakes remain. Human semantic signoff is pending. See [evidence review](reports/baseline/CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md).

## Portability requirements

Keep source, tests, evaluation definitions, docs, dependency declarations and selected sanitized baselines in Git. Exclude virtual environments, model weights, secrets, OAuth tokens and disposable outputs. Recreate the environment and reauthenticate Google on the future 64 GB Mac Studio. Runtime URLs and model roles remain configurable. Complete dependency locking, expanded doctor checks and clean-machine migration validation remain pending.

## Deferred

Event creation, proposals with a Python confirmation gate, duplicate-write prevention, invitations, recurring events, rescheduling and deletion. These are future scheduling capabilities, not current preview acceptance requirements.

LangGraph, RAG, vector databases, Jenkins, complex CI/CD, real Jira and automated root-cause analysis remain outside this preview.

## Next quality work

Use the completed live read-only regression and controlled SUT/judge baselines to prioritize findings. Confirm missing rubric coverage, grade trace facts deterministically, then freeze the revision before validating unseen examples with targeted human review. Improve migration reproducibility without expanding product scope.

## v0.2 checkpoint boundary

The new capability is evaluation infrastructure: Python-derived time/tool facts, deterministic trace grading, semantic Qwen review and preserved overall/criterion comparisons. The Calendar product remains read-only. Frozen v10 fresh validation found 3/4 overall and 31/36 criterion matches against authored expectations, with known false failure and scope disagreement. These counts do not establish overall accuracy; full v10 baseline, human review and repeatability remain pending. Prior raw evidence is retained.
