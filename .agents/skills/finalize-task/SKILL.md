---
name: finalize-task
description: "Use before handing off an implementation task or performing an authorized commit or push: check completion evidence and learning, verify publishing state, and provide copy-ready commands for remaining Git actions."
---

# Finalize Task

Use the existing task record and ordinary Git commands. No scripts, hooks, JSON schema, or fingerprint setup is required. This checklist guides behavior; it does not enforce compliance.

## Procedure

1. **Confirm completion.** Check acceptance criteria, required guidance read, validation results, and self-learning disposition. Standard tasks require independent review of the final changes; Tiny tasks may omit review with a reason. After any edit, rerun affected checks and renew applicable review. Report missing evidence, failed checks, and unresolved findings as blockers.
2. **Inspect the worktree.** Run `git status --short`, `git diff`, `git diff --cached`, and `git diff --check`; disable Git pagers. Inspect task-owned untracked files separately. Account for accumulated task changes across turns and exclude unrelated or already committed work.
3. **Check authorization.** Commit and push each require separate explicit user permission. Without it, do not execute that action; prepare the remaining Git commands for the user's review and execution.
4. **Commit when authorized.** Use the available `git-commit` skill for preparation. Stage only reviewed task paths or hunks; preserve unrelated staging and stop if ownership cannot be separated safely. Inspect the complete staged diff and run `git diff --cached --check` before committing. Use `<type>(<optional-scope>): <concise imperative summary>` and a useful body when needed. Do not add `Co-authored-by:` trailers; `-m` is valid Git syntax, not a trailer.
5. **Verify the actual commit.** Inspect `git log -1 --format=fuller` and `git show --stat --oneline HEAD`, plus the committed diff. Confirm the intended changes and full message, including any hook-added content. If unexpected content or a prohibited trailer appears, stop and report it before push; do not amend, reset, or bypass hooks without authorization.
6. **Push when separately authorized.** Confirm the branch, intended remote, and outgoing commits; do not push unrelated history or guess a missing destination. Push explicitly without force, then compare `git rev-parse HEAD` with `git ls-remote <remote> refs/heads/<branch>`. Report push failures or mismatches, never success by assumption.

## Output

Give a proportional handoff: outcome, exact checks and review results, remaining blockers, and actual commit/push state. Report a commit identifier or verified remote state only after execution.

- **Self-learning:** always include the assessment's disposition and evidence-based reason in the final response, not just internal notes. For `updated`, link the owning edits and summarize the lesson and validation; for `proposed`, describe the proposal and why it was not applied; for `already-covered`, link the existing guidance and explain its coverage; for `none`, explain why the task yielded no reusable lesson. Missing assessment evidence is a blocker.
- **Git commands:** whenever task changes remain uncommitted or unpushed, always include one copy-ready shell block for the remaining actions, explicitly labeled as not executed and for the user to review before running. For an uncommitted task, chain explicit task-path `git add`, `git commit` with a concrete Conventional Commits message, and `git push` with `&&` so the user can execute the reviewed sequence immediately. Do not split push into a separate block or insert an interactive confirmation. After an authorized and verified commit, include only the remaining push. This user-executed sequence is distinct from agent-executed publishing, which still requires the separate authorization and post-commit verification above. If all publishing is verified complete or there are no task changes, state that instead.
- Resolve the repository path, task-owned paths, branch, remote, destination branch, and outgoing history from Git evidence. Use `git -C` (or an explicit `cd`), quote paths and message arguments safely, and stage explicit paths rather than `git add .`/`-A`. Preserve unrelated staging and mixed file changes; do not suggest a whole-index commit that includes unrelated work. If ownership, failed checks/review, detached HEAD, unknown destination, or unrelated outgoing commits prevent a safe sequence, state the specific blocker and provide only safe commands rather than inventing values or offering an unsafe publish sequence. Never force-push or bypass hooks. Suggested commands do not grant the agent authorization or count as executed actions.
