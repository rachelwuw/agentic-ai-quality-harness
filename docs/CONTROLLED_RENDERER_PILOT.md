# Bounded controlled renderer pilot runner

Engineering delivery, October 21, 2026. This supplies the runner prerequisite from [the proposed six-case pilot](../evals/proposals/V1_CONTROLLED_PILOT.md); **no real pilot has been executed or authorized by this implementation**. Package version remains v0.3. Existing agent prompts/tools/model parameters, renderer, legacy evaluator, Judge rubrics/labels and historical reports are unchanged.

Subsequent input-guard update: [missing explicit dates are blocked before inference](EXPLICIT_DATE_GUARD.md). The no-date case now needs zero model requests, so the normal total becomes 10; max 18 and pending execution approval are unchanged. No new runtime result is implied.

Subsequent approved execution/review: pilot 003 completed all six expected routes with ten inference attempts and no Google/Judge calls. [Rachel’s exact six-output signoff](../reports/baseline/V1_CONTROLLED_PILOT_003_HUMAN_SIGNOFF.md) covers four rendered answers, one deterministic input question and one unknown response. This updates the current review status; the engineering/prior proposal sections retain their original context. No independent accuracy or live signoff is claimed.

## Explicit entry point (requires later execution approval)

```sh
python -m harness.calendar_pilot --execute-controlled \
  --cases evals/proposals/v1_controlled_pilot_cases.json \
  --private-dir reports/runs/v1-controlled-pilot-new
```

This invokes the REAL already-loaded local SUT, with a fake Calendar only: no Google connection, OAuth or Judge. It must not be executed simply because the engineering PR passes. No request occurs without the explicit flag; cases, references, language, budget and a NEW private output directory are validated before runtime access. CLI errors do not authorize retries or alternate cases.

The [case JSON](../evals/proposals/v1_controlled_pilot_cases.json) transcribes the six proposed prompts/fixtures and literal endpoint/product references. References remain **proposed** pending independent human review; template matches are not semantic accuracy. On the error case, the existing tool result lacks scope, so the honest unknown product says `Calendar scope cannot be verified from this record.` This is not the successful-case scope assertion. No historical expected label is rewritten.

## Isolation and limits

- Separate module reuses `run_calendar_agent(..., renderer_language=...)`, existing `ControlledCalendar`, renderer and private atomic writer. The old `calendar_evaluate` defaults and schema are unchanged. Both English and Traditional Chinese come from explicit case language.
- Guard the model-selected name/exact arguments **before** agent executor/tool operation. An unexpected, malformed or extra call stops the suite; the fake adapter independently checks one exact resolved interval (none for missing-date). No caller-supplied live Calendar is accepted by this runner.
- Physical inference sends, including transport retries, consume a shared cap of **18**. Every retry passes through `PilotClient.request()`. Stop before send 19; capture failed attempts. Budget/deadline control stops bypass ordinary model retries and cannot become a successful model response.
- **600-second orchestration deadline**: no new inference after expiry. Existing per-request timeout/backoff remains unchanged; an in-flight request may finish later. Lower limits can be specified with `--max-attempts`/`--deadline-seconds`; increases above 18/600 are rejected.
- Require reviewed `openai/gpt-oss-20b` already loaded once with context 8192, and check the full native model entry before/after each case. Stop on changes/unavailability; no auto loading/tuning. Temperature 0/max_tokens 2048 remain the existing client values. Native runtime metadata reads are separate from the inference cap.
- Keep all six planned result rows, including not-attempted/incomplete. Save partial tool evidence on interrupted/blocked cases, completed rows before later failures, and immutable request-time payload/response copies.

## Evidence and interpretation

A fresh owner-only `reports/runs/` directory contains atomic 0600 `raw.json` and `manifest.json`. No overwrite of an existing run directory; no automatic public promotion. Manifest records the suite hash, Python source hashes, limits and native runtime snapshots. Raw evidence contains frozen definitions, original answer/tool trace/product output, physical attempts and separate checks:

1. Selected tool/exact arguments, actual fake API interval, completed run.
2. Python query/event facts versus explicit fixed endpoint references.
3. Exact product text/status/language versus authored references.
4. Raw answer review and human product review remain **pending**; `semantic_pass_claim=false`.

Expected unsupported (missing date) and unknown (controlled API error) can match automated references. `expected_agent_exit=1` records the existing agent CLI contract for these outcomes; it is **not a measured subprocess exit**. The pilot harness exits 0 only when all expected automated checks match, the suite completes, and runtime stays unchanged. That is not a claim that every product was rendered, raw clarification was good, intent was independently validated or semantic signoff was obtained. A false raw availability claim on the missing-date case still requires human rejection even if unsupported routing matches.

Only fixed counts/state are printed, not raw/model/native details. Report all failures without rerun-until-green. If a case informs tuning it becomes development evidence, not an independent held-out benchmark.

## Offline validation

315 full pytest tests passed on October 21, 2026, including 32 new pilot tests. Scripted Chat Completions/native runtime responses and a socket guard verify same-run output/legacy raw equivalence, per-case fixtures, exact argument blocking, physical retry limits/deadline, immutable captures, interrupted/private progress, changed/unloaded runtime, reference validation, both languages and expected unknown/unsupported. No live SUT, Google or Judge request was made. See [tests](../tests/test_calendar_pilot.py).

## Next approval checkpoint

Review exact JSON references/prompts and candidate commit after required CI. Proposed single six-case round: normally 11 inference requests/five simulated tool calls, max 18 attempts, healthy estimate 1–3 minutes, no Google/Judge. Present the concrete frozen candidate, output directory and limits for Rachel's explicit execution approval. A later 20 x 3 study remains unprepared and unapproved; live signoff/repeat is separate.
