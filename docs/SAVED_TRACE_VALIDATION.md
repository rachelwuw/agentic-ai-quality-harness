# Saved evidence validation and deterministic CI

The judge accepts the existing CLI flags and historical v5–v10 rubrics. No criterion text, expected labels, system prompt or preserved model output is changed by this engineering checkpoint.

## Input boundary

`harness.saved_trace.validate_source` checks the report envelope, unique nonempty case IDs and boolean `structural_pass` before runtime access. Invalid envelopes fail with a results-index/field diagnostic. Per-case shape validation checks the prompt, run, completed answer, events, tool results, criterion arrays and recorded API-call objects. Invalid cases are recorded and valid subsequent cases continue.

Tool arguments can contain invalid JSON: a rejected SUT tool invocation is legitimate evidence. Tool errors, nullable/unknown availability and all-day evidence remain accepted; unsupported time facts stay unknown. Missing API evidence is unknown, never a zero-call assumption. Extra historical fields are preserved. This is shape validation, not authentication of a saved trace.

| Outcome | Status / category | Meaning |
| --- | --- | --- |
| Malformed saved case | `input_error` / `input_format_error` | Indexed case/field diagnostics; no judge inference for this case |
| Invalid, nontext, incomplete or malformed judge output | `judge_error` / `model_output_error` | Output cannot be used as semantic judgment; raw returned text retained |
| Request timeout / transport failure | `judge_error` / `transport_error` | No usable model response; failure type recorded |
| Valid JSON with semantic UNCERTAIN | `reviewed`, verdict `UNCERTAIN` | The model could not resolve a criterion from the evidence |
| Incomplete saved agent run | `missing_answer` | No completed answer to judge |

A malformed case cannot become `PASS_PROVISIONAL`. Independent deterministic checks and optional computed trace facts remain in its result when their inputs are valid. A recorded forbidden external request remains FAIL even if semantic judging fails. Input/output failures are operational errors, not evidence of semantic agreement. No automatic judge retries.

## CI boundary

[GitHub Actions](../.github/workflows/deterministic-tests.yml) installs `.[dev,calendar,mcp]` on Python 3.12, verifies MCP imports, and runs the deterministic pytest suite. The explicit import step fails if optional MCP dependencies are missing, preventing an accidental `importorskip` from silently removing MCP coverage.

CI has no model server, OAuth secrets or live Google tests. Tests use scripted model responses and mock adapters. Dependency ranges remain declared in `pyproject.toml`; this is not a complete dependency lock or full Mac Studio migration verification.
