# Local source control

This repository uses local Git with the GitHub remote [rachelwuw/agentic-ai-quality-harness](https://github.com/rachelwuw/agentic-ai-quality-harness). A commit records a reviewable checkpoint of source, tests, evaluation definitions, documentation and selected controlled baseline reports. It does not publish to GitHub.

## Included and excluded

Track src/, tests/, evals/, project dependency declarations, documentation and selected reports/baseline/ evidence. Exclude virtual environments, caches, LM Studio weights, OAuth credentials/tokens, local environment secrets and routine reports/runs/. Keep real private calendar traces outside committed baselines.

## Current checkpoint

v0.2 Development Preview: real read-only Calendar availability, local SUT, custom agent loop, MCP adapter, deterministic tests, controlled agent evaluations and a local judge. Known semantic failures and judge limitations are retained as evidence. Event creation and complete migration doctor/dependency locking remain pending. This checkpoint adds trace-derived facts and criterion-level evidence analysis; Judge remains advisory. It is not release signoff. The Python package version is 0.2.0.dev0. Commit locally before any separately requested push; tag creation is optional and must refer to a reviewed commit.

## Daily workflow

All changes follow **branch → commit/push → PR → CI passes → merge**. Do not push directly to `main` or use routine bypasses. Preserve uncommitted work before switching branches.

```sh
git status
git fetch origin main
git switch -c docs/my-change origin/main
# Make and inspect the changes; stage only the reviewed files.
git diff
git add SOURCE_CONTROL.md
git diff --cached
git commit -m "Describe the concrete change"
git push -u origin docs/my-change
```

Open a pull request from the task branch to `main`. Wait for the existing **`pytest`** required status check supplied by **GitHub Actions** (workflow: `Deterministic tests`). The branch must be up to date with `main`; update it and wait for CI again if the base changes. Merge through the PR after the check succeeds and merge authorization is available. Confirm the PR is merged, then fetch and fast-forward the local `main`; a local commit or branch push does not mean the PR has merged.

The `main` branch policy requires a PR, **0 approving reviews**, and no Code Owner or other-person approval. Deletion and force pushes are blocked; no routine bypass is configured. Restrict updates, signed commits and deployment requirements are not part of this policy. The short agent guidance is in [AGENTS.md](AGENTS.md).

A tag names a reviewed checkpoint. Do not move existing checkpoint tags to newer work. Local Git history is not an off-machine backup; pushing the task branch provides a remote copy while merging publishes it on `main`. A new machine should clone the source and recreate `.venv` and runtime/model installations, then configure secrets and reauthenticate Google.
