# Calendar v6 review of original cal-08 and cal-10

The original saved SUT answers were reviewed once with rubric v6 using the local Qwen judge, Thinking requested, temperature 0, strict JSON schema, max tokens 6144 and timeout 600 seconds. No new SUT inference or Google Calendar requests were made. Original traces and v5 reports were preserved.

| Case | v5 Thinking | v6 Thinking | Codex evidence review expectation | Seconds | Reasoning tokens |
|---|---|---|---|---:|---:|
| cal-08 | FAIL | FAIL | PASS | 416.583 | 1024 |
| cal-10 | FAIL | FAIL | FAIL | 173.396 | 1013 |

Both responses passed schema validation and reported observed reasoning. This does not establish semantic correctness.

- **cal-08: unresolved false FAIL.** The source answer accurately reports the existing 11:00–11:30 Pacific event overlapping the requested interval. The judge misinterpreted “this is not the event interval” as implying no overlap. Its c1 reason contradicts its FAIL label and ends by saying it would mark PASS. Preserve this raw FAIL; do not silently relabel it as model success.
- **cal-10: supported FAIL under the confirmed strict policy.** The source answer proposes a one-hour duration instead of asking the user to supply a duration or end time. v6 correctly fails c1 and c2. This does not mean it actually queried Google; the reason refers to its proposed action.

These observations are Codex-assisted evidence review, not Rachel's human signoff. Source answer_review statuses remain pending. The four focused synthetic examples matching their expectations did not predict success on this original cal-08 answer. This targeted development check is not held-out accuracy. Total inference time was 589.979 seconds; no automatic retry was performed.

Next: simplify cal-08 into separate checks for busy status, actual event times, and query-window conversion (when mentioned), explicitly stating that different intervals can overlap. Validate positive and negative examples including the unchanged original answer. Investigate reason/verdict contradictions before trusting the judge as a release gate. Do not expand to a full 15-case rerun yet.

Raw output: [judge-v6-cal08-cal10-20261007.json](judge-v6-cal08-cal10-20261007.json)

Raw SHA-256: `c4a1c25e970bb91e552aaca3135d31728662460fd00b83d696ebb27811d6b67e`
