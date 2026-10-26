# v1 acceptance checklist — Python CLI Calendar agent

Current evidence: October 26, 2026; product candidate `cad0604e477d15edc437d38057b26f78057938e8`. Package remains `0.3.0.dev0`. [Bounded closeout and failures](V1_BOUNDED_CLOSEOUT.md) · [Rebuild procedure](V1_REPRODUCE.md).

## Agreed delivery direction

Python CLI with explicit `--renderer python --language en|zh-TW` is the primary v1 path. A local LLM interprets/selects the read-only tool; Python validates facts and renders a separate product answer. Preserve raw `answer`, tool `events`, `product_output` and source identity. Do not enable renderer silently. Dedicated test calendar only; Judge advisory. No writes, multi-turn chat, new UI/framework or MCP functionality. LM Studio chat/MCP integration acceptance remains a v2 target.

Complete explicit date/start/end/IANA-zone requests are supported within the [renderer contract](CALENDAR_RENDERER_PREVIEW.md). Predeclared safe unknown/unsupported outcomes are acceptable for DST/incomplete inputs; null output is not semantic success. The [explicit-date gate](EXPLICIT_DATE_GUARD.md) supplies a deterministic date question before inference. DST products and other incomplete inputs lack full clarification guidance; no intent-verification or multi-turn continuation claim is made.

## Acceptance and evidence map

`[x]` marks the stated bounded engineering evidence, not release approval. `[ ]` retains an unresolved release gate.

| Gate | Current evidence | Remaining condition |
| --- | --- | --- |
| [ ] Product contract | Explicit opt-in, no silent raw fallback, rendered/unknown/unsupported; original/converted times and scope separated. | Rachel ratifies exact supported scope, exit behavior, incomplete-input/clarification limitations and advisory Judge policy. |
| [x] Offline logic | 379 passed, zero skips in new isolated Python environment, including required MCP imports. Historical 342 checkpoint plus 37 fresh-protocol tests. | Keep required pytest green for the closeout PR/final main; no arbitrary test-count target. |
| [x] Controlled critical checks | Frozen twenty cases, two rounds on unchanged candidate: tool arguments/API intervals, Python facts, literal product references and input gates each match 40/40 observations. | Bounded authored-reference evidence only; no population/intent-accuracy claim. Raw semantic defects remain separately recorded. |
| [x] Bounded repeatability | Product objects, routes and deterministic input messages equal in 20/20 pairs. Per round 12 rendered, 3 unknown, 5 unsupported. | Two rounds on one runtime, not independent certification or identical raw prose. Earlier 20×3 proposal superseded by Rachel's two-round autopilot authorization. |
| [ ] Current-candidate Google integration | One authorized attempt stopped at OAuth RefreshError: zero events/model calls, all three cases not attempted. Historical successful three-case evidence retained. | Interactive auth/fresh OAuth evidence, then separately authorized bounded regression and review; no silent retry. OAuth refresh traffic is separately uninstrumented. |
| [ ] Human acceptance | First-round fresh cases 01–06 explicitly approved by Rachel; previous controlled/live signoffs retain their historical scope. All forty observations have AI-assisted review. | Remaining 34 observations need Rachel decision; review packet groups 14 remaining distinct case outputs/input messages and repeat comparisons. AI review is not human signoff. |
| [x] Judge boundary | No Judge calls/tuning; deterministic checks and AI/manual review stay distinct. Known raw LLM year/offset/region/language defects preserved. | Do not promote a Judge PASS or automated contract match into semantic/release approval. |
| [ ] Reproducible release | 46-wheel hash lock including build tooling/pip; independent venv, project wheel, dependency check/imports and 379 tests passed on Mac arm64/Python 3.12.14. Runtime/artifact identity recorded. | Fresh OAuth and final release review missing. Existing runtime/model was not reinstalled; clean OS/new machine not tested. |

## Release decision

Not ready to declare v1: current-candidate live/auth evidence and concentrated human/release decisions remain open. No critical product defect was observed in controlled runs. Preserve all original labels, baselines, failure and unattempted denominators. No v1 version/tag/Release is authorized by engineering closeout.

Historical plans: [six-case pilot](../evals/proposals/V1_CONTROLLED_PILOT.md), [fresh twenty-case inventory](../evals/proposals/V1_FRESH_ACCEPTANCE_CASES.md), [rebuild proposal](V1_REBUILD_EVIDENCE_PLAN.md). They describe original authorization contexts; use the current closeout for completed work. New calls beyond the consumed bounded budgets require authorization under the [workflow](../SOURCE_CONTROL.md).
