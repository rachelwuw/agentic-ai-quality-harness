# Python Calendar agent renderer opt-in

## Current status — after the recorded experiment

[PR #17](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/17) was subsequently authorized and merged as `16899efbee39617dd083e8c791954c6cfd89090d`. The separately approved Google round and later merged [PR #18](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/18) are documented in [the live outcome](LIVE_RENDERER_OPT_IN.md#approved-live-renderer-round-v1-outcome). The proposed plan and “Keep PR #17 unmerged” instruction below record the authorization state at that time; they are not current pending work. Merge approval does not change the pending individual answer signoff or authorize another live run.

This is the single integration of the existing #16 renderer with a Python agent
run. It does not adopt #10/#11/#13 prompts, change model/tool/rubric settings or add
MCP features. The underlying renderer uses existing #15 math. Rendering is not a
claim that the LLM understands user intent or that its original prose improved.

## Explicit use

```sh
python -m harness.calendar_agent \
  'Check 2028-01-19 11:10–11:20 America/Los_Angeles on the test calendar.' \
  --renderer python --language en --output reports/runs/agent-rendered-new.json
```

The real CLI normally uses the local model and Google: the example is documentation,
not an execution authorization or a command run during this implementation. Runtime
evaluations require separate approval. Use `--language zh-TW` for fixed Traditional
Chinese output. Both flags must be present; invalid/missing language or an existing
opt-in output path fails before model/OAuth setup. New opt-in files are exclusive,
0600, and retain raw model/tool evidence; keep them private and do not commit them.

API: `run_calendar_agent(..., renderer_language='en')`. Default `None` preserves
the legacy return keys, `answer`, model messages, tools, trace and CLI behavior.
No new field is added by default. With opt-in, the SAME completed/failed run is
passed to `render_calendar_answer`; no extra inference, tool or network call is
performed by rendering. The original `answer`, `events` and `status` stay intact.

`product_output` holds the existing renderer version, language, render status,
rendered answer, reasons, limitations and evidence references. Provenance records
the current Python run, raw `answer`/`events` fields, and `user_intent_verified=false`.
It does not certify network authenticity, Calendar completeness or intent parsing.
Existing Judge consumers continue to read raw answer/events; no product-output
Judge ingestion or evaluation-label rewrite is introduced.

## Routing

| Renderer status | CLI output | Opt-in exit status |
| --- | --- | --- |
| rendered | Deterministic template answer, with any limitations retained in JSON | 0 if agent run completed |
| unknown | Conservative unknown statement and reasons in saved product output; no free/busy fallback | 1 |
| unsupported | Explicitly no renderer product output; rendered_answer stays null | 1 |

Raw model prose is retained in JSON, never substituted on stdout in opt-in mode.
No tool call does NOT imply needs-clarification: even a model saying "Free!" with
no tool is unsupported. Multiple queries, correction retries and incomplete runs
are unsupported under the existing renderer contract; do not pick a stale success.
Single Calendar error is unknown. No hidden policy infers user intent from prose.
All-day limitations remain explicit. Without flags, existing stdout/exit/schema
semantics are unchanged. MCP host conversations and existing eval/live runner entry
points do not automatically opt in; this change applies only to the Python API/CLI.

## Offline verification

Scripted models plus controlled Calendar verify the real loop → tool → renderer
path, both languages and busy/free/error; raw result/trace equality with default;
identical model-message/tool inputs, equal call counts and socket-blocked execution;
unknown, zero-tool, corrected/multi-query, model error, CLI routing/no fallback,
early flag/output validation and private new files. No real model/Google/Judge
request occurred. Historical baselines and expected labels remain unchanged.

## Proposed new controlled E2E round — requires approval before execution

Three fresh real SUT conversations with simulated Calendar responses and renderer
enabled. Compare raw prose and product output from the SAME run, not two independently
generated conversations. No Google or Judge calls. Pin source/prompt hashes and
runtime before/after: gpt-oss-20b context 8192, temperature 0, max_tokens 2048 unchanged.

| Case/language | Original fixture | Query | Expected product |
| --- | --- | --- | --- |
| winter-busy / en | 2028-01-19T19:00:00Z to 19:30:00Z | 2028-01-19 11:10–11:20 America/Los_Angeles | Unavailable; event 11:00–11:30 -08:00 contains query |
| summer-cross-day / zh-TW | 2028-08-17T16:00:00-07:00 to 16:30:00-07:00 | 2028-08-18 07:15–07:45 Asia/Taipei | 不可用；活動次日 07:00–07:30 +08:00，部分重疊 |
| noon-free / en | 2028-01-19T11:00:00-08:00 to 11:30:00-08:00 | 2028-01-19 12:00–12:30 America/Los_Angeles | Available; noon interval/scope explicit, no invented events |

Normally six inference requests and three controlled tool queries; zero Google.
Proposed hard cap eight inference requests including existing transport retries;
stop/save partial evidence on errors/budget exhaustion, no added conversations or
reruns. Estimated 1–2 minutes, depending on inference/retries. Do not alter cases,
labels, settings or prompts based on results. Save a fresh report with all failures.

Review tool arguments/intent mapping and Python facts independently, raw LLM quality
separately, and final product conclusion/scope/time/relation/language separately.
Any unknown/unsupported remains visible rather than counted as semantic PASS. One
round does not establish general reliability. Product adoption/merge is separately
authorized; Google live regression requires a later selected-version approval.

## Approved controlled E2E v1 outcome

Rachel approved the above three cases and eight-request cap, not PR merge.
Tested commit `5ba414b5219f6da4a9005533e96c1bbd0a44f29e` and main `089392c`
were unchanged before execution. The three fresh conversations completed in 24.459
seconds, with six first-attempt inference requests and three controlled Calendar
queries, zero Google/Judge calls and unchanged runtime. No prompt/settings/label
changes, extra conversations or reruns occurred.

| Review dimension | This round |
| --- | --- |
| Tool arguments, resolved query and recorded outcome | 3/3 structurally passed |
| Python time facts versus independent fixed endpoint references | 3/3 verified |
| Renderer conclusion/scope, query/original/converted times, relationship and language | 3/3 Codex-assisted review passed; Rachel signoff pending |
| Raw LLM prose | Defects retained; no overall reliability or improvement claim |

The winter raw answer's converted End table cell incorrectly says 11:30–12:00,
contradicting the actual 11:30 event end and other clauses. Its PST wording and
missing explicit scope remain preserved. Summer raw time values/overlap are
supported, but it omits explicit dedicated-calendar scope and uses CST; noon raw
conclusion/scope are supported but omit the numeric offset. Product output in all
three cases correctly renders the recorded facts in the selected language from
the SAME runs, with no additional inference. This validates only these controlled
paths, not user-intent generalization, actual Google integration or improved LLM
prose. Unknown/unsupported paths were tested offline, not exercised in this round.

Full public synthetic raw answers, tool traces, product outputs, code/prompt/plan
hashes and review are in `reports/baseline/calendar-renderer-e2e-v1.json`. Native
runtime details and HTTP request/response captures remain under ignored reports/runs/.
Original request captures used mutable message-array references; separate derived
request-time snapshots were reconstructed and checked against preserved responses,
without overwriting originals or running inference. The public review relies on
saved run events and fixed endpoint references, not the mutable captures.

Keep PR #17 unmerged pending Rachel review/explicit merge authorization. Google
live regression still needs a selected-version plan and separate approval.
