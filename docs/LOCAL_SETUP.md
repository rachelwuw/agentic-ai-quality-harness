# Local setup and runtime settings

## Quick start

Use Python 3.12+ and recreate the virtual environment on each machine:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,calendar,mcp]'
python -m pytest -q
```

`requirements-dev.txt` records the initial test environment; optional Calendar/MCP dependency ranges are in `pyproject.toml`. A complete dependency lock is still pending. Do not copy `.venv` to another Mac.

Install [LM Studio](https://lmstudio.ai/download), download/load the local SUT, and enable its loopback server. Keep model IDs configurable and use the IDs exposed by your runtime:

```sh
export SUT_MODEL='openai/gpt-oss-20b'
export JUDGE_MODEL='qwen/qwen3.5-9b'
export LM_STUDIO_BASE_URL='http://127.0.0.1:1234/v1'
python -m harness doctor
```

`.env.example` is a reference; the CLI does not automatically load `.env`. The current doctor checks runtime/model listing, not every migration prerequisite. Legacy `LM_MODEL` and `LM_BASE_URL` remain supported.

On this 32 GB Mac, load SUT and judge in turn rather than assuming both fit at once. Model weights remain on disk when unloaded. Historical Qwen judge baselines used an 8192-token context and Reasoning Budget 0. The saved Thinking experiment preset now uses a 1024-token budget; native requests select off/on explicitly and returned token counts verify whether reasoning occurred. See [the reasoning comparison](../reports/baseline/JUDGE_REASONING_COMPARISON.md) for the matched experiment and its limitations.

## Google Calendar setup

Create a dedicated private test calendar, enable the Google Calendar API, and create a Desktop OAuth client. Store local files outside the repository in `~/.config/agentic-ai-quality-harness/`:

- `google-client.json`: OAuth client credentials.
- `calendar.json`: `{"calendar_id": "YOUR_TEST_CALENDAR_ID"}`; do not use `primary`.
- `google-readonly-token.json`: generated during authorization.

```sh
python -m harness.calendar_setup
```

Complete Google consent yourself. The scope `calendar.events.owned.readonly` permits reads on owned calendars; the application restricts its tool to the configured test calendar. Keep the calendar private and do not commit credentials/tokens. Reauthenticate on a new machine.

## Run the assistant

With the SUT loaded:

```sh
python -m harness.calendar_agent 'Check October 6, 2026, 10:00–10:30 AM in America/Los_Angeles on the test calendar.'
```

The agent uses local start/end values plus an IANA time zone; Python resolves UTC offsets and rejects nonexistent or ambiguous local times pending clarification. The low-level Calendar CLI accepts explicit RFC3339 instants. A completed loop means an answer was produced, not that its content is correct.

For LM Studio chat, configure a local stdio MCP server to run your recreated virtual environment's Python with arguments `-m harness.calendar_mcp`. Enable the integration and restart it after tool updates. Its tools are `check_availability` and `get_current_time`; adjust the Python path on each machine. See [LM Studio MCP documentation](https://lmstudio.ai/docs/app/mcp).

## Run evaluations and the judge

With the SUT loaded:

```sh
python -m harness.calendar_evaluate --output reports/runs/calendar-evaluation.json
```

This runs the real local model against controlled simulated Calendar evidence. It does not access Google. Structural success is separate from answer quality. See [evaluation guidance](../evals/CALENDAR_EVALUATIONS.md).

Unload the SUT and load the configured Qwen judge. After every reload, verify Thinking on and the Reasoning Budget checkbox enabled at 1024 in the LM Studio UI; CLI loading did not preserve this budget in the recorded attempt. Then use strict JSON output (the default), `--max-tokens 6144` and `--timeout 600`. Verify observed reasoning in the returned report; the request alone is insufficient. Use a new output path for each run. Then:

```sh
# Replay frozen v10 development cases into a new output file:
python -m harness.calendar_judge --thinking --rubric evals/calendar_judge_rubric_v10.json --input evals/judge_v10_fresh_cases.json --max-tokens 6144 --timeout 600 --output reports/runs/judge-v10-new.json
# Optional historical v5 calibration, explicitly selecting its rubric:
python -m harness.calendar_judge --thinking --rubric evals/calendar_judge_rubric_v5.json --input evals/judge_calibration_cases.json --calibrate --max-tokens 6144 --timeout 600 --output reports/runs/judge-v5-calibration-new.json
```

The judge computes independent criterion scores; Python aggregates them. Invalid/truncated output becomes UNCERTAIN. No automatic retries or rerun-until-pass. Inspect FAIL/UNCERTAIN and sample PASS. Full suite scoring is not autonomous signoff. See [judge guidance](../evals/CALENDAR_JUDGE.md) and [calibration review](../evals/JUDGE_CALIBRATION_REVIEW.md).


## Hardware and migration

Development: M5 MacBook Air, 32 GB RAM / 4 TB SSD. Future target: 64 GB Mac Studio. Recreate the Python environment, reinstall LM Studio, download both model roles, configure local secrets and reauthenticate Google. Never copy `.venv` or commit model weights or credentials. Complete dependency locking, expanded doctor checks and a clean-machine rebuild remain pending. See [architecture](../ARCHITECTURE.md) and [source control](../SOURCE_CONTROL.md).
