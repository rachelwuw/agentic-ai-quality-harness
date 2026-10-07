# Project Scope — Calendar Scheduling Assistant

Approved direction: October 5, 2026. This document describes planned behavior, not implemented functionality.

## Objective

Build a useful local-model scheduling assistant and a quality harness that tests its decisions against real calendar outcomes. The assistant is the System Under Test; the harness measures its behavior.

## v0.1 user journey

Request a personal appointment in natural language. Clarify missing information, check calendar availability, propose a specific slot, obtain explicit confirmation, create the event, and report the actual event link or error.

## Included

- LM Studio and one local gpt-oss-20b artifact on Rachel's M5 MacBook Air, 32 GB / 4 TB.
- Custom Python loop, validated tools, bounded execution, and JSON traces.
- Two real tools: `check_availability` and `create_event`.
- Google Calendar API with user OAuth authorization and a designated test calendar.
- Single events for the user, with no attendee invitations.
- Date, duration, timezone, conflict, clarification, confirmation, duplicate-request, and truthful-result handling.
- A Python-enforced confirmation gate bound to the exact proposed event; model output alone cannot authorize creation.

## Acceptance criteria

- Resolve relative dates against an explicit current date and timezone; ask when meaning is ambiguous.
- Query availability before proposing a conflict-free slot. Recheck before creation and report a newly detected conflict. This is not an atomic reservation of the slot.
- Show title, date, start, end, and timezone before requesting confirmation.
- Do not create without explicit confirmation of that proposal. A changed proposal requires new confirmation.
- Verify actual API success and the returned event before claiming creation.
- Repeated submissions and uncertain API outcomes must not silently create duplicates; reconcile or ask for clarification.
- Keep writes confined to the configured test calendar in this first version.
- Preserve trace evidence for decisions, tool arguments, results, and errors; keep OAuth credentials out of Git and traces.

## Testing

Deterministic tests use scripted model responses and mock API results. Integration tests exercise the real Calendar API on the designated test calendar. Agent evaluations use the real local model to assess task understanding and tool behavior, reviewing traces and resulting calendar state. Live write tests need explicit test authorization; ordinary evaluation runs must not silently create events.

Calendar cases will replace or supplement the existing 15 QA prototype cases. Existing passing pytest results and QA traces do not establish Calendar readiness.

## Deferred

Attendee invitations, recurring events, rescheduling, deletion, LangGraph, RAG, vector databases, Jenkins, real Jira, LLM judges, complex CI/CD, and automated root-cause analysis.

## Next implementation steps

1. Configure Google API access, OAuth, and the designated test calendar.
2. Implement and verify availability lookup.
3. Implement proposals and Python-controlled confirmation.
4. Implement creation and read-back verification, including duplicate handling.
5. Adapt the agent role, tests, and evaluation cases incrementally.

Current implementation: the original QA agent with mock requirements and mock suite results. No Calendar integration exists yet.
