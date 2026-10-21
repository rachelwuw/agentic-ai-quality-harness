# Rachel human signoff — v1 controlled pilot 003

Recorded October 21, 2026 (America/Los_Angeles), following Rachel's review of the complete six outputs and accompanying query/fixture facts in this project chat. This is a subsequent human-review addendum; no new run was performed to record it.

## Source and review identity

- Executed candidate commit: `338e4771b70a8fe23a3c019c150382f27ed9cc75`.
- [Case definitions and references](../../evals/proposals/v1_controlled_pilot_cases.json), SHA-256: `d2013eea32387d5f848f06869998091ce29aa60193f6b168c80ab170cb06bc68`.
- Original source: ignored private `reports/runs/v1-controlled-pilot-003/raw.json`, SHA-256: `b262f77b398b1ac446ad70e1cd5348b364e53beaba2380048ce274d66cb35628`. Full model requests/native runtime details remain private and are not reproduced here.
- The public text below contains only the six reviewed synthetic controlled outputs. Per-output SHA-256 covers the exact decoded UTF-8 string, without an added trailing newline; it identifies text, not quality.
- Recorded execution: six cases completed with six automated matches, ten model inference attempts, five simulated Calendar operations, zero Google/Judge calls; runtime unchanged. These observations are separate from the human decision.

## Human decision and precise scope

After reviewing all six complete outputs, Rachel explicitly replied:

> 以上六例通過

This approves **four rendered availability answers (01–04), one deterministic input-validation question (05), and one conservative unknown product answer (06)**. Case 05 is not an LLM answer or rendered availability product: it used zero inference and zero Calendar operations, retained an empty raw answer, and returned unsupported/null product. Case 06 is a simulated CalendarError, not live Google failure evidence.

| Case | Approved field within recorded `run` | Rachel decision | Exact text SHA-256 |
| --- | --- | --- | --- |
| `v1p-01` | `product_output.rendered_answer` | 通過 | `2d9efc76d9b4872649c6bfbb9895b23d1bd0727a7319cf48783ef176c47f2cf1` |
| `v1p-02` | `product_output.rendered_answer` | 通過 | `76c4b84e3a4c9a7d1ecffd05a11dfa39d1fcbbc057b6b43c3713c5d1028ca428` |
| `v1p-03` | `product_output.rendered_answer` | 通過 | `6669539bce0f7c916a2d1e9a5996f65eac48f8a572548c8511b1b8488c87c224` |
| `v1p-04` | `product_output.rendered_answer` | 通過 | `8182549a92974e466a946e815204ce8214a9dd413b68c16c5d1898acc1ebb8e1` |
| `v1p-05` | `input_validation.message` | 通過 | `9714052064c62a40793e9308cc59592bfeb6d4e31790201b24327c03eae74e52` |
| `v1p-06` | `product_output.rendered_answer` | 通過 | `f465690a7137a08589a4c7a99763113f7e0b774407bf82cb970b49da6e529f82` |

## Exact reviewed text

### v1p-01

Approved field: `product_output.rendered_answer`. Product status: `rendered`.

```text
Unavailable (tool-reported; dedicated test calendar only).
Actual tool query: 2029-01-23T09:10:00-08:00 → 2029-01-23T09:20:00-08:00 (America/Los_Angeles)
Original event timestamps: 2029-01-23T17:00:00Z → 2029-01-23T17:45:00Z
Event in requested zone: 2029-01-23T09:00:00-08:00 → 2029-01-23T09:45:00-08:00 (America/Los_Angeles)
This event contains the entire query interval.
```

### v1p-02

Approved field: `product_output.rendered_answer`. Product status: `rendered`.

```text
不可用（工具回報；僅專用測試行事曆）。
工具實際查詢區間: 2029-07-24T14:20:00-07:00 → 2029-07-24T14:50:00-07:00 (America/Los_Angeles)
活動原始時間: 2029-07-24T21:00:00Z → 2029-07-24T21:30:00Z
活動於指定時區: 2029-07-24T14:00:00-07:00 → 2029-07-24T14:30:00-07:00 (America/Los_Angeles)
此活動與查詢重疊，但未包含整段查詢區間。
```

### v1p-03

Approved field: `product_output.rendered_answer`. Product status: `rendered`.

```text
不可用（工具回報；僅專用測試行事曆）。
工具實際查詢區間: 2029-07-25T07:10:00+08:00 → 2029-07-25T07:40:00+08:00 (Asia/Taipei)
活動原始時間: 2029-07-24T16:00:00-07:00 → 2029-07-24T16:30:00-07:00
活動於指定時區: 2029-07-25T07:00:00+08:00 → 2029-07-25T07:30:00+08:00 (Asia/Taipei)
此活動與查詢重疊，但未包含整段查詢區間。
```

### v1p-04

Approved field: `product_output.rendered_answer`. Product status: `rendered`.

```text
Available (tool-reported; dedicated test calendar only).
Actual tool query: 2029-01-23T12:00:00-08:00 → 2029-01-23T12:30:00-08:00 (America/Los_Angeles)
No conflicting events were returned.
```

### v1p-05

Approved field: `input_validation.message`. Product status: `unsupported`.

```text
Please provide a full date (for example YYYY-MM-DD) before checking availability; no calendar query has been made.
```

### v1p-06

Approved field: `product_output.rendered_answer`. Product status: `unknown`.

```text
Availability unknown; no free/busy conclusion is supported.
Calendar scope cannot be verified from this record.
```

## Boundaries and preservation

The original raw report's `raw_answer_review`, `human_product_review` and `semantic_pass_claim=false` stay as recorded at execution. This addendum supplies later case-level human decisions without rewriting historical machine/assisted labels. No per-criterion human labels were separately collected. Source and expected case JSON bytes are unchanged.

This approval does not cover raw LLM prose, other cases/versions, Judge reliability, independent intent generalization, live answers, overall reliability or v1 release approval. Raw LLM defects persist, including the winter answer's incorrect End table cell. The six cases were already used for diagnosis/fix development, so their successful repeat is regression evidence, not held-out accuracy. The earlier blocked run and unloaded-model preflight remain preserved privately.

[Earlier three-answer signoff](CALENDAR_RENDERER_E2E_V1_HUMAN_SIGNOFF.md) is a separate decision on different exact answers. Real Google live-answer human signoff remains pending. No model/Google/Judge calls, tuning, labels/rubrics/settings changes, or new execution approval are implied by recording this decision. Merge of this documentation PR requires its own authorization.
