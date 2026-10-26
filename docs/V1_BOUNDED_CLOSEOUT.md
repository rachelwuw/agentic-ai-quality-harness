# v1 bounded closeout — evidence and remaining decisions

## Subsequent authorized OAuth/live follow-up

The original failure and decisions below preserve their checkpoint context. [OAuth-only reauthorization and one newly authorized live round](V1_OAUTH_LIVE_CLOSEOUT.md) subsequently succeeded without source/label changes. Current remaining gates are concentrated human acceptance and the final Rachel release decision; the earlier failed live attempt remains intact.

October 26, 2026. Product candidate: `cad0604e477d15edc437d38057b26f78057938e8`, package `0.3.0.dev0`. This closeout changes dependency/evidence documentation, not product code, model settings, labels or rubric. No v1 tag or release is created.

## Controlled acceptance: two rounds, fixed candidate

Rachel authorized bounded autopilot: complete the missing first-round batches, then repeat all four batches once. This supersedes the earlier proposed 20 × 3 execution requirement for this work package; the old proposal remains historical. Original first-round batches 1/2 were reused, not rerun to replace results. All eight batch manifests have matching code/suite hashes and identical native runtime snapshots. Remaining authored references were AI-reviewed before inference; they are not an independent benchmark. Labels and both predeclared DST routes were unchanged.

| Round / batch | Planned/completed | Automated contract matches | Physical inference attempts |
| --- | --- | --- | --- |
| 1 / 1, historical | 6/6 | 6 | 12 |
| 1 / 2, historical | 6/6 | 6 | 12 |
| 1 / 3, new | 6/6 | 6 | 5 |
| 1 / 4, new | 2/2 | 2 | 3 |
| 2 / 1, new | 6/6 | 6 | 12 |
| 2 / 2, new | 6/6 | 6 | 12 |
| 2 / 3, new | 6/6 | 6 | 5 |
| 2 / 4, new | 2/2 | 2 | 3 |

Six new invocations used **40/108** permitted new physical attempts; total including history was 64. No batch retry, extra case, Judge or controlled Google call occurred. Each invocation kept the existing 18-attempt cap, 600-second orchestration deadline and 180-second request timeout. No case was failed, interrupted or omitted from the automated denominator.

Tool arguments/API intervals, Python facts, product literal references and input gates each matched **40/40 case observations**. These are separate contract checks, not overall semantic accuracy. Per round: **12 rendered, 3 unknown, 5 unsupported**, with 13 simulated Calendar operations. DST cases 06/07 both used original-local-argument Python validation, zero Calendar operations; case 20 was a simulated API failure. Cases 15–17 produced deterministic date questions with zero inference; cases 18/19 remained no-tool unsupported.

Product objects, selected routes and deterministic input messages matched across **20/20 pairs**. Raw prose was not identical and is not declared reliable. Two rounds on one machine/model are bounded repeatability evidence, not population accuracy or independent validation. See [machine-readable checks, source hashes and pair comparisons](../reports/baseline/V1_BOUNDED_AUTOPILOT_CONTROLLED.json).

## AI-assisted review and human boundary

AI inspected all forty observations, keeping product fidelity separate from raw prose. Only **first-round 01–06** have Rachel's explicit human product approval, bound to source/answer hashes in private evidence. Remaining **34 observations** have AI-assisted review only. Previous live/controlled signoffs apply only to their historical outputs.

Known raw-answer defects remain:

- Wrong year 2023 instead of 2030: 01/02/09/12 in both rounds, 05 in round 1 and 11 in round 2.
- Wrong Los Angeles `+08:00` offset in 04 in both rounds, despite correct UTC endpoints.
- 19 proposes America/Chicago before asking confirmation, violating the raw no-region-assumption criterion; no query is sent and product stays null/unsupported.
- 07/14 answer Chinese prompts in English; some raw answers omit explicit dedicated-calendar scope.
- 06 clarification has confusing wording. DST products safely say unknown but do not explain the transition or guide resubmission. Unsupported/null products do not establish clarification quality; no multi-turn continuation exists.

These defects did not alter the observed tool query or Python product output. Raw prose is not the supported renderer product, and the evidence does not show model improvement. A private review packet contains exact 07–20 products and deterministic date messages, plus repeat-pair comparisons, for one consolidated Rachel decision.

## Rebuild evidence

[Hashed lock and reproduction procedure](V1_REPRODUCE.md) cover **46 wheel artifacts**, including runtime/dev/Calendar/MCP dependencies, pip and build tooling, for **macOS arm64 / CPython 3.12**. A new venv installed from those artifacts with no dependency network access during install/build, built and installed the project wheel, passed `pip check`, required MCP/Calendar imports, installed-wheel imports outside the checkout, and **379 offline tests, zero skips**. The wheel's Python source bytes matched the tested candidate. Original `.venv` was not modified or deleted.

The first outside-checkout check accidentally resolved the venv executable symlink to the base interpreter and failed to import `harness`. Its log is retained; using the venv executable correctly passed without source/package changes. This was a verification-command error, not a hidden green rerun of a model experiment.

[Allowlisted environment evidence](../reports/baseline/V1_REBUILD_EVIDENCE.json) records Python, build tools, lock/project wheel hashes and SUT GGUF SHA-256. Existing runtime/model installation and OAuth are separate: no new OS/machine, runtime reinstall, model download or fresh OAuth was verified. Exact package versions reproduce this tested environment, not a recommendation that they are newest or independently security-audited. Historical dependency snapshot remains intact.

## Live regression: blocked at OAuth preflight

After controlled gates passed, the single authorized three-case live invocation used the unchanged candidate and existing fixture/guards. It stopped with **RefreshError**, after native model preflight but before any events send or inference. Counts: **0/12 events sends, 0/12 model attempts; 0/3 fixture checks and 0/3 agent cases completed; all 3 not attempted**. No retry, interactive login, fixture change or scope expansion occurred.

OAuth refresh traffic uses a separate uninstrumented auth transport: zero events sends is **not zero Google network traffic**. The refresh error alone is not evidence of a particular credential-revocation cause. Raw evidence remains ignored and owner-only; the [reviewed allowlisted summary](../reports/baseline/V1_BOUNDED_AUTOPILOT_LIVE_SUMMARY.json) contains no calendar identifiers, dates, answers, runtime instance identifiers or credentials. Historical successful live evidence is retained but cannot replace current-candidate regression.

## Remaining Rachel decisions — not ready to declare v1

1. Review/accept the remaining 14 distinct case products/input messages and the repeat-equality evidence; explicitly decide whether approval covers the additional 34 observations. AI review cannot supply human signoff.
2. Perform one concentrated interactive OAuth setup when ready. Fresh consent/auth evidence is still missing. A new bounded current-candidate live attempt needs authorization because the one permitted invocation was consumed; do not silently retry. Human review of its actual products would follow.
3. Ratify the release contract and known limitations, then decide the v1 release only after the live/auth and human gates are resolved. Keep renderer opt-in, dedicated-calendar scope, advisory Judge and no intent-validation claim explicit.

No critical product defect was observed in these controlled runs. Current live regression, fresh OAuth evidence and final human/release acceptance remain blockers. A clean Python environment is proved within the stated target; clean-machine/runtime recreation is not.
