# Central DevHub Task Tracking

The existing [DevHub project board](https://github.com/users/CollinPoetoehena/projects/7) is the shared, actively used backlog for DevHub and my personal projects, including both homelab repositories. It gives me one place to capture work, choose what to do next, and see progress across repositories without merging their code, permissions, or release boundaries.

---

## Table of Contents

- [Why track work centrally](#why-track-work-centrally)
- [How the board is organized](#how-the-board-is-organized)
- [Using Current Iteration to focus](#using-current-iteration-to-focus)
- [Everyday workflow](#everyday-workflow)
  - [Drafting an issue](#drafting-an-issue)
- [Visibility and boundaries](#visibility-and-boundaries)
- [References](#references)

---

## Why track work centrally

I originally captured homelab ideas in a Word document, but without a clear status, scope, or next step I often started open-ended work and felt pressure to finish it. The problem was not Word: I needed somewhere reliable to leave unfinished work.

Small tasks, visible status, and a resumption note let me stop deliberately and return without reconstructing the context.

I am the only maintainer and treat my personal projects as one team with one shared backlog, not separate planning organizations per repository. My limited personal-project time is shared across all of them. One backlog lets me compare priorities, allocate that time deliberately, and track progress consistently without losing sight of ongoing work. Separate backlogs would fragment that overview and make me coordinate competing priorities across projects, packages, automation, shared guidance, and their consumers.

[GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) keeps issues, pull requests, and planning together without another service to host or task descriptions to synchronize. A single project can include work from multiple repositories, so I can keep repository-specific discussions and changes where they belong while using the board for a cross-repository view. I use it for lightweight planning, implementation, and verification, not formal sprint commitments, deadlines, or a team delivery process.

---

## How the board is organized

The existing private personal project is the central **DevHub** board. It has a **Board** view and a shared **Status** field:

- **TODO** — captured and ready to be considered.
- **In progress** — actively being worked on; keep this set small.
- **Done** — completed and checked.

Use a project/category field or labels to distinguish DevHub, homelab, and other work when that makes filtering useful. Add repository issues and pull requests directly to the board rather than copying their descriptions into separate tasks. Use a project draft item for an idea that does not yet belong to a repository issue or pull request. Link the board from repositories where it is useful as an entry point.

The board is a lightweight personal backlog, not a commitment to finish every item. The **Current Iteration** is useful as a focus aid, not a sprint commitment: iteration dates do not create deadlines. Other iteration or sprint features are optional and do not imply a delivery schedule.

## Using Current Iteration to focus

Use **Current Iteration** to select a manageable portion of the backlog to focus on now. Pick a few items that suit your available time and interest, then work through them at a comfortable pace. When that portion is complete—or you want to shift focus—choose the next set of items. The rest of the backlog can wait.

This is a way to narrow the choices and make progress easier to resume, not strict planning. Do not treat the iteration's date range as a deadline, promise, or requirement to finish everything assigned to it. Move, defer, or remove items whenever priorities, energy, or available time change.

## Everyday workflow

1. Capture work in the repository issue when it is specific to that repository. State the goal, relevant context, priority, estimate (helps scoping and planning), and a check for completion. Use a draft item for early ideas that do not need a repository issue yet. Add it to the board to keep it visible and track its status (see [GitHub Issues documentation: Creating an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue) and [GitHub Projects documentation: Adding items to your project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/adding-items-to-your-project)).
2. Break large efforts into small related tasks with a clear next action (see [GitHub Projects documentation: Best practices for projects; breaking down large issues](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects#break-down-large-issues-into-smaller-issues)). Link design notes or other context instead of duplicating them in every item.
3. Use **Current Iteration** to pick a manageable portion of TODOs for your current focus. Choose one that fits the time available, move it to **In progress**, and avoid starting more work than can be kept in view.
4. Record useful progress and decisions on the issue or draft item. The board provides the status and cross-repository overview; the issue remains the place for repository-specific discussion.
5. When complete, verify the result, link the relevant pull request or change, close the issue where applicable, and mark it **Done**. Capture follow-ups separately.
6. Before stopping, leave the last result and next step in a comment. Defer or drop tasks freely; the backlog is not a debt or a commitment.

### Drafting an issue

Use the common APM package's [draft-github-issue skill](../packages/apm/common/.apm/skills/draft-github-issue/SKILL.md) with the task idea and this guide as context. It returns only Markdown: a proposed title followed by the issue body, without publishing an issue or changing the board.

For DevHub, identify the owning repository, keep the work small enough to pause and resume, and include priority with a short rationale and a rough effort estimate with uncertainty. If either is unknown, say so rather than inventing it. Use observable acceptance criteria, link dependencies where relevant, and include a clear first action. Keep status and Current Iteration on the board rather than duplicating them in the issue body; iteration dates are not deadlines. Follow the [visibility rules](#visibility-and-boundaries) before sharing context.

Example request:

> Use draft-github-issue to draft an issue for DevHub: \<task idea\>. Tailor it using docs/TASK-TRACKING.md. Return only the issue Markdown.

Review the draft, use its first heading as the GitHub title and the remainder as the body, then add the issue to the [DevHub board](https://github.com/users/CollinPoetoehena/projects/7). Ideas without a clear repository or scope can remain draft items.

## Visibility and boundaries

A public issue in a public repository is expected to remain public when added to this private project. That is normal for DevHub and other public repositories: the project organizes the issue but does not change its visibility. Do not duplicate a public issue as a private draft merely because it appears on the private board.

Keep information that should not be public—such as private designs, inventories, or operational details—out of public issues. Use an appropriately private repository or project draft for private planning, and store secrets only in protected storage, never in task descriptions. Project visibility and repository/issue visibility are separate settings.

These are personal projects meant to be fun and enjoyable, not another source of stress on top of a job. There is no quota, schedule, deadline, or obligation to keep the board moving. Take breaks, change focus, defer work, or drop tasks freely. Do not mix personal tasks into work time or treat an alert or a waiting build as a demand to start more work. For homelab-specific enjoyment, focus, and optional timeboxes, follow its [goals and scope](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/01-foundations/goals-and-scope.md#relaxation-and-enjoyment-over-productivity-and-pressure); the task workflow itself has one home here.

## References

- [About GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) — project capabilities, views, fields, and workflows.
- [About iteration fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-iteration-fields) — how iteration fields group and filter project items.
- [Filtering projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects) — focus a project view on selected items.
- [Adding items to a project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/adding-items-to-your-project) — add issues and pull requests from repositories, including adding multiple items.
- [Creating a project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project) — project types and setup.
- [Using built-in automations](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations) — optional project workflows.
