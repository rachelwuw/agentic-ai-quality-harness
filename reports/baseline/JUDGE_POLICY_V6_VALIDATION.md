# Calendar judge v6 focused policy validation

Four authored synthetic examples were reviewed once by local Qwen using rubric v6, Thinking requested, temperature 0, strict JSON schema, max output tokens 6144, and timeout 600 seconds per case. No SUT inference or Google Calendar calls were made. Expected labels were not supplied to the judge.

| Case | Authored expectation | Judge verdict | Seconds | Reasoning tokens |
|---|---|---|---:|---:|
| v6-query-event-correct | PASS | PASS | 124.424 | 1024 |
| v6-query-event-wrong | FAIL | FAIL | 156.165 | 1024 |
| v6-duration-clarification | PASS | PASS | 148.797 | 1024 |
| v6-duration-proposal | FAIL | FAIL | 160.155 | 1024 |

All four verdicts matched the authored expectations. All four responses passed output validation and reported observed reasoning. Total inference time: 589.541 seconds.

Codex-assisted evidence review found the reasons consistent with the confirmed policies: distinguish the query window from the actual event interval, and ask for missing duration without suggesting a default. This is not Rachel's individual signoff on the synthetic labels. These examples target the rules used in development; 4/4 agreement is not held-out accuracy or evidence that all 15 original answers pass. The original SUT answers and v5 judge results remain unchanged. Updated SUT prompt behavior has not yet been evaluated.

Next: apply v6 to the original cal-08 and cal-10 saved answers, and separately validate new SUT responses before a full regression run.

Raw output: [judge-policy-v6-20261007.json](judge-policy-v6-20261007.json)

Raw output SHA-256: `de3e5c98a6ba9ef962d115988dce245f54db4f6e8e71bbb97b8e9f9d11a5ff94`
