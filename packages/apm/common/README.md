# DevHub Common Agent Package

`devhub-common` distributes reusable engineering agents, instructions, and skills through [APM](https://microsoft.github.io/apm/). [`.apm/`](.apm/) is the authoring source; [`apm.yml`](apm.yml) declares pinned upstream skills.

The [APM overview](../README.md) owns shared setup, authoring, usage, and [reliability principles](../README.md#reliable-customization-design). This README describes the common package's roles, Orchestrator workflow, and safeguards.

## Table of Contents

- [Package contents](#package-contents)
  - [Agents](#agents)
  - [Instructions](#instructions)
  - [Skills](#skills)
  - [Pinned upstream skills](#pinned-upstream-skills)
- [Design](#design)
  - [Reliability](#reliability)
  - [Two implementation modes](#two-implementation-modes)
  - [Guidance and task evidence](#guidance-and-task-evidence)
  - [Validation and independent review](#validation-and-independent-review)
  - [Self-learning and maintenance feedback](#self-learning-and-maintenance-feedback)
  - [Completion and publishing](#completion-and-publishing)
- [Agent constraints](#agent-constraints)
- [Consumption and validation](#consumption-and-validation)

---

## Package contents

### Agents

| Agent | Responsibility |
|---|---|
| [Orchestrator](.apm/agents/orchestrator.agent.md) | Entry point; routes, coordinates, verifies, and owns delivery. |
| [Architect](.apm/agents/architect.agent.md) | Resolves material design decisions and defines boundaries. |
| [Coder](.apm/agents/coder.agent.md) | Owns implementation, tests, and focused validation. |
| [Documenter](.apm/agents/documenter.agent.md) | Maintains verified, concise documentation. |
| [Reviewer](.apm/agents/reviewer.agent.md) | Independently reviews actual changes and validation adequacy. |

### Instructions

- [Common](.apm/instructions/common.instructions.md): small universal engineering and validation core, explicitly read by every role.
- [Documentation](.apm/instructions/documentation.instructions.md): separate documentation standards for factual checks, placement, and formatting, scoped with `applyTo: "**/*.md"` rather than embedded in the common core for better reliability and targeted enforcement for documentation files.
- [AI customizations](.apm/instructions/ai-customization.instructions.md): agent, instruction, prompt, skill, and repository guidance design.
- [Ansible](.apm/instructions/ansible.instructions.md), [Dockerfile](.apm/instructions/dockerfile.instructions.md), [GitHub Actions](.apm/instructions/github-actions.instructions.md), and [Python](.apm/instructions/python.instructions.md): scoped technology and tool constraints.

The documentation file's pattern targets Markdown edits, and its description supports task-based discovery. The common core links to it, and Documenter explicitly reads it, so documentation work does not depend solely on automatic attachment. Verify loading in the intended harness; the pattern improves targeting but does not guarantee compliance.

### Skills

| Skill | Purpose |
|---|---|
| [draft-github-issue](.apm/skills/draft-github-issue/SKILL.md) | Drafts issues without publishing or implementing them. |
| [manage-skills](.apm/skills/manage-skills/SKILL.md) | Creates and maintains focused skills. |
| [setup-ai-customizations](.apm/skills/setup-ai-customizations/SKILL.md) | Sets up the shared baseline and local repository context. |
| [self-learning](.apm/skills/self-learning/SKILL.md) | Assesses task evidence and retains only reusable lessons with an owner. |
| [finalize-task](.apm/skills/finalize-task/SKILL.md) | Checks completion and separately authorized commit/push operations using ordinary Git commands. |

### Pinned upstream skills

[`apm.yml`](apm.yml) includes these [awesome-copilot](https://github.com/github/awesome-copilot) skills, pinned to `5269f7ea2d6c3a9bfda5ed878b6726cf509121fd`:

| Skill | Purpose |
|---|---|
| [git-commit](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/git-commit) | Supports requested Conventional Commits; does not authorize publishing or replace finalization checks. |
| [webapp-testing](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/webapp-testing) | Tests local web interfaces with Playwright. |

---

## Design

Select Orchestrator explicitly for the coordinated workflow. Its description aids discovery but cannot force another agent to invoke it. It remains the lead rather than another implementation specialist.

```text
Request intent
  +-- Discussion / plan / review only: respect that scope
  |
  +-- Implementation: load guidance and classify
         +-- Tiny: direct change and focused validation
         |
         +-- Standard: short plan -> Coder and validation
                                    |
                      self-learning assessment and any retained edits
                                    |
                      Reviewer checks final diff and evidence
                         +-- Findings -> correction -> validate -> review
                         +-- Clear
                                    |
                      Completion evidence check (both modes)
                                    |
                      Separately authorized commit / push, then report
```

Architect and Documenter are optional, based on material design decisions or documentation ownership. Independent, disjoint assignments can run in parallel; dependent or shared-file work cannot. Tiny work also runs the learning assessment before its completion check, but does not require an independent Reviewer.

### Reliability

This package applies the [shared reliability principles](../README.md#reliable-customization-design) through a small, explicit workflow tailored for mechanical and standard implementation modes for this common package:

- **Concise agents:** keep role identity, ownership, routing, required handoffs, and completion rules in agents. Avoid long procedural detail, duplicated standards, and rigid report templates. Specifically, the Orchestrator should focus on routing and invocation rather than embedding procedural steps (like an earlier setup of this agent used to do, which produced unnecessary complexity and reduced reliability).
- **Exactly two implementation modes in Orchestrator:** Tiny is a narrow mechanical exception; Standard covers everything else, including uncertainty. Do not add Small/Moderate/Large or more tiers that make delegation or review discretionary and more complex; keep the Orchestrator simple and predictable.
- **Procedures in skills instead of an agent like the Orchestrator:** [self-learning](.apm/skills/self-learning/SKILL.md) and [finalize-task](.apm/skills/finalize-task/SKILL.md) own repeatable steps. Orchestrator states when to invoke them rather than embedding their procedures; no separate Learning agent is needed for this (it is really part of the skill-based workflow (a procedure/workflow), not a distinct agent role).
- **Scoped standards:** retain a small universal common core and separate documentation and technology instructions. Resolve guidance and pass readable paths to specialists rather than assuming attachment or inheritance.
- **Required correction cycle:** Standard uses Coder and independent Reviewer; valid findings return to implementation, validation, and renewed review. Architect and Documenter remain optional specialists, not mandatory extra stages.
- **Lightweight evidence and publishing:** maintain brief task notes, renew affected checks/review after edits, and use ordinary Git commands. Commit and push require separate permission and verification of actual results; no custom execution framework or bundled hook is needed.
- **Evidence-backed maintenance:** retain only reusable lessons in their owning source, validate retained edits before final review, and report proposals or no durable lesson honestly.

These choices reduce ambiguity and context overhead; they do not guarantee model compliance. Missing guidance, required capabilities, checks, or review remain blockers. Installation, host discovery, and representative behavioral checks must be verified separately.

### Two implementation modes

| Mode | Admission and execution |
|---|---|
| **Tiny** | All conditions hold: mechanical and local, solution already understood, no design or behavioral decision, no significant component interaction or sensitive operation, and immediate verification. Implement directly. |
| **Standard** | Everything else, including uncertainty. Plan briefly, use Coder for implementation/validation, and Reviewer for independent review. |

A typo or known broken link can be Tiny; a small behavioral bug fix is Standard even in one file. Promote immediately when investigation or edits invalidate a Tiny condition. Missing required agents or tools blocks the Standard workflow rather than making review optional.

### Guidance and task evidence

Every role resolves and reads the common baseline, matching scoped instructions, repository entry guidance, and relevant owning documentation. The Orchestrator passes actual readable paths and task constraints to each specialist; neither context inheritance nor automatic instruction attachment is assumed.

Keep brief task notes in persistent session storage outside versioned sources. Track mode, scope, acceptance criteria, guidance read, exact check/review results, learning disposition, and separate publishing authorizations/results. Carry these notes across follow-up turns and renew affected checks and review after edits. No custom schema or fingerprint tooling is required.

Missing required guidance or material conflicts are visible blockers. Installing a package or linking an instruction does not establish loading; see [activation checks](../README.md#verify-activation).

### Validation and independent review

Coder owns implementation and its meaningful tests and focused validation. No routine Tester handoff is needed. Reviewer inspects the actual final diff, surrounding contracts, documentation, and evidence instead of trusting an implementer's summary.

Standard review is required, not selected by perceived usefulness. Concrete findings return to correction and validation, then renewed review. Retained learning edits are part of that final diff. Any subsequent edit requires renewed applicable checks and review; repeated distinct failures produce an explicit blocker.

Review can increase cost and elapsed time and is not proof of correctness. Its value is independent context and a compulsory correction opportunity, without invoking every available specialist.

### Self-learning and maintenance feedback

The [self-learning skill](.apm/skills/self-learning/SKILL.md) owns the repeatable assessment. No separate Learning agent is included: this is a procedure, not another routine role or handoff.

Assess failures, corrections, review findings, and recurring friction; inspect existing guidance before retaining a lesson. Record `updated`, `proposed`, `already-covered`, or `none`, with observation, rationale, owner, action, and validation where applicable. Missing evidence is a blocker, not a reason to invent a lesson.

Update shared source only in the owning repository and within authorized scope; keep project knowledge local and propose changes when the owner cannot be edited. Changes to enforcement, permissions, or publishing policy require explicit approval. This is controlled maintenance, not persistent model training. All retained edits join validation and final review.

### Completion and publishing

Both modes use the [finalize-task checklist](.apm/skills/finalize-task/SKILL.md) before claiming completion. Confirm acceptance criteria, guidance, exact check results, learning disposition, and applicable final review. Missing evidence, failed checks, and unresolved review findings are blockers; later edits require renewed affected checks and review.

Commit and push each require separate explicit authorization. Inspect the worktree and staged diff with ordinary Git commands, preserve unrelated changes, and use the available `git-commit` skill when committing. Stage only reviewed paths or safely separated hunks. Use Conventional Commits without `Co-authored-by:` trailers; `-m` is valid Git syntax, not unwanted message content.

Inspect the actual committed changes and full message before push, including any hook-added content. Unexpected changes or prohibited trailers require an explicit blocker, not automatic amendment. Confirm the intended branch, remote, and outgoing history; after an authorized push, verify the remote branch tip against the local commit.

The skill is a short procedure with no bundled code, tests, hooks, runtime dependency, or evidence-file setup. It guides behavior rather than automatically enforcing it. Existing repository hooks, permissions, and CI remain separate controls; do not install, replace, or bypass them as part of finalization.

Reports stay proportional: outcome, meaningful decisions, exact checks/review, learning disposition, blockers, and actual publishing state. Do not repeat suggested command blocks merely because changes remain uncommitted.

---

## Agent constraints

- Orchestrator requests `model: auto` and retains a broad wildcard tool list with explicit coordination/execution aliases for the existing protected-environment setup. This is not a narrow capability restriction; actual availability and Auto routing depend on the active harness.
- Its Local-harness agent allowlist contains Architect, Coder, Documenter, and Reviewer. Specialists declare `agents: []` where honored and never publish.
- Reviewer declares read/search/execute tools; execution is for read-only inspection or safe checks. This is a role boundary, not an operating-system sandbox.
- Field and tool support vary by harness; Copilot does not honor every Local field, including the `agents` allowlist. Verify the [current agent schema](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference) and actual tool/agent availability.
- Source validation cannot prove discovery, mandatory delegation, or compliance in a running session.

---

## Consumption and validation

Consumers identify this package as `CollinPoetoehena/DevHub/packages/apm/common`; DevHub's root [`apm.yml`](../../../apm.yml) uses `./packages/apm/common`. Follow the [repository setup](../README.md#repository-setup), [consumer guidance](../README.md#consumer-specific-guidance), and [validation procedure](../README.md#validation).

Validate sources with `apm compile --validate --local-only` from this directory. Check skill metadata and resource links separately. Refresh installations deliberately, then start a fresh session and verify discovery and representative [reliability scenarios](../README.md#reliable-customization-design) in each intended harness. Source edits do not update deployed customizations or running sessions.
