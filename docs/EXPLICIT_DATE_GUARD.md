# Explicit-date guard for the v1 renderer path

October 21, 2026. Fixes the missing-date failure recorded privately in controlled pilot `v1-controlled-pilot-002`: the SUT selected frozen current date 2029-01-01 even though the user supplied only 09:10–09:20. The pilot guard blocked that call; it did not fix the agent. That run remains unchanged: four automated matches, one blocked case, one unattempted, nine inference requests. No rerun or new live-model result is claimed here.

## Changed behavior

For `run_calendar_agent(..., renderer_language='en'|'zh-TW')` and CLI `--renderer python --language ...`, Python now checks for a recognizable valid full date **before model inference**. If none is recognized:

- No model callback or Calendar query occurs. The product remains `unsupported` with null `rendered_answer`, not a fake availability conclusion.
- `input_validation` identifies `deterministic_input_validation`, `model_called=false` and an English/Traditional Chinese request for a full date.
- `answer` and `events` are empty: no raw model answer exists. The agent run completes, but CLI exits 1 because availability is unresolved.
- The CLI prints the separate input-validation question and saves a fresh private trace with null model/base URL. It bypasses runtime/model listing and OAuth/Calendar connection entirely for this path. The user supplies a complete new request on the next invocation; there is no multi-turn session state.

Example blocked request: `Is 09:10–09:20 America/Los_Angeles free on the dedicated test calendar?`

Input-validation message:

> Please provide a full date (for example YYYY-MM-DD) before checking availability; no calendar query has been made.

## Conservative supported input formats

Recognize a calendar-valid date with an explicit year in one of these forms:

- ISO `YYYY-MM-DD` (including the date portion of an ISO timestamp).
- Numeric Chinese `YYYY年M月D日`.
- Full English month: `January 23, 2029`, `January 23rd 2029`, `23 January 2029`.

Relative dates (`today`, `tomorrow`, weekdays), missing-year dates, ambiguous slash dates and other unrecognized formats are **not resolved**; request a full date instead. Invalid dates such as 2029-02-30 are not accepted. This intentionally narrows the v1 renderer input contract and must be visible in docs; it does not implement a general natural-language parser.

Recognizing a date does **not** establish which date the user intended, verify that every requested date is valid, or bind the model-selected timestamps to the user's date. A prompt containing a valid date in unrelated text can pass this presence gate; existing tool argument/intent checks and human review remain necessary. No full `user_intent_verified` claim is added. Missing time, ambiguous intent, multiple dates and DST handling retain their existing separate boundaries.

Non-renderer Python behavior and the separate LM Studio/MCP host loop are unchanged. Archived renderer previews do not revalidate the originating prompt. No system prompt, model parameters, Judge rubric or historical label is changed.

## Pilot and validation impact

The six proposed prompts/references and original labels are unchanged. The missing-date case now consumes zero inference attempts and remains expected unsupported with no Calendar call. Its raw-answer review is `not_applicable_no_inference`; human review of the separate input message remains pending. Healthy expected pilot inference count becomes **10**, not the original proposal's 11; the maximum remains 18. Any new real-model round still requires execution approval and a new report directory.

342 offline tests passed, including missing-date API/CLI no-call regressions, both languages, invalid/relative/ambiguous dates, supported explicit formats, unchanged dated request payloads, old non-renderer behavior, and the pilot's physical retry accounting. Existing synthetic renderer tests now use explicit dates to test their original transport/routing purpose. The runner guard test separately bypasses the new gate in a monkeypatched offline test to verify its defense remains intact. No model, Google or Judge call occurred for this implementation.

[Input gate](../src/harness/calendar_input.py) · [Agent integration](../src/harness/calendar_agent.py) · [Regression tests](../tests/test_calendar_input.py)
