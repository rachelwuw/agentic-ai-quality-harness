# Retry policy

Implemented for the custom Python Calendar agent:

- SUT model inference: transient network failures and HTTP 429/500/502/503/504 receive at most two retries (three attempts), with 1- then 2-second waits. Only transport failures are retried; malformed or truncated model output is not retried. Attempts are retained in agent trace events, including exhausted requests.
- Google Calendar reads: the same retry limit applies separately to each page read. Pagination is not a retry. Page/attempt outcomes are included in successful tool results and preserved on query failure. Invalid API responses are not retried. 401/403 and other permanent HTTP errors stop without retry.
- Tool JSON/argument/format errors: the first error allows one correction. A second validation error exhausts the correction budget for that agent run; further tool calls are blocked before Google is accessed.
- Missing or ambiguous user date/time/duration requires clarification. Calendar failures and DST/date/interval errors block additional tool calls for that run. Availability remains unknown. OAuth setup/refresh is not automatically retried by this policy.
- Overall agent limit remains six model steps; transport retries occur within a step and do not add model steps.
- Judge uses the single-attempt request transport. Wrong verdicts and answer-quality failures are preserved without retry-until-pass.
- Predeclared repeated evaluation runs are separate from operation retries; report all runs.

Attempts record outcome, attempt number, error type, retry decision and wait duration without raw credentials or response bodies. A recovered request is not evidence that the service was failure-free.

Scope: the one-correction budget is enforced by the custom Python agent executor. LM Studio's separate chat/MCP host controls its own agent loop; the server shares bounded Calendar network retries, but this change does not enforce a conversation-wide correction limit in that host. No new live Google failure test was performed.
