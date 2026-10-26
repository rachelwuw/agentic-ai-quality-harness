A local LLM-powered **read-only Calendar Availability Agent** and Python quality harness. The accepted product path is the Python CLI with explicit `--renderer python --language en|zh-TW` on a dedicated test calendar.

Three testing layers retain separate evidence:

- **Deterministic tests:** 379 offline tests cover logic, tool arguments, time zones, retries, errors and renderer behavior; required pytest CI.
- **Integration:** fresh OAuth-only consent/refresh and one bounded three-case real Google regression; six events sends and six model attempts. OAuth traffic is separately uninstrumented.
- **Agent evaluations:** twenty real-local-model / simulated-Calendar cases repeated twice; 40/40 automated contract matches and 20/20 paired product/route/input-message matches. Advisory Qwen experiments and human review remain distinct from deterministic grading.

Rachel accepted the consolidated product/repeat review and known limitations and approved v1.0.0. Original pending labels, raw failures and Judge errors remain preserved; acceptance does not establish general accuracy or Judge reliability.

Reproduction uses 46 hash-locked wheels on Mac arm64 / CPython 3.12, including build tooling. A new 1.0.0 wheel was installed and verified separately from historical preview artifacts. Existing runtime/model and fresh OAuth are not proof of a complete new-machine rebuild.

**Limits:** no Calendar writes; renderer opt-in, faithful to tool evidence rather than verified intent. Safe unknown/unsupported and incomplete clarification boundaries remain. Raw LLM defects persist; MCP chat does not inherit Python CLI acceptance. No production-readiness claim or PyPI publication.

[README and demo](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/v1.0.0/README.md) · [Acceptance and exact evidence hashes](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/v1.0.0/reports/baseline/V1_RELEASE_ACCEPTANCE.md) · [Locked reproduction](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/v1.0.0/docs/V1_REPRODUCE.md) · [Evidence index](https://github.com/rachelwuw/agentic-ai-quality-harness/blob/v1.0.0/reports/baseline/README.md)
