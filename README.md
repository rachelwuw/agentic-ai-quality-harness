# Rachel’s Agentic AI Quality & Test Harness

[![Deterministic tests](https://github.com/rachelwuw/agentic-ai-quality-harness/actions/workflows/deterministic-tests.yml/badge.svg?branch=main)](https://github.com/rachelwuw/agentic-ai-quality-harness/actions/workflows/deterministic-tests.yml)

**v0.3 Development Preview**

## What it does

The **Calendar Availability Agent** uses a locally hosted LLM to understand a time-slot request, call a read-only Google Calendar tool, and report whether the dedicated test calendar is free. The **three-layer Python testing harness** checks its program logic, real API integration and model behavior, saving tool calls and answers so failures can be investigated.

## Three-layer testing harness

| Layer | What it checks | How it runs |
| --- | --- | --- |
| **1. Deterministic tests** | Agent loop, allowed tools, arguments, time zones, retries and error handling | pytest with scripted model responses and simulated APIs; no live model or Google access. Runs in GitHub Actions. |
| **2. Integration tests** | Real Google Calendar reads and the agent/tool integration | Explicitly invoked, bounded read-only regression runner with fixture preflight checks. Uses a dedicated calendar and real local model; outside ordinary CI. |
| **3. Agent evaluations** | Whether the real model selects the right tool, supplies correct arguments, follows the workflow and answers faithfully | Controlled cases with the real local SUT and simulated Calendar responses; saved traces separate execution success from answer quality. |

Agent evaluations combine rule-based checks, an independent local **Qwen Judge**, and assisted/human review. [Architecture](ARCHITECTURE.md) · [Evaluation guide](evals/CALENDAR_EVALUATIONS.md).

## Findings and engineering improvements

- **Correct tools can produce inconsistent answers → Python facts and opt-in rendering.** Render supported facts while preserving raw answers, traces and separate product output. [Same-run evidence](reports/baseline/calendar-renderer-e2e-v1.json).
- **Judge misses and false failures → criterion-level validation.** Check labels and reasons against reference expectations; preserve failure cases for regression analysis. [Judge findings](reports/baseline/JUDGE_V10_FRESH_REVIEW.md).
- **A local gain can leave other requirements unmet → evaluate the full answer contract.** Candidate fixes were not adopted as complete fixes when they failed the full criteria. [Decisions and evidence](evals/CALENDAR_CANDIDATE_DECISIONS.md).

## Example: detecting and addressing an answer defect

In the public controlled case **`winter-busy`**, the user asks whether **2028-01-19, 11:10–11:20 America/Los_Angeles** is free. The tool reports busy: the event is **19:00–19:30 UTC**, or **11:00–11:30 at UTC−08:00**.

These are **verbatim excerpts from the same run**, using a real local model and simulated Calendar data:

| Raw LLM answer | Opt-in Python product output |
| --- | --- |
| Converted End cell: `2028‑01‑19 11:30–12:00 America/Los_Angeles (offset −08:00)` | `Event in requested zone: 2028-01-19T11:00:00-08:00 → 2028-01-19T11:30:00-08:00 (America/Los_Angeles)` |
| Elsewhere: `The event runs from **11:00 to 11:30 PST** on that day, so it conflicts with the requested 11:10–11:20 slot.` | `Unavailable (tool-reported; dedicated test calendar only).` |

The raw answer's End cell contradicts the evidence and its own prose. The renderer preserves the correct event interval and scope without another inference; this demonstrates output fidelity for this case, not improved LLM reasoning. [Full question, trace, answers and review](reports/baseline/calendar-renderer-e2e-v1.json) (`results`, id `winter-busy`).

## Verification results

| Evidence | Recorded result |
| --- | --- |
| **Offline tests** | **379 passed**, rechecked October 21, 2026. Required pytest CI runs on PRs and main. [Tests](tests/) · [Workflow](.github/workflows/deterministic-tests.yml) |
| **Controlled agent cases** | Earlier 15-case baseline: **14/15 strict structural passes**, with correction recovery recorded separately. Later renderer round: **3/3 structural checks, Python fact checks and assisted product reviews**. [Baseline](reports/baseline/CALENDAR_BASELINE_V7_RETRY_REVIEW.md) · [Renderer review](docs/CALENDAR_RENDERER_OPT_IN.md#approved-controlled-e2e-v1-outcome) |
| **Live integration** | One three-case renderer round: **3 fixture checks and 3 agent structural checks passed**; all three products passed assisted review. [Live outcome](docs/LIVE_RENDERER_OPT_IN.md#approved-live-renderer-round-v1-outcome) · [Public summary](reports/baseline/calendar-live-renderer-attempt-v1-summary.json) |

Rachel confirmed the [earlier three controlled product answers](reports/baseline/CALENDAR_RENDERER_E2E_V1_HUMAN_SIGNOFF.md) and [six pilot outputs](reports/baseline/V1_CONTROLLED_PILOT_003_HUMAN_SIGNOFF.md): four rendered answers, a missing-date question and an unknown response. Live-answer human signoff remains pending. Original experiment labels are preserved.

## Quick start

**Offline tests — Python 3.12+:**

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,calendar,mcp]'
python -m pytest -q
```

No model or credentials are needed for these tests. To use the actual agent, first follow [LM Studio and read-only Google OAuth setup](docs/LOCAL_SETUP.md), then run:

```sh
python -m harness.calendar_agent \
  'Check 2028-01-19 11:10–11:20 America/Los_Angeles on the test calendar.' \
  --output reports/runs/agent-new.json
```

This calls the real local model and Google, not the demo fixture. Use fresh output paths and keep live traces private. [Optional Python renderer flags](docs/CALENDAR_RENDERER_OPT_IN.md).

## Limitations and evidence

Calendar access is **read-only** and limited to the dedicated test calendar; no booking or writes. The renderer is **opt-in** for supported completed single-tool runs, does not verify user intent, and does not automatically apply to default answers or MCP conversations. Missing/error/contradictory evidence stays unknown; multi-query, correction and incomplete runs are unsupported. The opt-in path requires a recognizable full date; otherwise it requests one before inference. [Supported date formats](docs/EXPLICIT_DATE_GUARD.md) · [Full renderer boundaries](docs/CALENDAR_RENDERER_PREVIEW.md).

The Judge is **advisory**. Assisted review is distinct from Rachel's human signoff; neither test counts nor small-sample passes establish general reliability. Raw LLM defects remain, and full Judge repeatability and clean-machine migration verification are incomplete.

[Evidence index and experiment history](reports/baseline/README.md) · [Judge methodology](evals/CALENDAR_JUDGE.md) · [Scope](PROJECT_SCOPE.md) · [Development workflow](SOURCE_CONTROL.md)
