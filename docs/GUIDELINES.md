# DevHub Guidelines

These are shared, human-readable conventions for organizing DevHub and its projects. Each repository owns its own implementation, user-facing documentation, and exceptions.

---

## Table of Contents

- [Shared guidance and AI customizations](#shared-guidance-and-ai-customizations)
- [Documentation Design](#documentation-design)
  - [Documentation ownership](#documentation-ownership)
  - [Documentation placement](#documentation-placement)
  - [Architecture decision records (ADRs)](#architecture-decision-records-adrs)
- [Relaxation and Enjoyment over Productivity and Pressure](#relaxation-and-enjoyment-over-productivity-and-pressure)
- [Version control and repository strategy](#version-control-and-repository-strategy)
  - [Monorepo or polyrepo?](#monorepo-or-polyrepo)
  - [Branches and reviews](#branches-and-reviews)
  - [GitHub Pro for personal practice](#github-pro-for-personal-practice)
- [Placing packages and components](#placing-packages-and-components)
- [Setting up a project or package](#setting-up-a-project-or-package)
- [Naming conventions](#naming-conventions)
- [Package README links](#package-readme-links)

---

## Shared guidance and AI customizations

This file is the single home for shared, human-facing repository, package, and setup conventions. Project docs own user-facing concepts and usage, getting started, local setup, architecture decisions, and task tracking; see [Getting Started](GETTING-STARTED.md), [project architecture](ARCHITECTURE.md), and [task tracking](how-to/TASK-TRACKING.md). Link to those docs when useful instead of copying them into agent instructions.

Keep related project-wide documentation in one cohesive, sectioned authoritative file rather than splitting it into many small files by default. For example, DevHub's overall architecture, repository boundaries, and release rationale belong in [docs/ARCHITECTURE.md](ARCHITECTURE.md); component- or package-specific setup and usage belong in each owner's README. A separate focused document is warranted when it has a distinct owner, audience, or lifecycle, or when its size or format materially improves usability. Choose one owning document for each topic and link to it elsewhere; this is a default, not a mandate to combine unrelated topics into a giant document.

The shared principles for approaching personal projects—including enjoyment, attention, sustainable scope, and freedom from unnecessary pressure—are in [Relaxation and Enjoyment over Productivity and Pressure](#relaxation-and-enjoyment-over-productivity-and-pressure). Individual projects should link to that guidance and keep only their local application and technical details.

The [APM guide](../packages/apm/README.md) owns shared AI customization design and setup. Its [package-design ADR](../packages/apm/adrs/distribution-and-synchronization/PACKAGE-DESIGN.md) separates shared `guidelines-core`, which repositories may adopt independently, from local `development-core` agents/skills and opt-in `development-*` stacks. These source packages are ready; their presence does not establish installation, synchronization, or host discovery.

Consumer-specific context belongs in one root `AGENTS.md`, with scoped instructions or local skills only for a demonstrated need. Follow the [APM design and setup guide](../packages/apm/README.md) for ownership, authoring, and discovery verification. Give each topic one authoritative owner and link to it rather than repeating its guidance. Shared guidelines and local development customizations have separate consumers; do not assume one instruction automatically overrides another.

The engineering and documentation rules are intentionally not repeated in this file: `GUIDELINES.md` is the shared human-facing home for repository and package conventions, while [`guidelines-core` coding instructions](../packages/apm/guidelines-core/.apm/instructions/coding.instructions.md) are the reusable AI-facing source for engineering standards. Keeping each topic in one authoritative place avoids drift, prevents conflicting or stale directions, and makes clear which guidance to maintain.

---

## Documentation Design

### Documentation ownership

Each part or component of the repository owns documentation for its behavior, setup, and decisions. Keep one authoritative home for each topic, place it with the part it describes, and link to it from other relevant documentation rather than duplicating it. Use repository-level documentation for topics that span components or describe the repository as a whole.

For Markdown formatting and writing conventions, follow the shared [documentation guidelines](../packages/apm/guidelines-core/.apm/instructions/documentation.instructions.md).

### Documentation placement

Keep documentation about a project's code, setup, architecture, decisions, and operation in the project repository whenever it belongs with that project. Use Markdown files near the code or configuration they explain, or in the repository's `docs/` directory when the material spans multiple areas. The repository should have one clear, authoritative home for each topic.

Keeping this documentation in Git makes it part of the project rather than a separate reference to maintain:

- Git history records how guidance changed and why; branches, pull requests, and reviews let documentation be considered alongside related code or configuration changes.
- A local checkout keeps the documentation available with the code, including for offline work. Contributors can search it and follow relative links without switching tools or locating a separate page.
- Markdown files can link directly to implementation, configuration, and other documentation. Their proximity makes it easier to keep explanations aligned with the version of the project they describe.
- AI tools working in the repository, such as GitHub Copilot in VS Code, can use local documentation and code together as context. With documentation in an external service such as Confluence, that context may require separate access, integrations, search, or manual copying, and can be harder to keep aligned with a particular checkout, which is unnecessary extra complexity. So, prefer keeping documentation in the repository whenever possible.

An external documentation tool can still be useful for material whose audience, collaboration needs, access controls, or lifecycle are better served there. When it refers to project documentation, make the repository document authoritative and link to it from the external page—for example, link to the relevant README or file in `docs/`—rather than maintaining a second full copy. This keeps the external tool useful as an index or entry point without creating competing versions that can drift.

Choose the storage location based on the content and its access requirements. Do not put secrets or restricted information in a repository unless its access controls and policies explicitly allow it; use an approved system for material that must remain outside source control.

### Architecture decision records (ADRs)

**Guideline:** Use an Architecture Decision Record for a significant architectural choice whose context, alternatives, or consequences will matter beyond the immediate change. An ADR is a standalone, narrowly scoped record of one decision: what problem it addresses, what was chosen, why that choice fits the constraints, and what trade-offs were accepted. It is not a general architecture overview, implementation checklist, or transcript of a discussion.

This is a deliberate exception to the default of keeping related documentation in a cohesive main document. Decision reasoning has a distinct purpose and lifecycle: readers need it when evaluating or revisiting a choice, but usually not when learning how to use the project. Isolating that reasoning makes both kinds of documentation more useful.

Use this separation to:

- **Make the decision explicit and considered:** Put the problem, constraints, assumptions, and credible options on paper before settling on an approach. Compare the options' benefits, drawbacks, and trade-offs against those constraints, then state why the chosen option's positives outweigh its negatives for this context. This makes the choice reviewable rather than an implicit preference or a decision made by default.
- **Separate design from implementation:** An ADR lets you explore and agree on a significant design choice before writing code. You can focus first on what should be built and why, then plan and implement that agreed approach as separate work. This reduces the pressure to make architectural choices while solving implementation details and gives later implementation work a clear design to follow.
- **Preserve the reasoning, not just the outcome:** Record the alternatives considered, their comparative advantages and risks, supporting evidence, and why they were or were not selected. Future maintainers can distinguish a deliberate trade-off from an accidental limitation and identify when changed requirements warrant reconsideration.
- **Keep main documentation focused:** READMEs, architecture overviews, and usage guides should explain the current approach and what readers need to do. Summarize the relevant decision there and link to the ADR for the full comparison; do not make every reader work through rejected options to find setup or usage instructions.
- **Avoid duplication and drift:** Give the decision rationale one authoritative home. Several documents can reference it without maintaining separate explanations that gradually disagree. Keep any concise current-state summaries consistent with the applicable decision.
- **Support focused review and reuse:** A bounded record can be discussed, linked from tasks or pull requests, and supplied as context independently of a large documentation file. Its scope makes clear which part of the system it governs and which neighboring decisions it does not settle.

#### Scope and placement

Keep **one ADR per specific significant decision**, with enough context to understand it independently. Do not combine several independently revisitable choices merely because they were discussed together. A storage backend, a retention policy, and an update mechanism can have different alternatives, owners, and reasons to change; putting them in one large ADR makes it confusing to read and harder to review, maintain, or supersede one decision without affecting the others.

Group related focused ADRs in a descriptive subfolder of the owning ADR directory and link them from its index. Each record owns its rationale and trade-offs; neighboring records link to it rather than copy its full reasoning. The [APM ADR index](../packages/apm/adrs/README.md) groups distribution/synchronization, workflow, and AI-customization decisions this way.

Split by decision boundaries, not an arbitrary line count. A long comparison for one consequential choice may still belong in one record; explanatory sections, constraints, and consequences are not automatically separate decisions. When extracting or moving an existing record, preserve its original decision date, status, rationale, and prior history, and add a dated changelog explaining the reorganization and linking the focused records. Reorganization is not approval of a new policy; a genuinely replaced choice follows supersession conventions.

Store records with the owning component or in its established ADR directory, following that area's naming, status, and date conventions. Repository-wide decisions belong with repository-wide documentation; component-specific choices stay with their component. The [APM ADR directory](../packages/apm/adrs/) is an existing component-level example, not a required location for every DevHub decision.

Create an ADR when a choice materially affects architecture, component boundaries, persistence, dependencies, operational responsibilities, security assumptions, or an enduring engineering workflow. Do not create one for every edit, routine implementation detail, or easily reversible choice with no meaningful wider impact. The depth should reflect the decision's significance, not a document-length target.

#### Writing and referencing records

Include enough context, decision rationale, positive and negative consequences, alternative analysis, and evidence that the record remains useful without the original conversation. Use the [ADR skill](../packages/apm/development-core/.apm/skills/adr/SKILL.md) and its [template and examples](../packages/apm/development-core/.apm/skills/adr/references/ADR-TEMPLATE.md) for authoring guidance, while respecting established project conventions.

In a main document, state the current decision and link to the record at the point where the reader may need its rationale. For example: "Nontrivial work starts with an approved Markdown plan before execution; see the [workflow decision](../packages/apm/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md) for the reasoning and exceptions." The main document still owns behavior, setup, and usage; a link should not force readers into an ADR to discover basic instructions.

Distinguish proposals from approved decisions. When an accepted choice is replaced, preserve its original reasoning, mark it superseded according to the project's conventions, link the replacement, and update current-state documentation to point to the applicable record. An ADR records the architectural agreement; it does not by itself prove that the implementation exists or satisfies it.

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

## Version control and repository strategy

Keep related work together when it shares ownership and access, changes together, and is maintained or validated as a coordinated unit. Split it when a distinct service, owner, access requirement, operational lifecycle, or publication boundary makes independent work valuable. Size, language, or independent package versions alone do not require a repository split.

### Monorepo or polyrepo?

A **monorepo** keeps multiple projects or components in one repository; a **polyrepo** gives each project or service its own repository.

| Layout | Advantages | Disadvantages | Best fit |
|---|---|---|---|
| Monorepo | Related changes, shared tooling, and ownership stay together and are easy to discover. | Components share an access boundary; large checkouts and CI need deliberate management. | Projects with the same owner, access needs, and coordinated changes. |
| Polyrepo | Each project can have independent access, ownership, workflows, and lifecycle. | Cross-repository changes need coordination, and settings or tooling may be repeated. | Distinct services or genuine ownership, access, operational, or publication boundaries. |

Start with a monorepo by default: for most related work it is the easiest first choice and remains suitable for a long time. Split only when a real boundary or a demonstrated scale constraint outweighs the coordination and administration cost; use separate repositories from the start when access rights or an independent service require it.

For further reading, see [Atlassian's monorepo guide](https://www.atlassian.com/git/tutorials/monorepos), [Google's experience and trade-offs with a single repository](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/), and [GitHub's repository visibility documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).

DevHub keeps shared development resources, tooling, guidance, and setup together because one maintainer frequently changes them in coordination. The [monorepo ADR](adrs/DEVHUB-MONOREPO.md) records the project-specific rationale and trade-offs; the [architecture guide](ARCHITECTURE.md#why-devhub-is-a-monorepo) summarizes the current boundary. Distinct applications and services belong in their own repositories when those boundaries apply.

### Branches and reviews

- Use short-lived feature branches from an up-to-date `main` for a focused change. Merge once reviewed and validated, then delete the branch; avoid accumulating unrelated work or long-lived divergence.
- Keep commits and reviews focused, including directly coupled tests and documentation. Split unrelated changes so each review has a clear purpose.
- Keep `main` usable: run relevant checks before merging and fix or revert regressions promptly.
- Follow each project's documented contribution, review, and release workflow, including required checks and approvals. Shared guidance does not replace repository-specific requirements.

### GitHub Pro for personal practice

For my personal account, GitHub Pro is the lowest-cost paid plan for an individual account. The small recurring investment is worthwhile for access to private-repository protections and hands-on practice configuring and maintaining a professional setup independently: branch protection, required pull request reviews, and passing status checks before merging. See [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans#github-pro) and [current pricing](https://github.com/pricing).

This is a personal subscription choice, not repository policy or a prerequisite for contributors or every repository. GitHub Free already includes unlimited private repositories and branch protection for public repositories; Pro extends branch protection and required reviewers to private repositories owned by the personal account. Availability depends on plan, repository visibility, and ownership; organization-owned private repositories need an eligible organization plan, not the maintainer's personal Pro subscription. Check [protected-branch availability and settings](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) before choosing controls.

---

## Placing packages and components

- Keep implementation-local helpers with the application that uses them. Create a reusable package for a real public interface or consumer need.
- Treat the managed contract—not the directory count or programming language—as the release boundary. Independently versioned packages may share a repository; document the consumer contract and compatibility explicitly.
- Keep native package metadata and artifact identities. Add CI and release automation at the component's scope, including checks for affected consumers.
- Record the choice and exceptions in the owning project or package README, then track the work in the central DevHub backlog. Revisit the boundary when consumers or maintenance costs change.

For the architectural rationale and release examples, see the [release-boundary ADR](adrs/RELEASE-BOUNDARIES-BY-MANAGED-CONTRACT.md).

---

## Setting up a project or package

- Give each project and package an owning README that explains its purpose, setup, supported use, and project-specific decisions. Keep detailed commands and operational procedures with the component.
- Before publishing a component, document its consumers, native metadata, validation commands, release tags, artifact destination, and upgrade or rollback steps.
- Link to shared DevHub guidance from the project's README instead of copying it. The [getting-started guide](GETTING-STARTED.md) explains how consumers use shared resources.
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
