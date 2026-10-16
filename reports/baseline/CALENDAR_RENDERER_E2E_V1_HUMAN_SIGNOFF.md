# Rachel human signoff — controlled renderer E2E v1

Recorded October 15, 2026 (America/Los_Angeles; October 16 UTC), following Rachel's case-by-case review in this project chat. This is a subsequent human review record, not a new execution or a rewrite of the original experiment.

## Evidence identity

- Source: [calendar-renderer-e2e-v1.json](calendar-renderer-e2e-v1.json), `results` selected by case id.
- Source file SHA-256: `7e22cbca4fd84aa40783a1c4725047f6f0ecdc817401234254b8305a5b5f6d2f`.
- Tested candidate commit: `5ba414b5219f6da4a9005533e96c1bbd0a44f29e`.
- Reviewed field: each case's `run.product_output.rendered_answer`, in full, as displayed in chat alongside the user request and reference event/query facts.
- Output hashes below are SHA-256 of the exact decoded UTF-8 string, with no added trailing newline. They identify the approved text; they are not quality measurements.

## Human decision

Rachel explicitly replied:

> winter-busy：通過
>
> summer-cross-day：通過
>
> noon-free：通過

| Case id | Rachel decision | Product answer SHA-256 |
| --- | --- | --- |
| `winter-busy` | 通過 (passed) | `1e8177856b3238353a1b6a393ae531f08febd7fcd1dcfc74134b75ee6ecbb9a1` |
| `summer-cross-day` | 通過 (passed) | `e6500282eba586963fc85cc5295257c0596f86ab5fcacb08ecafdf5bf11c5643` |
| `noon-free` | 通過 (passed) | `6f2b92c9569f479315bed56221a44ab357e1b4a34dbab3c3f3e62a109e8e3555` |

The reviewed facts were winter 11:10–11:20 within an 11:00–11:30 event (America/Los_Angeles, −08:00); summer cross-day conversion to 07:00–07:30 Asia/Taipei (+08:00), partially overlapping the 07:15–07:45 query; and noon 12:00–12:30 with no returned conflicting events. Full original timestamps and complete product text remain in the linked source.

## Scope and preservation

This confirms the three exact **Python product answers** faithfully present the supplied case facts, including availability, dedicated-calendar scope, query/original/converted times where applicable, interval relationship and selected output language. It does not approve the raw LLM answers or certify Judge reliability, general intent parsing, other cases, production readiness or a future run. No separate per-criterion human labels were collected; the decisions are case-level product signoffs.

The three real Google live cases have **not** received Rachel's individual answer signoff through this decision. Their private traces, pending reviews and public `semantic_pass_claim=false` remain unchanged.

The source JSON's original `answer_review`, `overall_status` and `product_assisted_review.human_signoff` remain as recorded at execution time. This linked addendum supplies the later human decision without changing historical labels, model settings, rubrics or results. No model, Google or Judge calls were made to record this signoff. Approval of these answers does not itself authorize merging this documentation PR or another live experiment.
