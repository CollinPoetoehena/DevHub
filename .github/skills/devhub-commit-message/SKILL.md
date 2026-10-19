---
name: devhub-commit-message
description: "Create a Git commit message and copy-ready commit/push commands from all current pending changes. Use when asked to summarize a diff for a commit, including manual changes or work done without another skill."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-commit-message/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request asks for only a commit subject, omit the body from the response. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Commit Message from Current Changes

Create a commit message for the current pending changes. Do not implement changes, edit files, stage files, commit, or push; provide the message and commands for the user to execute.

The other DevHub skills include commit-message guidance as the final handoff to a larger workflow. This standalone skill is still useful after substantial manual edits, a long mixed session, or a general Copilot conversation without a relevant skill: invoking a full implementation or documentation workflow just to summarize the current diff adds irrelevant steps and context. This skill gives that distinct, recurring finish-up task its own direct entry point and focuses on the entire accumulated change set.

Some overlap with the other skills is intentional: repeating the necessary steps makes this workflow independently discoverable and usable even when no other customization is active. It must not rely on the other skills for instructions or become a prerequisite for them. Keep it focused on reviewing pending changes and preparing a message and commands; for a one-off message that does not need this workflow, use ordinary Copilot chat instead.

---

## Table of contents

- [Discover Repository Guidance](#discover-repository-guidance)
- [Inspect the Complete Change Set](#inspect-the-complete-change-set)
- [Compose and Check the Message](#compose-and-check-the-message)
- [Completion Report and Git Handoff](#completion-report-and-git-handoff)

---

## Discover Repository Guidance

1. Identify the owning Git repository. If the workspace contains multiple repositories, use the requested repository; do not combine changes across repository boundaries. Report when no Git repository or safe scope can be established.
2. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, and directory-specific guidance. Look for commit conventions in `README.md`, `CONTRIBUTING.md`, development guides, commitlint configuration, and recent commit subjects.
3. Treat common filenames as candidates, not requirements. If they do not reveal the conventions, inspect the repository layout, search relevant filenames and contents, and follow existing entry-point links. Keep discovery focused and respect access restrictions.
4. Follow explicit repository commit conventions. If none exist, infer a concise style from recent history without assuming Conventional Commits are required. Track which files were actually read and used, inferred conventions, and missing guidance.

---

## Inspect the Complete Change Set

1. Use read-only Git commands with pagers and external diff helpers disabled. Inspect `git status --short`, `git --no-pager diff --no-ext-diff --no-textconv`, and `git --no-pager diff --cached --no-ext-diff --no-textconv`. Read the actual diffs, not just file names, statistics, or the latest chat request.
2. Review relevant untracked files using file-reading tools; they are not included in those diffs but `git add -A` will stage them. Account for additions, modifications, deletions, renames, and staged/unstaged changes to the same file. Inspect the combined tracked diff against `HEAD` when needed to understand the final result; for a repository without commits, use the staged diff and file contents.
3. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes and edits by the user or others, not only the latest task or your own edits. Do not claim ownership or validation of others' work.
4. Read enough surrounding source or documentation to describe the change accurately. For large diffs, review them in bounded file groups. Do not infer contents of restricted files or claim binary, inaccessible, conflicted, or unread changes were reviewed; report limitations explicitly.
5. Flag unrelated changes, unresolved merge conflicts, suspected sensitive files, or incomplete review. Do not provide a ready-to-run all-changes command when the change set cannot safely be included; explain what needs review or separation without staging, removing, or fixing anything yourself.

---

## Compose and Check the Message

1. Write a concrete, concise subject describing the combined purpose and scope. Follow discovered conventions for prefixes, tense, and subject length. Do not add a co-author trailer.
2. Add a short body when the breadth or significance of the changes warrants it. Summarize major changes and verified breaking changes or migration requirements; do not merely list every file.
3. Check the subject and body against all reviewed changes. Do not describe only the latest edit, invent intent, or claim tests passed without evidence. If changes have separate purposes, flag that separate commits may be clearer rather than concealing unrelated work under a misleading subject.
4. Inspect the current branch, upstream, and configured remotes without contacting them. For a branch with an upstream, suggest `git push`; without an upstream, use `git push --set-upstream` with a verified remote and current branch. If detached, no remote is suitable, or the target is ambiguous, report the blocker rather than inventing a branch or push target.
5. Ensure command arguments are safely shell-quoted, including commit messages, branch names, and remote names. Use separate `-m` arguments for subject and body when needed. Do not include placeholders in a purportedly ready-to-run command.

---

## Completion Report and Git Handoff

Present the proposed commit message, a brief summary of the scope reviewed, and any blockers or limitations. Identify files actually used for repository guidance and structure and each file's role; state inferred conventions and missing dedicated guidance. Report checks actually performed, not unrun builds or tests. This message-only workflow does not need to run application tests.

Before the final block, remind the user to review the diff: `git add -A` stages all changes, including unrelated edits. End with a copy-ready `sh` block containing `git add -A && git commit` with the concrete message, followed by `&& git push` or the verified upstream-setting variant. The message must reflect the full pending scope reviewed above. Do not add a co-author trailer, and do not execute the commands.

If there are no pending changes, the task is outside Git, or a safe commit/push sequence is blocked, explain why the commands are omitted or incomplete. Provide a draft message only for the changes you can substantiate, clearly labeling any incomplete scope.
