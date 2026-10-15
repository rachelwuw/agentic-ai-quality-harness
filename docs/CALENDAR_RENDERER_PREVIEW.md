# Offline Calendar renderer preview

Approved scope: an opt-in offline preview, not a product integration or an LLM
answer repair. `calendar_renderer.render_calendar_answer(run, language=...)` reads
one recorded run and returns a separately versioned preview. It never modifies
`run.answer`, events, historical reports, expected labels or Judge inputs. The
agent loop, tool payload, system prompt, model settings and rubric are unchanged.

## Contract

- Explicit `en` or `zh-TW` selects fixed templates; no language guessing/model call.
- A completed run must contain exactly one `check_availability` tool event. Missing
  tools, multiple queries, correction sequences, other tools, malformed events or
  incomplete runs return `unsupported` with no rendered prose. No LLM fallback.
- Supported records must explicitly identify `configured_test_calendar_only`.
  The conclusion is tool-reported available/busy, not independent verification.
  Query text is labeled as the actual recorded tool query, not proof that it
  matches the user's intended dates/timezone.
- Errors (including empty error markers), missing scope/data, invalid intervals,
  free-with-events, busy-with-no-events, and known nonoverlapping returned busy
  intervals yield `unknown`, never a supported free/busy conclusion.
- Every rendered answer includes conclusion, scope, query dates/numeric offsets/
  IANA zone and conflict explanation if timed busy events exist. Original event
  strings retain their original offset/Z; no inferred original region or PST/PDT.
- Reuse `trace_facts.interval()` and `interval_relationship()`. Each timed event
  either contains the whole query or overlaps without containing it. Multiple
  events are assessed individually; no union coverage claim.
- Valid all-day date pairs retain dates/end-exclusive semantics and reported busy
  status, with explicit clock-conversion/relationship limitations. They never get
  guessed midnight timestamps. Malformed/mixed date representations yield unknown.

Output schema `calendar-renderer-preview-v1` includes `render_status` (rendered,
unknown, unsupported), `rendered_answer`, explicit `language`, `evidence_refs` to
the original tool event, `reasons` and `limitations`. A rendered all-day result may
have limitations; rendered is not a semantic PASS or independent Google check.

## Offline CLI

```sh
python -m harness.calendar_renderer \
  --input reports/baseline/calendar-evaluation-post-fix-baseline.json \
  --output reports/runs/calendar-renderer-preview-new.json \
  --language zh-TW
```

Uses the existing saved-evaluation envelope contract (unique IDs and boolean
`structural_pass`). It writes a NEW owner-only 0600 sidecar containing the source
hash, original answer and separate preview; refuses existing output or overwriting
the source. It does not rewrite the saved source or invoke any network/client.
Keep private input-derived previews local; original answers and event times may
be private. There is no automatic upload, Judge ingestion or agent integration.

## Validation on main 913f933 plus this candidate

259 offline tests passed, including exact English output, fixed Chinese templates,
summer/winter/DST endpoints, cross-day conversion, noon/free query, original offset
preservation, partial/contained events, no union inference, all-day limitations,
unknown contradictions, malformed evidence, multiple-query rejection, source
immutability, deterministic repeat output and a socket-guarded no-overwrite CLI.
The initial new test fixture labeled a genuinely overlapping interval as disjoint;
that fixture was corrected to an endpoint-adjacent interval, without changing any
existing evaluation label or renderer overlap semantics.

Both languages were previewed on the existing 15-case public controlled saved
baseline: 8 rendered, 3 unknown and 4 unsupported in each language. These counts
measure renderer eligibility, not answer accuracy, new SUT execution or improvement
of the historical LLM answers. Previews are new files under ignored reports/runs/;
all original traces remain untouched. cal-08 demonstrates separate original
Los Angeles timestamps and next-day Taipei conversion, with partial overlap text.

## Deferred integration and claims

No renderer is wired into `run_calendar_agent`, evaluations, live runner, MCP or
Judge. Even faithful rendering cannot fix a wrong agent query, incomplete Calendar
results or fabricated saved evidence. Tool/intent correctness, renderer correctness
and raw LLM prose quality must remain separate evaluation dimensions. Any product
integration, broader language selection, multiple-query support or true SUT/Google
evaluation requires a separately reviewed scope and execution approval. Merge also
requires Rachel's explicit authorization.
