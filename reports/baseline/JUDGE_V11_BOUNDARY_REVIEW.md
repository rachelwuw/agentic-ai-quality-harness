# Approved v11 boundary and repeatability study — October 12, 2026

The 12 authorized local Qwen requests completed in two single-attempt rounds. All outputs were valid; labels were identical across both rounds, including known mistakes. The study establishes repeatability in this loaded-model session, not semantic reliability, independent accuracy or release approval.

Rachel approved c2/c6/c7 boundaries and all six expected-label rows, including D: c2 FAIL, c6 FAIL, c7 PASS, then separately authorized execution. Her approval applies to policy/labels and running the study, not these outputs. The following evidence review is Codex-assisted and awaits Rachel's result review. Synthetic cases are development controls, not new SUT outputs or private Calendar traces.

## Frozen execution and provenance

- Order A/D/B/E/C/F, twice; fresh conversation per request; no retries, tuning, regenerated answers, Google requests or extra inference calls.
- Qwen/qwen3.5-9b, `Qwen3.5-9B-Q8_0.gguf`, context 8192, LM Studio 0.4.25+1, CLI commit 69d945a. Server reports parallel capacity 4; requests were sequential.
- UI Thinking on; enabled Reasoning Budget 1024 verified before both rounds. All 12 responses reported 1024 reasoning tokens. Temperature 0, strict JSON, max output 6144, timeout 600.
- [Pre-run manifest](judge-v11-manifest-20261012.json) freezes source, rubric, approved labels, implementation and system-prompt hashes, and runtime model metadata. Hashes were checked before round 2 and after execution. Default v10 and archived v10 rubric bytes remain unchanged.
- Historical v10 reports did not pin complete artifact/runtime identity. This is not an isolated causal comparison to v10. There was no server restart/model reload between rounds; broader runtime/restart repeatability remains untested.

## Results

| Measure | Result |
| --- | --- |
| Requests / valid outputs | 12 / 12 |
| Input, output, transport errors / timeouts | 0 / 0 |
| Valid semantic UNCERTAIN | 0 |
| Overall label agreement | 8/12 |
| Overall false FAIL | 4/6 expected-PASS observations (A and B, both rounds) |
| Overall false PASS | 0/6 expected-FAIL observations |
| Criterion agreement, planned denominator | 94/108 |
| Criterion agreement, valid-only denominator | 94/108; all planned judgments available |
| Overall repeat pairs | 6/6 available and consistent |
| Criterion repeat pairs | 54/54 available and consistent |
| Generation duration | 2578.853 seconds (42m58.853s); excludes setup and review |
| Median / maximum request | 204.9845 / 354.896 seconds |
| Exploratory nearest-rank p95 | 354.896 seconds; 12 requests is a small sample |

All six paired raw JSON output strings were identical. Equal labels/reasons still include the same false failures. These counts measure agreement with approved synthetic expectations, not product accuracy.

| Case | Expected | Both rounds | Criterion disagreements in each round |
| --- | --- | --- | --- |
| A: original LA event, no conversion claim | PASS | FAIL | c2/c6/c7 expected PASS, observed FAIL |
| D: correct Taipei numbers, contradictory LA label | FAIL | FAIL | c7 expected PASS, observed FAIL |
| B: correct winter conversion | PASS | FAIL | c6 expected PASS, observed FAIL |
| E: wrong winter clock, correct Taipei attribution | FAIL | FAIL | c6 expected PASS, observed FAIL |
| C: correct summer conversion | PASS | PASS | None |
| F: correct opening, later wrong restatement | FAIL | FAIL | c6 expected PASS, observed FAIL |

c2 matches 10/12 approved labels, c6 4/12, c7 8/12. Other criteria match 12/12, but correct labels do not establish correct reasons.

## Evidence-reviewed defects

1. **A: invented arithmetic and inferred conversion.** The answer preserves the original `2027-08-17 17:00–17:30 America/Los_Angeles` event and makes no conversion claim. Python correctly derives next-day Taipei 08:00–08:30. The Judge instead claims 10:00–10:30, contradicts provided facts, and treats original-zone reporting as an implied conversion. This drives c2/c6/c7 false failures in both rounds.
2. **D: c7 scores attribution despite numeric-only boundary.** The Judge recognizes that displayed numeric values match Taipei but fails c7 because the label says LA. c6 and c2 correctly catch that defect; aggregate FAIL masks the additional criterion mistake.
3. **B: explicit verdict/reason contradiction.** The c6 label is FAIL; its extended reason repeatedly concludes the attribution satisfies the requirement and ends in PASS. This is preserved raw, not repaired. The reason explicitly struggles with the sentence `No conversion claim satisfies this check.` That wording can mean either absence of a claim passes, or no claim can ever pass. Wording ambiguity is a plausible contributor, not an isolated causal finding.
4. **E/F: c6 scores numeric errors.** The displayed target is Taipei, so approved c6 passes; clock mistakes belong to c7 and broader c2. Both rounds fail c6 due to those numeric mistakes, showing persistent boundary overlap.
5. **c3 reason errors despite matching labels.** In B/E/C/F, the reason describes a query-window conversion or calls Taipei the event timezone. The answers omit conversion to the original event zone (LA); omission is allowed. Their PASS labels match but reasons do not accurately describe this evidence.

Raw labels, reasons, evidence and reasoning metadata remain unchanged. No keyword-based auto-correction or semantic score repair was applied.

## Next decision

Keep the Judge advisory and default rubric at v10. Proposed next change, requiring a new version and fresh validation: replace the ambiguous no-claim sentence with explicit absence wording, such as `If the answer makes no event-conversion claim, return PASS for this check.` Do not tune during this completed study. Clarify numeric versus attribution boundaries without changing Python facts or deterministic grading.

Any follow-up should freeze revised wording and new independently authored, human-labelled cases before inference. Previously inspected cases can be development regressions, not held-out validation. Reliability across languages, additional timezones, model reloads and runtimes remains unestablished. No new study or default activation is authorized by this report.

## Preserved evidence

- [Round 1 raw output](judge-v11-round1-20261012.json)
- [Round 2 raw output](judge-v11-round2-20261012.json)
- [All labels, reasons, confusion counts and repeat pairs](judge-v11-comparison-20261012.json)
- [Frozen manifest and hashes](judge-v11-manifest-20261012.json)
- [Approved design and replay procedure](../../evals/JUDGE_V11_VALIDATION.md)
- [Approved source](../../evals/judge_v11_cases.json) and [expected labels](../../evals/judge_v11_expected_labels.json)

Engineering validation: 160 deterministic pytest tests passed locally after adding v11 opt-in coverage. The CLI test checks fixed order, nine-check payload, computed overlap facts, labels excluded from inference, and unchanged default v10. No live model or Google call occurs in pytest. Required PR CI remains separate from model evidence.
