# v1 acceptance checklist — Python CLI Calendar agent

Current evidence: October 26, 2026; product candidate `cad0604e477d15edc437d38057b26f78057938e8`. Release package version is `1.0.0`; the model/Google evidence retains its original product candidate identity. Rachel subsequently approved the consolidated review and known limitations: [release acceptance addendum](../reports/baseline/V1_RELEASE_ACCEPTANCE.md). [Current OAuth/live closeout](V1_OAUTH_LIVE_CLOSEOUT.md) · [Earlier bounded closeout and failures](V1_BOUNDED_CLOSEOUT.md) · [Rebuild procedure](V1_REPRODUCE.md).

## Agreed delivery direction

Python CLI with explicit `--renderer python --language en|zh-TW` is the primary v1 path. A local LLM interprets/selects the read-only tool; Python validates facts and renders a separate product answer. Preserve raw `answer`, tool `events`, `product_output` and source identity. Do not enable renderer silently. Dedicated test calendar only; Judge advisory. No writes, multi-turn chat, new UI/framework or MCP functionality. LM Studio chat/MCP integration acceptance remains a v2 target.

Complete explicit date/start/end/IANA-zone requests are supported within the [renderer contract](CALENDAR_RENDERER_PREVIEW.md). Predeclared safe unknown/unsupported outcomes are acceptable for DST/incomplete inputs; null output is not semantic success. The [explicit-date gate](EXPLICIT_DATE_GUARD.md) supplies a deterministic date question before inference. DST products and other incomplete inputs lack full clarification guidance; no intent-verification or multi-turn continuation claim is made.

## Acceptance and evidence map

`[x]` marks scoped engineering evidence or Rachel’s subsequent overall acceptance, as specified per row. It does not convert automated/AI checks into criterion-level human labels.

| Gate | Current evidence | Remaining condition |
| --- | --- | --- |
| [x] Product contract | Explicit opt-in, no silent raw fallback, rendered/unknown/unsupported; original/converted times and scope separated. | Accepted by Rachel for v1.0.0, including exit behavior, incomplete clarification and advisory Judge limitations; no scope expansion. |
| [x] Offline logic | 379 passed, zero skips in new isolated Python environment, including required MCP imports. Historical 342 checkpoint plus 37 fresh-protocol tests. | Keep required pytest green for the closeout PR/final main; no arbitrary test-count target. |
| [x] Controlled critical checks | Frozen twenty cases, two rounds on unchanged candidate: tool arguments/API intervals, Python facts, literal product references and input gates each match 40/40 observations. | Bounded authored-reference evidence only; no population/intent-accuracy claim. Raw semantic defects remain separately recorded. |
| [x] Bounded repeatability | Product objects, routes and deterministic input messages equal in 20/20 pairs. Per round 12 rendered, 3 unknown, 5 unsupported. | Two rounds on one runtime, not independent certification or identical raw prose. Earlier 20×3 proposal superseded by Rachel's two-round autopilot authorization. |
| [x] Current-candidate Google integration | Fresh OAuth-only consent/refresh succeeded. Newly authorized single live round: 3/3 fixture/structure/parameter/facts and AI product checks; 6 events sends + 6 model attempts. Earlier RefreshError attempt preserved. | New live products accepted through the scoped release addendum; original pending fields are preserved. OAuth traffic remains separately uninstrumented; no general live-error coverage claim. |
| [x] Human acceptance | First-round fresh cases 01–06 explicitly approved by Rachel; previous controlled/live signoffs retain their historical scope. All forty observations have AI-assisted review. | Rachel accepted the remaining 34 controlled + 3 new live observations and known limits through one consolidated decision. The private packet groups 17 contexts into 15 output groups. No individual criterion labels are inferred. |
| [x] Judge boundary | No Judge calls/tuning; deterministic checks and AI/manual review stay distinct. Known raw LLM year/offset/region/language defects preserved. | Do not promote a Judge PASS or automated contract match into semantic/release approval. |
| [x] Scoped rebuild / release acceptance | 46-wheel hash lock including build tooling/pip; independent venv, project wheel, dependency check/imports and 379 tests passed on Mac arm64/Python 3.12.14. Runtime/artifact identity recorded. | Fresh OAuth-only consent and refresh validation now recorded separately from Python recreation. Rachel accepted this bounded reconstruction scope and approved v1.0.0. New version artifact verification is separate from historical wheel hashes. Existing runtime/model was not reinstalled; clean OS/new machine not tested. |

## Release decision

Rachel accepted the concentrated review, product contract and known limitations and explicitly approved v1.0.0. The [acceptance addendum](../reports/baseline/V1_RELEASE_ACCEPTANCE.md) binds this decision to exact packet/source/output hashes. Release engineering requires a PR, required pytest/main CI, a new annotated tag and GitHub Release. No model/Google rerun is part of the metadata/documentation release. No PyPI publication or production-readiness claim.

Historical plans: [six-case pilot](../evals/proposals/V1_CONTROLLED_PILOT.md), [fresh twenty-case inventory](../evals/proposals/V1_FRESH_ACCEPTANCE_CASES.md), [rebuild proposal](V1_REBUILD_EVIDENCE_PLAN.md). They describe original authorization contexts; use the current closeout for completed work. New calls beyond the consumed bounded budgets require authorization under the [workflow](../SOURCE_CONTROL.md).
