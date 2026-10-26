# v1 environment rebuild — evidence plan, not a completed rebuild

## Current status — October 26, 2026

The original proposal below is retained as history. Bounded autopilot subsequently authorized and completed the hash-fixed dependency/build scheme and new Python venv checks. See [actual rebuild evidence and procedure](V1_REPRODUCE.md) and [closeout](V1_BOUNDED_CLOSEOUT.md). Runtime/model recreation was not performed; current live attempt failed OAuth refresh, fresh OAuth is still missing. Earlier approval-only instructions below are historical, not current work status.

October 21, 2026. Preparation only: no dependencies installed, environment created/deleted, model loaded, Google authorization performed or experiment executed. Companion to [v1 acceptance](V1_ACCEPTANCE.md).

## Existing evidence and specific gaps

[pyproject.toml](../pyproject.toml) declares Python >=3.12, pytest 8.4.2, optional Calendar/MCP dependency ranges, and build-system setuptools >=68. [requirements-dev.txt](../requirements-dev.txt) records an initial test snapshot; it does not lock all Calendar/MCP/build dependencies. [LOCAL_SETUP.md](LOCAL_SETUP.md) documents setup, model IDs, loopback endpoint and private OAuth storage; doctor only lists runtime models.

Read-only inspection of the **existing** environment observed Python 3.12.14, pytest 8.4.2, mcp 1.30.0, google-auth-oauthlib 1.5.0 and requests 2.34.2. Setuptools is not installed in this runtime environment; its declared isolated-build requirement is separate. These are observed local versions, not recommendations for newest versions, a full transitive lock or proof of a fresh install. Do not install setuptools into the current environment merely to hide that distinction.

| Stage | Required artifact/check | Current status |
| --- | --- | --- |
| 1. Lock target environment | Choose v1 target Python/platform, resolve all selected dev/calendar/mcp transitive dependencies and isolated build tooling; preserve version/hash/marker provenance and install instructions. | Missing complete lock. Keep old snapshot and manifest unchanged until candidate lock reviewed. Mac arm64/Python 3.12 first; do not claim cross-platform reproducibility. |
| 2. Clean Python environment | Fresh uniquely named venv outside the existing `.venv`, install from reviewed artifacts, dependency-consistency check and full offline suite; save commit, Python/platform, package inventory and CI/test outputs. | Not performed. The current 379 passing offline tests (342 at the earlier explicit-date-guard checkpoint) do not substitute for fresh installation evidence. |
| 3. Model/runtime recreation | Install LM Studio/models separately, verify model identity/artifact hash, loaded instance/context and client parameters. Capture only approved runtime metadata. | Existing manifests prove earlier runtime snapshots, not a newly recreated runtime. Current doctor is incomplete. |
| 4. Google recreation | On an approved isolated setup, use dedicated test calendar and fresh consent/auth outside Git; validate read-only access with bounded reads only. | Not performed. Do not copy existing credentials/tokens, revoke current access or trigger consent under documentation approval. |
| 5. Release reproducibility review | Rachel reviews artifacts and boundaries: fresh venv vs existing runtime vs independently authenticated Google; no skipped MCP dependencies, no committed private traces/credentials. | Pending. No v1 tag/version bump/Release authorized. |

## Controlled procedure to prepare next

1. Inspect/choose a locking workflow using the declared extras and Python 3.12 target; resolve versions in an isolated disposable build environment only after authorization for dependency/network work. A `pip freeze` list alone is insufficient: it can omit isolated build requirements, hashes, markers and clean-install validation.
2. Produce a candidate lock plus exact install/check instructions for review without changing package functionality/model configuration. Keep target/platform limitations explicit. Do not add an unreviewed tool or install dependencies in the current `.venv`.
3. After approval, create a fresh venv at a new path, install strictly from reviewed artifacts, check dependencies, explicitly require MCP imports as CI does, then run the full offline suite. No model/OAuth activity is needed for this stage. Preserve logs privately and publish only reviewed metadata/results.
4. If installation/tests fail, preserve the failure and fix the lock/instructions through a branch/PR. Do not mutate the original working environment or silently replace failed evidence.
5. Plan runtime and Google recreation as separately authorized stages. A new Python venv on this Mac proves only Python-environment recreation; it does not demonstrate a clean OS/new machine or fresh model/OAuth setup. A second machine is optional later evidence, not a prerequisite for starting stage 2.

Commands already in LOCAL_SETUP are the unpinned baseline, not a frozen v1 reproduction recipe. Concrete lock/install commands, output destination, expected downloads and time/disk estimates will be supplied with the implementation proposal; none are approved/executed by this plan.

Keep secrets, model weights and private Calendar traces outside Git. Any public environment record must omit credential contents, private URLs/tokens, Calendar identifiers and unnecessary local account/path details. Read-only model metadata queries are distinct from inference; neither substitutes for actual setup verification.
