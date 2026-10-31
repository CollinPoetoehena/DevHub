# Repository and Package Guidelines

These are shared, human-readable conventions for organizing DevHub and its projects. Each repository owns its own implementation, user-facing documentation, and exceptions.

---

## Table of Contents

- [Shared guidance and AI customizations](#shared-guidance-and-ai-customizations)
- [Relaxation and Enjoyment over Productivity and Pressure](#relaxation-and-enjoyment-over-productivity-and-pressure)
- [Choosing a repository boundary](#choosing-a-repository-boundary)
- [Placing packages and components](#placing-packages-and-components)
- [Setting up a project or package](#setting-up-a-project-or-package)
- [Naming conventions](#naming-conventions)
- [Package README links](#package-readme-links)

---

## Shared guidance and AI customizations

This file is the single home for shared, human-facing repository, package, and setup conventions. Project docs own user-facing concepts and usage, getting started, local setup, architecture decisions, and task tracking; see [Using DevHub](USAGE.md), [project architecture](ARCHITECTURE.md), and [task tracking](how-to/TASK-TRACKING.md). Link to those docs when useful instead of copying them into agent instructions.

The shared principles for approaching personal projects—including enjoyment, attention, sustainable scope, and freedom from unnecessary pressure—are in [Relaxation and Enjoyment over Productivity and Pressure](#relaxation-and-enjoyment-over-productivity-and-pressure). Individual projects should link to that guidance and keep only their local application and technical details.

Reusable AI customizations, shared engineering standards, and workflows live in the [common APM package](../packages/apm/common/README.md), which is the authoring source for these customizations:

- Agents define role responsibilities and workflows: [Orchestrator](../packages/apm/common/.apm/agents/orchestrator.agent.md), [Architect](../packages/apm/common/.apm/agents/architect.agent.md), [Coder](../packages/apm/common/.apm/agents/coder.agent.md), [Documenter](../packages/apm/common/.apm/agents/documenter.agent.md), and [Reviewer](../packages/apm/common/.apm/agents/reviewer.agent.md).
- The [common instructions](../packages/apm/common/.apm/instructions/common.instructions.md) are the single source for shared engineering, testing, and documentation standards. Technology- or tool-specific instructions add relevant constraints, such as [AI customization](../packages/apm/common/.apm/instructions/ai-customization.instructions.md), [Ansible](../packages/apm/common/.apm/instructions/ansible.instructions.md), [Dockerfile](../packages/apm/common/.apm/instructions/dockerfile.instructions.md), [GitHub Actions](../packages/apm/common/.apm/instructions/github-actions.instructions.md), and [Python](../packages/apm/common/.apm/instructions/python.instructions.md).
- Skills capture focused, repeatable procedures; the current shared example is [manage-skills](../packages/apm/common/.apm/skills/manage-skills/SKILL.md).

Consumer-specific context belongs in one root `AGENTS.md`, with scoped instructions or local skills only for a demonstrated need. Follow the [APM design and setup guide](../packages/apm/README.md) for ownership, authoring, and discovery verification. These customizations supplement the common package; do not duplicate shared standards or assume one instruction automatically overrides another.

The engineering and documentation rules are intentionally not repeated in this file: `GUIDELINES.md` is the shared human-facing home for repository and package conventions, while `common.instructions.md` is the reusable AI-facing source for engineering standards. Keeping each topic in one authoritative place avoids drift when one copy is updated and another is missed, prevents conflicting or stale directions, and makes clear which guidance to maintain.

---

## Relaxation and Enjoyment over Productivity and Pressure

Personal projects are part of life, not another source of pressure. They should make room for curiosity and enjoyment alongside work, everyday responsibilities, other interests and rest. These principles first grew out of the homelab, but they apply to all my personal projects. Since the homelab is part of DevHub, DevHub is their shared home; individual projects should link here and retain only their local application and technical details.

**Guiding principle:** I want to learn and experiment without turning enthusiasm into an obligation to make constant progress, perfect every detail or finish every idea. Optional boundaries help me stop, pause or leave work unfinished; the goal is to enjoy the process of personal projects at a pace that fits the rest of life.

The details below describe how to put this principle into practice:

- **A hobby, not a second job:** Treat personal projects as hobbies and places to learn, not productivity targets; success is not measured by delivery speed, backlog completion, the number of services kept online or resemblance to a production environment. There is no required pace, deadline or finish line. Understanding an idea, following curiosity, repeating an experiment or deciding not to keep a project can all be worthwhile outcomes. For me, hands-on problems are relaxing as well as interesting: I can focus on an idea, see it take shape, follow questions naturally and enjoy making things work. Curiosity—not a deadline, customer or pressure to deliver quickly—should guide the work. Some sessions are challenging or frustrating, but the freedom to experiment, learn from mistakes and take breaks keeps the experience from becoming an obligation. Make room for exploring, building, observing, troubleshooting and learning. It is fine to leave an experiment unfinished, simplify a design or return to it later. Do not add automation, complexity or extra work merely to appear efficient or match someone else's setup; choose the amount of structure that helps you learn and enjoy the work. Relaxed does not mean careless: keep experiments reversible and within a sustainable scope, and account for responsibilities involving important data or other people. Boundaries protect others and preserve enjoyment; they are not an uptime contest.
- **Timebox without turning it into a deadline:** Choose optional project times if that helps prevent work from expanding into every spare moment (in my case it does, so I always apply this strategy). A schedule is a gentle boundary for attention, not a promise, quota, or deadline. Keep it regular, make it flexible, set it week by week, or skip it altogether; do what works best for you and fits within your schedule (or make it fit into your schedule), etc. For example, Friday afternoons could be the usual time, with Saturday mornings as an additional option every week; generally keep Sundays free, working then only if I want to really badly and/or have/want nothing else to do (even then try to leave time for other things, such as family and exercise, etc.). Start a session with something interesting or a manageable next step, and use its end as a natural cue to stop, even if the task is unfinished. Stop earlier, skip a session or use the time for something else whenever you want. Ordinary project work and unfinished experiments can wait; handle credible emergencies affecting safety or an essential service appropriately. Timeboxing is not a way to get more done or finish within an estimate. Do not race the clock, measure success by completed tasks or turn a missed session into debt; a satisfying session—or choosing to stop and rest—is worthwhile even if nothing is finished. Before stopping, note where you got to, what you observed and the next useful step in a low-friction place you will find again. [Central DevHub Task Tracking](how-to/TASK-TRACKING.md) describes the optional shared backlog; no particular tracker is required.
- **Focus on one context at a time:** Focus on work while working, on a personal project during chosen project time, and on other people or rest when that is what you are doing. A notification, interesting idea or AI response is not permission to interrupt. Learning at home that later helps at work does not make personal work a work task. Switching between demanding activities requires rebuilding context: the goal, changes, assumptions and checks still needed. Unfinished thoughts can linger and make it harder to settle into the next activity. Similar tools across projects do not make their environments, responsibilities or goals interchangeable; mixing contexts can lead to acting in the wrong place. Repeated switching can make activities take longer and reduce their quality, encouraging rushing, skipped verification and feeling behind in both contexts. Focus is not about squeezing productivity from every minute; give the chosen activity enough attention to do it carefully and enjoy it. Related subtasks within one larger task can share context if they do not conflict, and each result should be reviewed before relying on it. Waiting is valid; idle time does not always need filling. When another task must be handled, make a deliberate switch, leave a brief resumption note and return at a clear stopping point where possible. Staying within work preserves the work/personal boundary, but is not a reason to start personal work alongside it.
- **Notifications from personal projects are not automatic interruptions:** Routine project alerts from personal projects do not need immediate assessment. Experimental downtime is normally acceptable; let ordinary alerts wait until chosen project time or configure them not to interrupt in the first place. Prompt attention is for a credible emergency only, such as verified signs of compromise, immediate physical danger, imminent loss of important data or an essential service being affected. A generic warning or offline experiment is not itself an emergency, and there is no need to investigate routine alerts just in case. Reduce risk with sensible security and recovery practices: keep systems patched, restrict access, separate experiments from essential services and maintain recoverable backups. Decide in advance which trustworthy signals warrant interruption and what safe first response is appropriate; these controls reduce risk but cannot guarantee incidents will never happen. Avoid watching dashboards, chat notifications or AI sessions during work, errands or rest. Defer routine alerts outside chosen project time, group related notifications and silence expected maintenance while preserving a deliberate path for genuine emergencies. If you feel compelled to check, fix or continue, step back: reduce notifications, pause or retire the experiment, simplify it, or move an important responsibility to a service you do not have to operate. Taking a break is valid; personal 24/7 on-call coverage is not the goal.
- **Keep other people's dependencies out of experiments:** Technical independence makes it easier to leave experiments alone. Keep household internet, Wi-Fi and essential name resolution available when experimental infrastructure is off, broken or being rebuilt. A stable shared foundation can still need maintenance; independence means it does not depend on experimental compute, cluster workloads, storage or management systems. If other people or important data depend on a service, acknowledge its patching, backup and recovery obligations; calling it a hobby does not remove them. You do not need to self-host every useful service or move important data into an experiment. Hosted or local-first alternatives may leave more time for work you enjoy. Choose responsibilities consciously rather than letting an experiment become essential. The homelab-specific household-dependency and design guidance is in the [Goals and Scope chapter](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/01-foundations/goals-and-scope.md).
- **Keep the scope sustainable:** Prefer a small stable foundation and disposable experiments. One host can teach many concepts; add resources for capacity, physical-failure practice or actual availability needs, not appearance. Use automation when it saves work or supports learning, not when it makes every simple task a development project. Limit ongoing responsibilities to what you are willing to maintain without crowding out work, other interests or rest. Account for time and operational costs as well as purchase costs: free software still needs updates and recovery, and hardware still consumes electricity. Prefer a well-understood service with tested recovery over a long list nobody can operate after an outage. Give experiments a deliberate lifecycle: create, observe, learn, then remove or promote. Automate repeatable rebuilds where supported and decide what evidence to collect. Promotion to a responsibility affecting others adds ownership, monitoring, access controls and data recovery, not merely a restart policy. Preserve learning when infrastructure goes away by recording outcomes in short notes.
- **Write it down and return when ready:** Use task tracking to capture ideas, not to demand action. A short note with the next action, context and a link makes it easier to return. If an idea occurs outside project time, capture it briefly when appropriate and safe, then return to the current activity rather than opening an investigation. Tasks can wait until you have time and interest; they can also be deferred or dropped. Split larger tasks into small, related subtasks with clear outcomes. Choose one manageable next step, keep the active set small, and record what was checked and where to resume. This structure avoids holding unfinished details in memory or finishing everything in one sitting. The board protects the one-context-at-a-time boundary; it is not a scoreboard or a reason to start several unrelated tasks. There is no requirement to work on a project every day, clear every TODO, answer every notification or maintain experiments around the clock. If structure creates pressure, make it lighter; the purpose remains enjoyment, curiosity and peace of mind.

---

## Choosing a repository boundary

Keep related work together when it shares ownership and access, changes together, and is maintained or validated as a coordinated unit. Split it when a distinct service, owner, access requirement, operational lifecycle, or publication boundary makes independent work valuable. Size, language, or independent package versions alone do not require a repository split.

DevHub keeps shared development resources, tooling, guidance, and setup together because one maintainer frequently changes them in coordination; the [architecture guide](ARCHITECTURE.md#why-devhub-is-one-repository) records the rationale and accepted trade-offs. Distinct applications and services belong in their own repositories when those boundaries apply.

---

## Placing packages and components

- Keep implementation-local helpers with the application that uses them. Create a reusable package for a real public interface or consumer need.
- Treat the managed contract—not the directory count or programming language—as the release boundary. Independently versioned packages may share a repository; document the consumer contract and compatibility explicitly.
- Keep native package metadata and artifact identities. Add CI and release automation at the component's scope, including checks for affected consumers.
- Record the choice and exceptions in the owning project or package README, then track the work in the central DevHub backlog. Revisit the boundary when consumers or maintenance costs change.

For the architectural rationale and release examples, see [Release and versioning units](ARCHITECTURE.md#release-and-versioning-units).

---

## Setting up a project or package

- Give each project and package an owning README that explains its purpose, setup, supported use, and project-specific decisions. Keep detailed commands and operational procedures with the component.
- Before publishing a component, document its consumers, native metadata, validation commands, release tags, artifact destination, and upgrade or rollback steps.
- Link to shared DevHub guidance from the project's README instead of copying it. The [workspace and AI setup guide](USAGE.md) explains how consumers use shared resources.
- Consumers own their triggers, credentials, and deployment configuration when using shared automation.

Use the official [Python Packaging User Guide](https://packaging.python.org/en/latest/overview/) and [Go module documentation](https://go.dev/doc/modules/developing) for ecosystem-specific mechanics.

---

## Naming conventions

Use `devhub-{category}-{project}` for focused repositories. Broader existing names such as DevHub and devhub-homelab remain meaningful exceptions. Native package identifiers follow ecosystem requirements; a repository name does not override an existing import or module path.

---

## Package README links

Package READMEs own their setup, supported behavior, decisions, and exceptions. Link to relevant official ecosystem documentation rather than duplicating general technical references. When a package needs DevHub's project-specific architecture context, link it once:

```markdown
> For DevHub's project boundaries and release design, see
[DevHub architecture](https://github.com/CollinPoetoehena/DevHub/blob/main/docs/ARCHITECTURE.md).
This README covers this package's setup, usage, design decisions, and exceptions.
```
