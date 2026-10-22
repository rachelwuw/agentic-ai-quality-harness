# Fresh v1 acceptance cases — proposed, not executed

October 21, 2026. Prepared after code candidate `338e477` and the six-case regression signoff in `0b87a10`. These new inputs have not been run against the SUT or used to change implementation. They are authored development proposals, **not an independently validated benchmark**. Rachel/separate reference review must approve the exact inputs and outcomes before inference. No new execution is authorized here.

## Fixed inputs and case inventory

Use a fresh conversation per case, frozen `now=2030-01-01T12:00:00-08:00`, unchanged SUT/runtime settings, explicit renderer language below, and fake Calendar only. LA means the literal IANA zone `America/Los_Angeles`; TPE is `Asia/Taipei`; KOL is `Asia/Kolkata`. All intervals are half-open. Fixtures below are event timestamps, not query intervals.

For rows with language en, the exact prompt template is `Check {query} on the dedicated test calendar. Explain any conflict.` For zh-TW it is `請查詢專用測試行事曆：{query}，是否有空？請說明衝突。` Substitute the exact query cell with abbreviations expanded as specified above. Rows marked literal use the quoted prompt verbatim instead. This template rule is part of the proposed input identity; do not silently paraphrase at execution.

| ID / language | Query or literal prompt | Fake fixture | Required outcome/reference |
| --- | --- | --- | --- |
| v1a-01 / en | 2030-02-12 08:00–08:20 America/Los_Angeles | Empty | Render available; query −08:00, UTC 16:00–16:20. |
| v1a-02 / en | 2030-01-16 09:05–09:15 America/Los_Angeles | 2030-01-16T17:00:00Z → 17:25:00Z | Busy; event LA 09:00–09:25 −08:00 contains query; UTC query 17:05–17:15. |
| v1a-03 / zh-TW | 2030-08-20 18:20–18:50 America/Los_Angeles | 2030-08-21T01:00:00Z → 01:30:00Z | Busy, partial; event LA August 20 18:00–18:30 −07:00; UTC query August 21 01:20–01:50. |
| v1a-04 / en | 2030-01-16 08:30–09:00 America/Los_Angeles | 2030-01-16T09:00:00-08:00 → 09:30:00-08:00 | Available; before-event adjacency, UTC query 16:30–17:00; return no busy events. |
| v1a-05 / zh-TW | 2030-01-16 09:30–10:00 America/Los_Angeles | Same event as 04 | Available; after-event adjacency, UTC query 17:30–18:00. |
| v1a-06 / en | 2030-03-10 02:10–02:20 America/Los_Angeles | No fake API operation allowed | DST gap: no guessing. Accept either zero tool calls/unsupported, or exactly one same-local-argument validation call producing `dst_time_requires_clarification`/unknown. No Calendar operation in either route. Raw/user message must request an unambiguous valid time. |
| v1a-07 / zh-TW | 2030-11-03 01:10–01:20 America/Los_Angeles | No fake API operation allowed | DST fold: same two predeclared safe routes as 06; never silently choose a fold/offset. Review the allowed-route policy before freezing. |
| v1a-08 / zh-TW | 2030-09-11 06:45–07:15 Asia/Taipei | 2030-09-10T15:30:00-07:00 → 16:00:00-07:00 | Busy, partial; event TPE September 11 06:30–07:00 +08:00; UTC query September 10 22:45–23:15. |
| v1a-09 / en | 2030-06-15 23:50 to 2030-06-16 00:20 America/Los_Angeles | 2030-06-16T00:00:00-07:00 → 00:10:00-07:00 | Busy; query crosses midnight, UTC June 16 06:50–07:20; event 07:00–07:10 UTC. Event does NOT contain full query. |
| v1a-10 / en | 2030-12-04 12:00–12:30 America/Los_Angeles | Empty | Available; noon, −08:00, UTC 20:00–20:30. |
| v1a-11 / zh-TW | 2030-02-13 00:00–00:30 Asia/Taipei | 2030-02-12T16:15:00Z → 16:25:00Z | Busy; event TPE February 13 00:15–00:25 +08:00 lies within query. UTC query February 12 16:00–16:30; event does not contain query. |
| v1a-12 / en | 2030-01-16 14:00–14:30 Asia/Kolkata | 2030-01-16T08:15:00Z → 08:45:00Z | Busy, partial; event 13:45–14:15 +05:30; UTC query 08:30–09:00. |
| v1a-13 / en | Literal: `Check June 15, 2030, 12:00–12:30 America/Los_Angeles on the dedicated test calendar. Explain any conflict.` | Empty | Available; full English month date accepted; −07:00, UTC 19:00–19:30. |
| v1a-14 / zh-TW | Literal: `請查詢專用測試行事曆：2030年12月4日 10:00 到 10:30，America/Los_Angeles，有空嗎？` | Empty | Available; Chinese date accepted; −08:00, UTC 18:00–18:30. |
| v1a-15 / en | Literal: `Is 16:10–16:35 America/Los_Angeles free on the dedicated test calendar?` | None | Deterministic full-date request, zero inference/Calendar; unsupported/null product, empty raw answer. |
| v1a-16 / en | Literal: `Check tomorrow 16:10–16:35 America/Los_Angeles on the dedicated test calendar.` | None | Same explicit-date gate; relative dates are deliberately outside v1 supported date formats. No model inference. |
| v1a-17 / zh-TW | Literal: `請查詢專用測試行事曆：2030-02-30 10:00 到 10:30，Asia/Taipei，有空嗎？` | None | Invalid date rejected with deterministic date request; zero inference/Calendar, unsupported/null. |
| v1a-18 / en | Literal: `Check January 16, 2030 at 09:00 America/Los_Angeles on the dedicated test calendar.` | None | Missing end/duration: zero tool/API calls, unsupported/null product; raw answer must ask for end/duration, never suggest an invented duration. Date gate alone does not enforce this. |
| v1a-19 / en | Literal: `Check 2030-01-16 09:00–09:30 CST on the dedicated test calendar.` | None | Ambiguous zone: ask clarification, zero tool/API calls; unsupported/null product. Do not assume a region. |
| v1a-20 / en | 2030-01-16 15:00–15:30 America/Los_Angeles | Controlled adapter raises CalendarError | One exact query −08:00, UTC 23:00–23:30; conservative unknown, no invented availability or retry query; not evidence of a live Google outage. |

The numeric reference endpoints were authoring-cross-checked using standard-library zoneinfo. This shares implementation machinery and is **not independent validation**. Human/reference review must separately check date/offset/boundary reasoning, particularly 06/07 permitted routes, before the dataset is frozen. Full literal product text and raw-answer review criteria must be transcribed/reviewed before execution, not derived by asking the SUT or calling the renderer for golden answers.

## Execution prerequisites / avoid false readiness

The existing `calendar_pilot` deliberately requires IDs v1p-01–06 and its original schema. It cannot run this inventory; do not relabel these inputs as the old six IDs or weaken their labels. A separately reviewed versioned protocol must support these new IDs, DST safe alternatives and explicit no-inference cases while preserving old defaults. Offline tests must verify all references, blocked unexpected/extra calls, partial/all-planned reporting and immutable/private outputs before any new SUT call.

Freeze code, materialized input/reference bytes and hashes, runtime, grader version, routes and review policy. Review tool intent/arguments, resolved intervals, Python facts, product output and raw prose separately. Count expected unsupported/unknown honestly; never turn null output into an automatic full-quality pass. Dates, scope and interval relations are critical checks; reject all known critical failures. The existing 95% optional-presentation proposal requires explicit per-check denominators before any run.

## Proposed staged budget — no approval yet

Start with only reviewed v1a-01–06 as a new-version batch: approximately 11–12 inference requests (five normal tool cases plus DST clarification/validation), maximum 18 physical attempts including retries, deadline 600 seconds without changing request timeout. Healthy estimate 1–3 minutes, based on previous small controlled rounds; not a guarantee. Fake Calendar only, zero Google/Judge. Final concrete invocation, new private output directory and exact commit need review after the new protocol exists. No auto load/tuning/rerun-until-green.

The remaining cases and any 20 x 3 study require a later approved budget. If these inputs inform a code/prompt change, retain them as regression/development evidence and prepare fresh acceptance inputs. This inventory alone establishes no general reliability or v1 release readiness.
