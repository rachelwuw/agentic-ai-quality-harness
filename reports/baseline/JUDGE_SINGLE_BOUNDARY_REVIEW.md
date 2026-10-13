# Approved single-criterion boundary diagnostic — October 13, 2026

Eight authorized single-attempt local Qwen requests completed with valid output. All eight selected criterion labels match the approved expectations, compared with four of eight in the preserved clarified batch outputs. D/c7 and E/c6 false failures became PASS in both rounds; D/c6 and E/c7 remained FAIL. This is a promising selected diagnostic, not independent accuracy or full-answer acceptance.

Rachel approved the four-check design and eight requests. Prior D/E boundaries and labels remain approved. Result review and merge are separate; PR #4 and #5 remain unmerged. This review is Codex-assisted evidence review, not Rachel's output or release signoff.

## Exact inputs and format

Answers, user prompts, tool events and recorded API-call fields match the approved wording source at commit f63939bc1dbc74eeeca5cdc70ff5601668aec427. Selected requirement strings match the clarified v12 batch checks exactly. No rewrite of the requirement, answer or trace occurred. Only one check was supplied to the existing runner, which renumbered it c1; mappings preserve original c6/c7 identities.

That changes criterion count, surrounding context, schema size and ID together. It also retains original 'Draft c6/c7' wording and cross-references. Improvement cannot be attributed solely to check count. Historical batch runs are not contemporaneous randomized controls. This extends the existing v9 single-criterion diagnostic method; it introduces no alternative evaluator or automatic per-check production mode.

Runtime verified before both rounds: qwen/qwen3.5-9b Q8_0; context 8192; LM Studio 0.4.25+1; UI Thinking on, enabled budget 1024; temperature 0; strict JSON; max output 6144; timeout 600. All eight responses reported 1024 reasoning tokens. Source/rubric/labels/reference/system/implementation hashes stayed unchanged. Fresh conversation per request; no retries, Google requests, SUT regeneration, settings changes or additional inference.

## Results

| Original mapping | Expected | Batch rounds 1/2 | Single rounds 1/2 | Evidence-reviewed reason |
| --- | --- | --- | --- | --- |
| D/c7 | PASS | FAIL / FAIL | PASS / PASS | Correct Taipei numeric values assessed; contradictory LA label explicitly disregarded per requirement |
| E/c6 | PASS | FAIL / FAIL | PASS / PASS | Conversion claim explicitly attributed to Taipei; numeric accuracy explicitly excluded |
| D/c6 | FAIL | FAIL / FAIL | FAIL / FAIL | Conversion claims Taipei but displayed label says Los Angeles |
| E/c7 | FAIL | FAIL / FAIL | FAIL / FAIL | Displayed 00:00–00:30 disagrees with computed 01:00–01:30 Taipei |

- Planned/attempted requests and available judgments: 8/8.
- Matching labels: 8/8 planned and 8/8 valid; selected batch labels matched 4/8.
- Historical batch-to-single improvements: 4 observations; regressions: 0.
- PASS control matches: 4/4; FAIL control matches: 4/4. No false PASS or false FAIL in this selected sample.
- Operational errors and valid semantic UNCERTAIN: 0.
- Repeat labels: 4/4 available and consistent. All four raw JSON output strings also repeat exactly.
- Recorded generation time: 897.308 seconds (14m57.308s), median 115.667 seconds, maximum 132.961 seconds; excludes setup/review.
- Eight returned reasoning budgets total 8192 tokens. Usage metadata is preserved per request.

All eight reasons support their criterion labels in this review; no explicit reason/verdict contradiction was observed here. That does not resolve contradictions elsewhere in the batch evaluator. Raw labels, evidence and reasons are unchanged.

**Single PASS does not mean the whole D/E answer passes.** D still contains wrong timezone attribution; E still contains wrong numeric conversion. Their excluded checks correctly fail. The CLI's provisional status here only reflects the supplied one-check rubric and must not be used as a full-answer gate.

## Cost and limits

Two source answers and four selected checks are a tiny failure-selected development sample. Negative controls guard against passing everything, but do not establish broad sensitivity, language coverage or stability across model reloads. Each check has only two observations in one loaded session. These are synthetic answers, not live SUT outputs or independent benchmark items.

The selected historical batch reports needed four requests (D/E in two rounds), about 788.946 seconds, and returned nine checks each. This diagnostic needed eight requests, about 897.308 seconds, and scored only four distinct selected checks twice. The runtime comparison is descriptive across different executions, not a controlled speed benchmark. Do not extrapolate that replacing all nine checks is cheap or justified.

The observed improvement supports a format-level hypothesis: narrower requests can help these selected c6/c7 boundaries. Count/context/schema/ID and historical execution conditions remain confounded. It does not prove a universal fix or permit automatically replacing batch judgments with later favorable judgments.

## Recommended next decision

Keep default v10 and advisory judging unchanged. Do not convert all criteria to individual calls or claim the Judge is generally reliable. If this direction is worth pursuing, first freeze a small new validation set with both attribution and numeric errors, correct answers and implicit conversions, labelled before inference. Prefer independent authorship/review. Compare batch and single formats on those cases under an explicit request/cost limit before any product-mode decision. No new validation or default activation is authorized by this report.

## Preserved evidence

- [Approved design and limits](../../evals/JUDGE_SINGLE_BOUNDARY_DIAGNOSTIC.md)
- [Single-check inputs](../../evals/judge_single_boundary_cases.json), [approved labels](../../evals/judge_single_boundary_labels.json)
- [Filtered batch snapshots and full original report hashes](../../evals/judge_single_boundary_batch_reference.json)
- [Frozen manifest and runtime](single-boundary-20261013/manifest.json)
- [Round 1 raw output](single-boundary-20261013/round1.json), [round 2 raw output](single-boundary-20261013/round2.json)
- [Comparison and all reasons](single-boundary-20261013/comparison.json)
- [Exact offline analysis script retained as text](single-boundary-20261013/analysis-script.txt); no model/network calls, local root/run paths recorded explicitly

160 deterministic tests passed locally. The new mocked CLI test verifies four ordered requests, one-check schema/c1 mapping, unchanged source evidence, labels excluded from the request and default v10. Those tests make no model or Google calls. Required PR CI is separate from semantic evidence.
