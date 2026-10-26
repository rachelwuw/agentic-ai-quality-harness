# v1 OAuth and current-candidate live closeout

October 26, 2026. Follow-up to the [bounded closeout](V1_BOUNDED_CLOSEOUT.md). Execution checkout was `648bdc8cf09f1f6fb80b5bffe9a148c46b6a16a7`; every product Python source hash still matched tested candidate `cad0604e477d15edc437d38057b26f78057938e8`, and live-case bytes matched the earlier attempt. This PR changes evidence/documentation only. No product, labels, model settings, rubric, workflows, version or release artifacts changed.

## OAuth-only authorization

Rachel explicitly authorized a fresh interactive flow and completed browser consent personally. The existing Desktop client and configured dedicated test calendar were reused; no Google Cloud changes were needed. Only `calendar.events.owned.readonly` was requested and the granted scope was checked for exact equality. This scope permits reads of owned calendars; the application/guards restrict this run to the dedicated calendar.

The existing `InstalledAppFlow` was invoked directly, not `calendar_setup.main()`, which would also issue a seven-day query. The OAuth-only flow made **zero Calendar reads and zero model calls**: no Calendar listing, setup query, fixture modification or permission expansion. Fresh credentials were checked for validity, exact scope and refresh capability; one explicit OAuth refresh validation passed before token replacement. The prior token was preserved privately outside Git, and the new complete token was published atomically with owner-only permissions. No other grant was revoked or credential contents emitted.

OAuth browser authorization, code/token exchange and explicit refresh are separate from Calendar events sends. Internal OAuth HTTP exchanges were not completely instrumented; neither zero OAuth-only Calendar reads nor the six events sends below describe total Google traffic. Consent/refresh success on this existing client/Mac is fresh OAuth evidence, not clean-machine or new Cloud-client provisioning evidence.

## Single authorized live round

| Layer | Evidence |
| --- | --- |
| Budget and completion | One invocation, three planned/completed cases; **6 Calendar events HTTP sends + 6 physical model attempts**, below hard limits of 12 each. No entire-round retry, extra Calendar reads or Judge calls. Elapsed 17.251 seconds. |
| Fixture preflight | 3/3 checks matched the unchanged fixture, all before model inference. |
| Google/tool parameters | Three preflight plus three agent GETs used the exact expected endpoint intervals. All six returned HTTP 200. Wrong/extra requests remained guarded. |
| Python facts | 3/3 query UTC endpoints matched fixed references. Overlap was partial rather than containment; adjacent boundary did not overlap; empty/noon was free. Tool scope stayed dedicated-calendar-only. |
| Runtime and source | Runtime unchanged within the round. All tested source/case hashes retained; no runtime setting or model change. |
| Renderer | 3/3 rendered in explicit Traditional Chinese and passed AI-assisted product-fidelity review: correct availability, query/event distinction, original/converted labels, date/offset and scope. |
| Human boundary | Exact product text matched 3/3 historically approved texts, but this new run remains **pending Rachel signoff**. Original `answer_review=pending` and `semantic_pass_claim=false` are retained. |

Raw LLM prose remains separate: overlap reports the correct conflict/test-calendar scope but omits the explicit date; adjacent reports correct free/date/test-calendar scope but omits numeric offset; empty reports correct free/date/time/zone but omits explicit dedicated-calendar scope and numeric offset. No raw model improvement, full semantic pass or general reliability is asserted. Unknown/unsupported/live-error paths were not exercised in this successful round.

The [original OAuth-failed attempt](../reports/baseline/V1_BOUNDED_AUTOPILOT_LIVE_SUMMARY.json) remains intact with all three cases not attempted. This newly authorized success does not overwrite it. New [runner allowlisted summary](../reports/baseline/V1_LIVE_AFTER_OAUTH_SUMMARY.json) and [OAuth/review addendum](../reports/baseline/V1_OAUTH_LIVE_REVIEW.json) contain no private answers, live dates/queries, Calendar identifiers, URLs, native instance identifiers or credentials. Full traces, exact answers, assistant review and source/answer hashes stay in new ignored owner-only local files.

## Consolidated human acceptance and release

A new private `FINAL_RACHEL_REVIEW_PACKET.md` combines **34 remaining controlled observations and 3 new live observations**. It groups controlled 07–20 and live overlap/adjacent/empty into **17 case contexts / 15 distinct output groups**, including grouped duplicate date questions and null products. It shows each answer once, provides source hashes, and records the 20/20 controlled repeat-pair equality. First-round controlled 01–06 already have separate Rachel approval; no new human labels are inferred. Equality to prior text is review assistance, not transferred approval.

Engineering gates now have bounded evidence: offline/rebuild, two controlled rounds, repeat comparisons, fresh OAuth consent/refresh, current-candidate live parameter/facts checks and AI-assisted product review. Original raw defects, clarification/intent limitations, existing-runtime versus new-Python boundaries, and historical failures remain documented.

**No observed technical blocker remains within the declared bounded scope. V1 is not declared:** Rachel must still decide the concentrated product/repeat acceptance and final release, including known limitations/exit behavior. No tag, GitHub Release, publication or formal version change is authorized by this engineering task. Future model/Calendar runs require a new budget; this round is consumed.
