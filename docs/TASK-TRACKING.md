# Central DevHub Task Tracking

One private backlog covers DevHub and all my personal projects, including both homelab repositories. The homelab is part of DevHub's personal-project ecosystem, not a separate planning organization: repository permissions and release boundaries do not need separate backlogs.

---

## Table of Contents

- [Why track work centrally](#why-track-work-centrally)
- [Project setup](#project-setup)
- [Everyday workflow](#everyday-workflow)
- [Privacy and boundaries](#privacy-and-boundaries)

---

## Why track work centrally

I originally captured homelab ideas in a Word document, but without a clear status, scope, or next step I often started open-ended work and felt pressure to finish it. The problem was not Word: I needed somewhere reliable to leave unfinished work.

Small tasks, visible status, and a resumption note let me stop deliberately and return without reconstructing the context. A single overview also avoids coordinating separate backlogs for packages, automation, shared guidance, and their consumers. I am the only maintainer, and all this work is part of my wider DevHub.

[GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) keeps issues, pull requests, and planning together without another service to host or task descriptions to synchronize. I use it for lightweight planning, implementation, and verification, not sprints, estimates, deadlines, or a team delivery process.

TODO: add more explanation why central tracking, such as I treat personal projects as basically 1 team/job where you have 1 central backlog to manage all tasks, priorities, and progress consistently across different repositories and projects. I only have so much time for personal projects and that central tracking helps me allocate it effectively without losing sight of any ongoing work; if you have 1 backlog per project it would not be very good, etc.

TODO: make sure also add why this is private: it may contain sensitive information, such as for my homelab, and also not necessary to open to the public what I worked on, how, etc., that is not necessary and kept to myself, etc.

---

## Project setup

Use the existing private [personal project board](https://github.com/users/CollinPoetoehena/projects/7) as the central **DevHub** project; access is required. It was originally set up for Homelab. To consolidate without losing tasks:

1. In its settings, rename it **DevHub** and set the description/README to link to this guide. Keep the existing URL and items rather than making another board.
2. Explicitly verify **Private** visibility before adding personal or sensitive work. Repository visibility does not set project visibility.
3. Keep a **Board** view and a **Status** field with **TODO**, **In progress**, and **Done**. The existing **Team Planning** template is sufficient; iteration and sprint views can stay unused.
4. Use a project/category field or labels for DevHub, homelab, SDKs, and other projects when filtering helps. Keep one shared status workflow.
5. Add tasks from all personal projects to this board. Keep public issues in their owning public repository only when safe to publish; use private-repository issues or private project draft items for private work.
6. Link the board from DevHub's repository and add other repository links where useful. Linking a public repository does not require making the project public; verify the project's own access settings.

These are the desired board settings, not a claim that the remote project has already been renamed. Its URL remains the entry point during consolidation.

---

## Everyday workflow

1. Capture one useful task with its goal, relevant repository links, and a clear completion check.
2. Break large efforts into small related subtasks with a next action. Link supporting design context rather than copying it into every item.
3. Pick a TODO when I have time, move it to In progress, and keep the active set small.
4. Validate the result, link the relevant change, close the issue where applicable, and mark the item Done. Capture follow-ups separately.
5. Before stopping, leave the last result and next step in a task comment. Defer or drop tasks freely: the backlog is not a debt or a commitment.

The repository's existing [TODO notes](../TODO.md) are working material to triage, not a second maintained board. This setup does not automatically publish or bulk-import their contents.

---

## Privacy and boundaries

A private project does **not** make a public issue private. Keep private designs, inventories, operational results, and sensitive planning out of public issues; secrets belong in protected storage, not task descriptions.

Task tracking is meant to reduce pressure. Do not mix personal tasks into work time or treat an alert or a waiting build as a demand to start more work. For homelab-specific enjoyment, focus, and optional timeboxes, follow its [goals and scope](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/01-foundations/goals-and-scope.md#relaxation-and-enjoyment-over-productivity-and-pressure); the task workflow itself has one home here.
