# ADR: Layer Shared Guidance and Repository Instructions

## Context

Shared engineering standards should follow the repositories that use them, while each repository remains the authority for its architecture, commands, and local constraints. Repeating that information in every agent, skill, and chat creates conflicting copies and maintenance work. Putting everything in one always-loaded document also obscures the guidance relevant to a task.

The decision drivers are clear ownership, concise entry points, appropriately scoped rules, human-readable documentation, and compatibility with the intended Copilot harness. The [package-design ADR](../distribution-and-synchronization/PACKAGE-DESIGN.md) owns package contents and destinations; this record owns how their guidance is composed.

---

## Decision

Use a concise root `AGENTS.md` for repository orientation and local constraints, with links to owning documentation and specific guideline files. Keep common standards in repository-facing `guidelines-core` and technology-specific instruction maps with their opt-in `development-*` stack packages. Use host-supported formats such as Copilot's scoped `*.instructions.md` files; guidelines is the tool-independent term. Do not duplicate standards in every role definition.

```text
Repository guidelines-core -> common engineering standards
Optional local development stack -> scoped technology map + skills
                                      +
Repository AGENTS.md -> owning docs, configuration, local constraints
                                      +
Current request -> task goal, boundaries, acceptance criteria

Selected agent/skill -> role or procedure using that guidance
```

This is an ownership model, not a universal host precedence algorithm. [Copilot instruction discovery](https://code.visualstudio.com/docs/agent-customization/custom-instructions) depends on the harness, supported locations, settings, path matches, and task relevance.

### Ownership and specificity

- **Shared defaults**: `guidelines-core` owns durable coding, documentation, security, and testing standards without workflow agents or skills. Repositories can adopt these guidelines without the local development setup.
- **Stack maps**: Python, Go, and other opt-in development stacks own their scoped instruction maps beside their skills/resources. These maps refine common defaults and route to stack capabilities without copying the baseline or assuming a skill must run for every task.
- **Repository authority**: Root `AGENTS.md` gives the project purpose, relevant entry points, local compatibility limits, and routes to actual configuration and validation commands. Repository-specific choices stay in that repository, not the shared package.
- **Focused instructions**: Use file patterns and descriptions supported by the host to select relevant rules. Keep instructions short enough to make the important constraints prominent; link deeper explanations rather than repeat tutorials.
- **Procedures and references**: A reusable task procedure belongs in a skill when it warrants one. Agents and skills use the standing instructions; they do not maintain competing copies. A repo-specific skill stays local, while a generic skill belongs in the separate development setup.
- **Task-specific requirements**: A one-time goal or exception stays in the user request unless recurring evidence justifies durable guidance.

Within DevHub's guidance, repository configuration and local constraints take precedence over shared defaults, and specific language/tool rules refine general conventions. Higher-priority platform instructions, permissions, and organizational policies still apply. Surface unresolved conflicts instead of silently choosing a convenient interpretation.

### Root entry point and subtree exceptions

Prefer one root `AGENTS.md` that routes to existing READMEs and focused documentation. Do not maintain a duplicate repository-wide instruction document with the same content. Add nested `AGENTS.md` only when a subtree has materially different constraints that a root link or scoped instruction cannot adequately express, and the intended host supports the required discovery. Do not create a nested file for every folder.

A link is a route, not proof that its target is loaded. Make clear when the agent should read the linked document or invoke the relevant skill. Verify discovery and actual behavior separately in the intended host; instruction prose guides but cannot enforce mandatory checks. Use repository tooling, CI, permissions, and system boundaries for enforcement.

---

## Consequences

### Positive

- **Single ownership**: Shared standards, local facts, and task procedures each have one home, reducing competing versions across agents and repositories.
- **Relevant context**: Short entry points and scoped rules keep unrelated detail out of routine tasks while retaining routes to deeper knowledge.
- **Independent workflow**: Repositories retain guidance even when a contributor uses the default agent or a different development setup.

### Negative

- **Discovery dependence**: Supported scopes vary between hosts; a deployed file or link does not prove inclusion or compliance.
- **Conflict handling**: Shared defaults and local requirements can disagree, requiring explicit resolution and consistent maintenance.
- **Reference upkeep**: Routes, instruction scopes, and local commands must remain accurate; excessive indirection can hide essential constraints.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [One large `AGENTS.md`](https://agents.md/): place all shared rules, local facts, and procedures in the repository entry point. | Gives readers and agents one predictable file without additional discovery routes. | Unrelated language and task detail competes with local constraints; copied shared content drifts between repositories. | One entry point is useful, but one owner for every kind of detail is not. Scoped rules and linked procedures preserve relevance and ownership. | A very small repository has little guidance and no substantial reusable procedures. |
| [Rules embedded in every custom agent](https://code.visualstudio.com/docs/agent-customization/custom-agents): each role carries its own engineering standards. | A selected role can contain all of its guidance without following links. | Shared standards are duplicated, role updates can diverge, and default-agent work may miss the same rules. | Standards must apply independently of which workflow or role is selected. | A genuinely role-specific constraint belongs in that role; this does not justify copying the shared baseline. |
| [Nested `AGENTS.md` everywhere](https://agents.md/): distribute orientation and rules through every subtree. | Can place specialized constraints close to affected code. | Adds overlapping files and discovery assumptions even where subtree behavior is unchanged. | The root entry point plus scoped instructions covers ordinary variation with fewer competing sources. | A materially different subtree needs local constraints that links or scoped rules cannot express adequately. |

---

## Status

Accepted: the user selected layered guidance with `AGENTS.md`, shared repository guidelines, and stack-owned instruction maps. The `guidelines-core` and `development-*` source packages implement that ownership; installation and discovery remain separate and require host-specific verification.

---

## Date

2026-11-13
