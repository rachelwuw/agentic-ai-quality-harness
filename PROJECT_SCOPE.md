# Project scope — Calendar Availability Assistant

Current v1.0.0, October 26, 2026. This document describes the implemented scope and separates future scheduling work.

The v1.0.0 product includes an explicit opt-in deterministic Python product answer to the existing LLM tool-selection workflow. Raw LLM `answer`, tool `events` and `product_output` remain separate; default behavior and the MCP host loop do not opt in. Single supported tool runs use fixed English or Traditional Chinese templates; missing evidence stays unknown, and multi-query, correction and incomplete runs are unsupported. Renderer fidelity does not establish correct user-intent interpretation.

Evidence: [three controlled real-SUT conversations](docs/CALENDAR_RENDERER_OPT_IN.md) and [one three-case real Google read-only round](docs/LIVE_RENDERER_OPT_IN.md), with separate tool execution, Python facts and assisted product review. All three products in each round passed assisted review. The three controlled product answers subsequently received [Rachel's case-by-case signoff](reports/baseline/CALENDAR_RENDERER_E2E_V1_HUMAN_SIGNOFF.md); the historical three live product outputs also received Rachel’s private signoff. Later v1 consolidated acceptance is recorded separately in the [release addendum](reports/baseline/V1_RELEASE_ACCEPTANCE.md). Raw LLM prose defects and advisory Judge limitations remain. These small samples do not establish general semantic accuracy or production reliability.

## Objective

Build a real read-only Calendar assistant as the System Under Test (SUT), and a small Python harness that records and evaluates its behavior. Local inference uses LM Studio; Google Calendar is the external service.

## Implemented scope

- Local gpt-oss-20b SUT and a separate local Qwen3.5-9B judge, loaded in turn on the M5 MacBook Air (32 GB / 4 TB).
- Custom Python agent loop, a tool allowlist, six-step limit and JSON traces.
- Explicit-date input gate on the opt-in renderer path: no recognized full date means a separate deterministic clarification, zero inference/Calendar queries and unsupported product; [formats and limits](docs/EXPLICIT_DATE_GUARD.md). Non-renderer/MCP behavior is unchanged.
- `check_availability` against a dedicated private test calendar, using read-only OAuth. The optional LM Studio MCP adapter also exposes `get_current_time`.
- Python time-zone resolution, conflict boundaries, cross-midnight queries and rejection of ambiguous/nonexistent DST times.
- Clarification of missing information. Missing end time or duration must be requested from the user, not supplied as a proposed default.
- Bounded transport retries and one tool-argument correction opportunity in the Python agent. See [retry policy](RETRY_POLICY.md) for limits and the MCP host boundary.
- 379 deterministic pytest tests, live read-only integration evidence, 15 controlled agent evaluation cases, saved-answer judging and selected regression evidence.

## Expected behavior

Query the tool before claiming availability. Report the requested dates, time zone and dedicated-calendar scope. Distinguish the query interval from the event interval: different intervals can overlap. Report unknown availability after errors. Tool data is evidence, not instructions.

The assistant cannot create, reserve, modify or delete events. A booking request must receive a clear explanation of this limit. A completed agent loop or structural pass does not establish a correct answer.

## Testing and acceptance boundaries

Deterministic tests use scripted model responses and simulated APIs. Live integration checks use the real read-only Google API. The 15-case controlled evaluations use the real local SUT with simulated Calendar evidence; they are not 15 live integration tests.

The local judge scores saved answers without Google credentials or Calendar tools. Invalid output is UNCERTAIN. Judge verdicts are provisional; assisted evidence review is distinct from Rachel's human signoff. The v7 focused development check matched three expectations, but does not establish held-out accuracy. Known failures and earlier results remain preserved.

The historical v0.2 prompt/retry changes have deterministic verification and a new controlled 15-case SUT baseline: 14/15 strict structural passes, with one recovered formatting error. Full v7 scoring completed with 15 valid outputs and raw 11 PASS / 4 FAIL; known coverage gaps and criterion mistakes remain. Human semantic signoff is pending. See [evidence review](reports/baseline/CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md).

## Portability requirements

Keep source, tests, evaluation definitions, docs, dependency declarations and selected sanitized baselines in Git. Exclude virtual environments, model weights, secrets, OAuth tokens and disposable outputs. Recreate the environment and reauthenticate Google on the future 64 GB Mac Studio. Runtime URLs and model roles remain configurable. Hash-fixed dependency/build recreation is verified for Mac arm64/Python 3.12; expanded doctor checks and clean-machine migration validation remain unverified.

## Deferred

Event creation, proposals with a Python confirmation gate, duplicate-write prevention, invitations, recurring events, rescheduling and deletion. These are future scheduling capabilities, not current preview acceptance requirements.

LangGraph, RAG, vector databases, Jenkins, complex CI/CD, real Jira and automated root-cause analysis remain outside this preview.

## Next quality work

The agreed v1 direction is Python CLI with explicitly enabled renderer as the primary supported path; the existing LM Studio chat/MCP experience is a v2 integration/acceptance target. See the [v1 acceptance checklist and evidence gaps](docs/V1_ACCEPTANCE.md) and [proposed six-case controlled pilot](evals/proposals/V1_CONTROLLED_PILOT.md). Historical proposals retain their original planning status. Current v1 evidence and Rachel acceptance are mapped in the checklist; examples do not authorize new model/Google calls.

Use the completed live read-only regression and controlled SUT/judge baselines to prioritize findings. Confirm missing rubric coverage, grade trace facts deterministically, then freeze the revision before validating unseen examples with targeted human review. Improve migration reproducibility without expanding product scope.

## Historical v0.2 checkpoint boundary

The new capability is evaluation infrastructure: Python-derived time/tool facts, deterministic trace grading, semantic Qwen review and preserved overall/criterion comparisons. The Calendar product remains read-only. Frozen v10 fresh validation found 3/4 overall and 31/36 criterion matches against authored expectations, with known false failure and scope disagreement. These counts do not establish overall accuracy; full v10 baseline, human review and repeatability remain pending. Prior raw evidence is retained.

## Bounded v1 closeout — October 26, 2026

[Two-round controlled evidence and blockers](docs/V1_BOUNDED_CLOSEOUT.md) now replace the earlier planned-only status: 40/40 automated contract matches, 20/20 product/route/input repeat comparisons; raw prose defects remain. [Hash-fixed Python recreation](docs/V1_REPRODUCE.md) passed 379 tests in a new venv. The initial live regression failed OAuth preflight and is preserved. A [newly authorized OAuth-only flow and current-candidate live round](docs/V1_OAUTH_LIVE_CLOSEOUT.md) subsequently passed bounded engineering checks; the subsequent [release acceptance addendum](reports/baseline/V1_RELEASE_ACCEPTANCE.md) records Rachel’s acceptance of the consolidated remaining controlled/live outputs and known limitations, and approval of v1.0.0. Original labels remain unchanged.
