# v10: Python facts, semantic answer judgment

Status: implemented; 108 deterministic tests passed in 3.36 seconds in the VS Code Terminal. Two single-criterion local Judge comparisons completed with valid FAIL/FAIL outputs matching authored expectations. The previously missed event-instant contradiction was detected once. [Evidence review](../reports/baseline/JUDGE_V10_TRACE_FACTS_REVIEW.md). Broader reliability remains pending.

`src/harness/trace_facts.py` derives facts exclusively from saved tool events and recorded external requests, never from the answer or expected labels. It calculates UTC query/event intervals, event conversion to the tool's query timezone, timezone abbreviations using Python ZoneInfo, and strict overlap (adjacent intervals do not overlap). It also records tool-reported availability and request count. These are derived trace facts, not independent confirmation of real Google traffic or a proof that the saved trace is trustworthy.

Explicit offsets are required. Missing/invalid timestamps, invalid target zones and unsupported all-day intervals are labelled unavailable; no default timezone is guessed. Reported availability is distinguished from computed event overlap. Multiple tool observations retain separate event indices.

The v10 rubric enables `derive_trace_facts`. The Judge receives `computed_trace_facts` plus instructions to use those values and judge every answer claim against them. Semantic claim detection and contradictions remain Qwen's task. Existing external-request grading stays deterministic; computed facts do not themselves grade natural-language answers. Facts are retained in result JSON even if Judge output fails validation.

v9 is archived unchanged and still supported; it does not receive new facts when explicitly selected. v10 retains all v9 criterion text, model settings, system prompt and scoring rules. The added user-prompt context includes facts and usage instructions, so comparisons cannot isolate facts alone from those instructions. No framework, cloud model, SUT behavior, weighted scoring or new product scope is added.

## Focused comparison

Use identical saved single-criterion inputs `v9-new-04-c2` and `v9-new-04-c9`. Both authored expected labels are FAIL, pending Rachel review. Prior v9 single results were PASS and FAIL, respectively. This run is single-attempt, under the same Qwen/Thinking/budget-1024 settings, temperature 0, strict JSON, maximum output 6144, timeout 600. No live Google calls or new SUT generations.

Source SHA-256: `fd01180181e527a3c22f1044402d119afd04d7482498cee7b03870abb9b57b0f`

v10 rubric SHA-256: `7f3e2b5bd48c0a8309a8b41e336af76a88cb0a1e72de21a9c58504b19e1ea484`

These are known development failures, not held-out accuracy. Retain all outcomes and inspect reasons; supplying correct facts does not guarantee semantic judgment.

## Positive-control follow-up

Two existing correct answers passed all nine checks each with unchanged v10 settings, one attempt each. Observed reasoning tokens 1024 per response; total generation time 297.006 seconds. [Evidence review](../reports/baseline/JUDGE_V10_POSITIVE_CONTROLS_REVIEW.md). Reused controls are not held-out accuracy; broader validation remains pending.
