# Live Calendar QA Review

Run date: October 5, 2026. Entry point: Python calendar agent, using local gpt-oss-20b through LM Studio and the real Google Calendar API.

## Fixture

One event was created through Google Calendar UI on **Agentic Harness Test**:

- Title: `[QA TEST] Availability fixture`
- October 6, 2026, 11:00–11:30, `America/Los_Angeles` (UTC−07:00).
- Busy; no guests, recurrence, or notification.
- Retained for repeatable testing. The agent itself still has read-only access.

## Agent results

| Case | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Ask for October 6, 11:15–11:45 Los Angeles | Query UTC−07:00; report conflict | Model supplied UTC−08:00, queried 12:15–12:45 local, and reported free | FAIL |
| Ask for October 6, 11:30–12:00 Los Angeles | Query UTC−07:00; report free at the exact boundary | Model supplied UTC−08:00 and queried 12:30–13:00 local; free answer was coincidentally correct | FAIL: wrong queried interval |
| “幫我約明天” | Ask for time and duration; do not invent a booking | Asked for start/end or duration; no tool call | PASS |

Original traces, ignored by Git:

- `reports/calendar-overlap-live.json`
- `reports/calendar-adjacent-live.json`
- `reports/calendar-clarification-live.json`

## Isolation: direct tool results

Executed visibly in VS Code Terminal with the correct offset:

```sh
.venv/bin/python -m harness.calendar_tools --start '2026-10-06T11:15:00-07:00' --end '2026-10-06T11:45:00-07:00'
.venv/bin/python -m harness.calendar_tools --start '2026-10-06T11:30:00-07:00' --end '2026-10-06T12:00:00-07:00'
```

The overlapping interval returned `available: false` and the fixture's 11:00–11:30 busy interval. The adjacent interval returned `available: true` with no busy intervals. Both direct API checks passed.

## Finding and next change

The model converted October Los Angeles time to UTC−08:00 instead of UTC−07:00. The tool accepted the syntactically valid timestamps and correctly queried those supplied instants. Current validation cannot detect a mismatch with the user's intended local time zone.

Recommended next step: resolve local date/time plus an IANA time zone in Python, including daylight-saving validation, rather than relying on the model to generate a UTC offset. Add this finding as a regression case before introducing event creation.

This review covers three live Python-agent cases and two direct tool checks. It does not establish LM Studio chat MCP behavior for these same cases, repeat-run reliability, or full scheduling correctness. No implementation fix was made during this review.


## October 5, 2026 — Time-zone regression fixed

The Python agent and MCP adapter now accept local `YYYY-MM-DDTHH:MM:SS` start/end values plus an IANA `time_zone` (for example, `America/Los_Angeles`). Python `zoneinfo` resolves UTC offsets before the Calendar API call. Offset-bearing local input, invalid zones, DST gaps, and ambiguous DST folds are rejected; the assistant must clarify rather than guess. The low-level Calendar CLI still accepts explicit RFC3339 instants.

Validation: 52 deterministic tests passed, including summer/winter offsets, rejected wrong-offset input, DST gaps/folds, and a DST-crossing interval. Real local-model reruns correctly queried October 6 with UTC−07:00: 11:15–11:45 busy; 11:30–12:00 free. Traces: `reports/calendar-overlap-fixed.json` and `reports/calendar-adjacent-fixed.json`. These validation runs used background execution after visible Terminal control became unavailable. No calendar writes occurred.

Restart the `rachel-calendar-readonly` MCP integration (or LM Studio) and begin a new chat to load the updated tool schema. The Python entry point is live-tested; the reloaded LM Studio chat entry point has deterministic adapter coverage but has not yet been live-retested. Model interpretation of dates/times still needs broader evaluation.
