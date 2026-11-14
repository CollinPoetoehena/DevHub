---
name: commit-command
description: 'Generate copy-ready git add, git commit, and git push commands with one Conventional Commits message for all current changes. Use when asked for commit commands or at implementation completion; never execute them.'
---

# Commit Command

Analyze the complete current changes and return one command sequence for the user to execute after verification. Do not stage, commit, push, or otherwise modify the repository.

## Message format

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
<type>(<scope>): <summary>

<body>

<footer>
```

- Scope, body, and footer are optional; without a scope, use `<type>: <summary>`.
- Use an imperative summary ("add", not "added" or "adds"), at most 72 characters for the first line, with no trailing period.
- Use the body to explain what changed and why.
- Format footers as `Token: value` or `Token #value`, such as `Refs: #456` or `Closes #123`. Only the colon form is recognized as a Git trailer. Replace spaces in footer tokens with hyphens, except for `BREAKING CHANGE`.

## Types

Conventional Commits defines `feat` and `fix`; the remaining types follow the [Angular-derived convention](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional). Prefer the repository's own type list when provided.

| Type | Use for |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `style` | Formatting without logic changes |
| `refactor` | Code changes that neither add features nor fix bugs |
| `perf` | Performance improvements |
| `test` | New or updated tests |
| `build` | Build system or dependency changes |
| `ci` | CI configuration |
| `chore` | Other maintenance |
| `revert` | Reverting an earlier commit |

## Breaking changes

Put `!` before the colon or add an uppercase `BREAKING CHANGE:` footer; `BREAKING-CHANGE:` is also valid. Explain the incompatibility and required migration.

```text
feat(api)!: remove the v1 endpoints

BREAKING CHANGE: Clients must use the v2 endpoints.
```

## Workflow

1. Find the repository root and read applicable commit rules, commitlint configuration, and recent commit messages.
2. From the root, inspect `git status --long`, `git diff --staged`, `git diff`, and `git ls-files --others --exclude-standard`. Read every non-ignored untracked file and the full diffs, not just filenames or statistics; include additions, deletions, renames, and staged and unstaged changes across the repository, not only this task.
3. Stop with a clear explanation if there are no changes, unresolved conflicts, an in-progress merge/rebase/cherry-pick/revert/am operation, secrets, or changes you cannot fully inspect. Never invent a message from incomplete evidence or suggest an empty commit.
4. Derive one message covering all current changes using the format and types above; do not split commits. Follow repository conventions, use a scope only when accurate, and include a body or breaking-change footer when needed.
5. Check the current branch, upstream, and remotes. Use the configured upstream for pushing; otherwise use `git push --set-upstream` with a verified remote and branch. If detached or the push destination is ambiguous or unavailable, explain the blocker instead of guessing.

## Output

Return only one fenced shell block, with concrete, correctly shell-quoted values and no placeholders or alternative messages:

- Use `git -C <root>` for each command so it works from any directory.
- Chain commands with `&&` so a failure prevents subsequent steps.
- First, `git add -A -- <explicit-reviewed-paths>` covering every reviewed change, including deletions.
- Then, `git commit -m <summary>`, with additional `-m` arguments for any body and required footers.
- Finally, the verified `git push` command.

## Gotchas

- **Generate only**: The user verifies and executes the commands; invocation never authorizes Git writes or network publication.
- **Preserve safety**: Never suggest history rewriting, force-pushing, hook bypasses, Git configuration changes, or staging ignored files or secrets.
