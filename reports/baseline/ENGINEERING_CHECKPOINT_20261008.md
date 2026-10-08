# Deterministic engineering verification — October 8, 2026

Scope: saved-trace validation and deterministic-only CI configuration. This is not a SUT or Judge model experiment and is not live Calendar integration.

A new temporary virtual environment was recreated with Python 3.12.14 using `.[dev,calendar,mcp]`. MCP, requests and Google OAuth library imports succeeded. The full suite ran in the visible VS Code Terminal:

```text
143 passed in 3.80s
```

No skipped tests were reported; the three existing MCP adapter tests were included. No Google or model inference was used. Added coverage checks malformed run/event/tool-result shapes, field diagnostics, API evidence retained on errors, output-type validation, category separation, non-vacuous verdicts, CLI continuation/report saving and compatibility of saved development fixtures. Source evidence is not mutated.

The initial validation run found two failures caused by treating historical `available: null` as malformed. The implementation was corrected to preserve unknown availability, then the full suite above passed. Historical fixtures/labels were not changed to make tests pass.

This verifies a clean environment on the current Mac. The Linux GitHub Actions result is tracked separately; no clean Mac Studio rebuild, new model evaluation or long judge experiment is claimed.

## GitHub verification

The Python 3.12 Linux [GitHub Actions run](https://github.com/rachelwuw/agentic-ai-quality-harness/actions/runs/37850872081) for engineering commit `5362a52` completed with **success**. Dependency installation, required MCP imports and the deterministic pytest step all passed. This confirms the workflow ran, not merely that its YAML was added.
