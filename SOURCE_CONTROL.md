# Local source control

This repository uses Git locally. A commit records a reviewable checkpoint of source, tests, evaluation definitions, documentation and selected controlled baseline reports. It does not publish to GitHub.

## Included and excluded

Track src/, tests/, evals/, project dependency declarations, documentation and selected reports/baseline/ evidence. Exclude virtual environments, caches, LM Studio weights, OAuth credentials/tokens, local environment secrets and routine reports/runs/. Keep real private calendar traces outside committed baselines.

## Current checkpoint

v0.1 development preview: real read-only Calendar availability, local SUT, custom agent loop, MCP adapter, deterministic tests, controlled agent evaluations and a local judge. Known semantic failures and judge limitations are retained as evidence. Event creation and complete migration doctor/dependency locking remain pending. This checkpoint is not release signoff.

## Daily workflow

Run these in the repository terminal:

```sh
git status
git diff
# Stage only reviewed changes, then inspect the staged result.
git add src/ tests/ evals/ README.md
git diff --cached
git commit -m "Describe the concrete change"
git log --oneline
```

A tag names a checkpoint. Do not move existing checkpoint tags to newer work. No remote is required for local commits. Local Git history is not an off-machine backup; GitHub or another backup can be configured separately later. A new machine should clone the source and recreate .venv and runtime/model installations, then configure secrets and reauthenticate Google.
