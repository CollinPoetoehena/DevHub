---
name: finalize-task
description: "Use before handing off an implementation task or performing an authorized commit or push: check the final changes, validation, review, learning, and actual publishing state."
---

# Finalize Task

Use the existing task record and ordinary Git commands. No scripts, hooks, JSON schema, or fingerprint setup is required. This checklist guides behavior; it does not enforce compliance.

## Procedure

1. **Confirm completion.** Check acceptance criteria, required guidance read, validation results, and self-learning disposition. Standard tasks require independent review of the final changes; Tiny tasks may omit review with a reason. After any edit, rerun affected checks and renew applicable review. Report missing evidence, failed checks, and unresolved findings as blockers.
2. **Inspect the worktree.** Run `git status --short`, `git diff`, `git diff --cached`, and `git diff --check`; disable Git pagers. Inspect task-owned untracked files separately. Account for accumulated task changes across turns and exclude unrelated or already committed work.
3. **Check authorization.** Commit and push each require separate explicit user permission. Without it, report the uncommitted/unpushed state; provide commands only when useful or requested.
4. **Commit when authorized.** Use the available `git-commit` skill for preparation. Stage only reviewed task paths or hunks; preserve unrelated staging and stop if ownership cannot be separated safely. Inspect the complete staged diff and run `git diff --cached --check` before committing. Use `<type>(<optional-scope>): <concise imperative summary>` and a useful body when needed. Do not add `Co-authored-by:` trailers; `-m` is valid Git syntax, not a trailer.
5. **Verify the actual commit.** Inspect `git log -1 --format=fuller` and `git show --stat --oneline HEAD`, plus the committed diff. Confirm the intended changes and full message, including any hook-added content. If unexpected content or a prohibited trailer appears, stop and report it before push; do not amend, reset, or bypass hooks without authorization.
6. **Push when separately authorized.** Confirm the branch, intended remote, and outgoing commits; do not push unrelated history or guess a missing destination. Push explicitly without force, then compare `git rev-parse HEAD` with `git ls-remote <remote> refs/heads/<branch>`. Report push failures or mismatches, never success by assumption.

## Output

Give a proportional handoff: outcome, exact checks and review results, learning disposition, remaining blockers, and actual commit/push state. Report a commit identifier or verified remote state only after execution. Do not treat suggested commands as performed actions.
