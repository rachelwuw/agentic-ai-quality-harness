# Project work guidance

- Preserve existing uncommitted work and inspect the current branch and remote before editing.
- Use a task branch, commit/push that branch, open a PR to `main`, wait for the required `pytest` check from GitHub Actions, then merge when authorized. Never push directly to `main` or force-push.
- Keep the PR branch up to date with `main`; use no routine ruleset bypass. Required approving reviews are 0; Code Owner approval is not required.
- Keep `main` deletion and force pushes blocked. Do not change branch rules or repository visibility without explicit user authorization.
- See [SOURCE_CONTROL.md](SOURCE_CONTROL.md) for the workflow. Keep secrets, model weights, private Calendar traces and disposable reports out of Git.
