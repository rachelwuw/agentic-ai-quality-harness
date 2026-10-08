# Saved evidence demo

These are actual saved answers from the local gpt-oss-20b SUT. Calendar responses are **simulated controlled fixtures**, not live Google data. Dates are frozen development inputs. No private Calendar events are reproduced. Both cases have structural success; semantic quality is a separate question. This explanation is Codex-assisted evidence review, not Rachel’s human signoff.

[Original source](../reports/baseline/calendar-baseline-v7-retry-20261007.json) · [Source review](../reports/baseline/CALENDAR_BASELINE_V7_RETRY_REVIEW.md)

## cal-04: Success: an adjacent slot is available

**Problem / user request**

Check October 6, 2026, 10:30–11:00 in Los Angeles on the test calendar.

**Tool arguments: `check_availability`**

```json
{
  "start": "2026-10-06T10:30:00",
  "end": "2026-10-06T11:00:00",
  "time_zone": "America/Los_Angeles"
}
```

**Tool result (controlled fixture)**

```json
{
  "start": "2026-10-06T10:30:00-07:00",
  "end": "2026-10-06T11:00:00-07:00",
  "available": true,
  "busy_intervals": [],
  "source": "controlled_calendar_fixture",
  "scope": "configured_test_calendar_only",
  "time_zone": "America/Los_Angeles"
}
```

**Final answer (verbatim saved output)**

```text
October 6, 2026, 10:30 – 11:00 AM (America/Los_Angeles) is **available** on the test calendar.
```

**How the harness verifies it**

The controlled runner records the requested interval and fixture outcome, and checks expected tool use and arguments. The slot ends exactly when the fixture event starts: half-open intervals do not overlap. The answer correctly reports availability on the test calendar. Structural checks pass; this example illustrates a successful availability answer, not an independent judge benchmark.

## cal-08: Failure: correct tool use, misleading conversion claim

**Problem / user request**

Check October 7, 2026, 02:15–02:45 in Asia/Taipei on the test calendar.

**Tool arguments: `check_availability`**

```json
{
  "start": "2026-10-07T02:15:00",
  "end": "2026-10-07T02:45:00",
  "time_zone": "Asia/Taipei"
}
```

**Tool result (controlled fixture)**

```json
{
  "start": "2026-10-07T02:15:00+08:00",
  "end": "2026-10-07T02:45:00+08:00",
  "available": false,
  "busy_intervals": [
    {
      "start": {
        "dateTime": "2026-10-06T11:00:00-07:00"
      },
      "end": {
        "dateTime": "2026-10-06T11:30:00-07:00"
      }
    }
  ],
  "source": "controlled_calendar_fixture",
  "scope": "configured_test_calendar_only",
  "time_zone": "Asia/Taipei"
}
```

**Final answer (verbatim saved output)**

```text
The requested interval on the test calendar is **busy**.

- **Interval:** 2026‑10‑07 02:15–02:45 (Asia/Taipei)
- **Availability:** Not available
- **Busy event(s):** 2026‑10‑06 11:00–11:30 America/Los_Angeles (converted to the requested timezone)

This information is based solely on the dedicated test calendar.
```

**How the harness verifies it**

The tool and recorded simulated API interval are correct, so structural checks pass. The answer nevertheless says the busy event was “converted to the requested timezone” while displaying Los Angeles time. Python trace facts convert the busy interval to **2026-10-07 02:00–02:30 Asia/Taipei**; Qwen must judge whether the answer’s claim agrees with those facts. A correct “busy” conclusion cannot cancel this misleading claim. The latest full judge baseline also has known coverage gaps: see [v7 assisted review](../reports/baseline/CALENDAR_JUDGE_V7_NEW_BASELINE_REVIEW.md). This is why overall verdicts and individual criteria must both be reviewed.
