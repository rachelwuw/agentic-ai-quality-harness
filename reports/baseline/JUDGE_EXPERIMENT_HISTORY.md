# Judge experiment dispositions — October 13, 2026

Retain negative results alongside promising diagnostics. A merged research checkpoint does not activate a production scoring mode. Default v10 remains active; all Judge results remain advisory.

| Study | Observed result | Disposition and evidence |
| --- | --- | --- |
| v11 boundary/repeatability | 12 valid outputs; 8/12 overall and 94/108 criterion matches. All 54 repeat pairs agree, including mistakes. | [PR #4](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/4) closed without merge; branch `codex/judge-v11-boundary-study` retained. [Frozen report](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/e8f47c94829eb4643c502c4eecaf71ba8b63d5af/reports/baseline/JUDGE_V11_BOUNDARY_REVIEW.md). |
| Wording comparison | 24 attempts; 23 valid judgments and one unretried transport failure. Both arms match 93/99 common available criterion labels; zero improvements or regressions. | [PR #5](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/5) closed without merge; branch `codex/judge-wording-comparison` retained. [Frozen report](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/f63939bc1dbc74eeeca5cdc70ff5601668aec427/reports/baseline/JUDGE_WORDING_COMPARISON_REVIEW.md). |
| Single-criterion boundary diagnostic | 8/8 selected labels match versus 4/8 historical batch labels; positive and negative controls repeat. Count/context/schema/ID are confounded. | [PR #6](https://github.com/rachelwuw/agentic-ai-quality-harness/pull/6) merged as a research checkpoint. [Local evidence review](JUDGE_SINGLE_BOUNDARY_REVIEW.md). No automatic scoring-mode activation or general accuracy claim. |

PR #4/#5 code and complete raw artifacts remain on their preserved branches, not in main. Exact commit links above identify immutable historical reports rather than mutable branch tips. Selected batch snapshots needed for the merged single-criterion diagnostic are already preserved in `evals/judge_single_boundary_batch_reference.json` with original-report hashes.

The proposed next validation uses new same-author synthetic development candidates. It is a separate design/PR with labels and execution awaiting approval, not an independent benchmark or replacement of the negative evidence above.
