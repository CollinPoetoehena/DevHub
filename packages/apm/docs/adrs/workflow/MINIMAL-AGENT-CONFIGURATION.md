# ADR: Match Agent Metadata to Actual Host Contracts

## Context

Supported agent fields, tool names, and defaults vary by host. The current definitions intentionally declare broad `tools: ['*']` access, and coordinators configure which agents may be delegated. Omitting tool metadata is not equivalent to restricting capabilities: for example, Copilot's documented default may grant all tools. The decision is to describe and review actual metadata accurately without mistaking prose for enforced permissions.

The decision drivers are clear role contracts, honest host-specific configuration, and real enforcement of mandatory boundaries. [Model selection](MODEL-SELECTION.md) separately owns the no-fixed-model policy.

---

## Decision

Use only metadata required for the selected role and host behavior. The current package sets `tools: ['*']` on all four agents; Planner permits `agents: ['*']`, while the Implementation Orchestrator declares `agents: ['*', 'Implementer', 'Reviewer']`. Implementer and Reviewer specify `user-invocable: false`; Planner and Orchestrator omit that field and are user-invocable by default where supported. No role pins a model or reasoning effort. These values describe the current package source, not a portable promise that every host interprets them identically.

In each Markdown definition, state the role's responsibilities, required inputs, outputs, delegation boundaries, escalation conditions, and when to stop. Shared rules stay in instructions; reusable procedures stay in focused skills. The [workflow-agent ADR](WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) owns the role structure; the [thin-customization ADR](../ai-customizations/AI-CUSTOMIZATION-CREATION.md) owns the detail boundary.

Metadata is not a substitute for host permissions. The [VS Code custom-agent reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference) documents fields such as `tools`, `agents`, and `user-invocable`; semantics and support vary by harness. In particular, its current compatibility table says `agents` is not supported by the Copilot harness, so the Orchestrator's declared worker list does not prove Copilot worker visibility. Do not infer access restrictions, permission mode, approval settings, or model identity from role prose or unsupported metadata. Apply required controls through host policies, permissions, sandboxing, and CI, and verify them in the intended environment.

Consequently, "Planner must not implement," "Implementer must not delegate," and "Reviewer must not edit" are role contracts unless enforced by tools and host controls. Current `tools: ['*']` metadata is broad; it must not be described as least-privilege or as a security boundary. Do not narrow or change source-agent metadata as part of this ADR documentation update.

Verify agent visibility, delegation availability, tools, review behavior, and permission handling in the intended host. Source metadata does not establish that agents are installed, discoverable, or behaving as specified.

---

## Consequences

### Positive

- **Accurate contracts**: Documentation distinguishes broad configured tool access from role boundaries and host enforcement.
- **Explicit delegation**: Coordinator metadata names available worker roles where configured, while selection and invocation remain host-dependent.

### Negative

- **Broad configured tools**: `tools: ['*']` does not enforce read-only or no-delegation roles; the host must provide any mandatory restrictions.
- **Host dependence**: Metadata support, default visibility, and delegation semantics need runtime verification; package declarations alone do not prove availability.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Narrow per-role tools and agents](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): list only each role's required tools and delegation targets. | Could reduce available actions in a host that enforces these fields, and make intended role capabilities inspectable. | Support and enforcement differ by harness; a file-level declaration is not a substitute for verified permission boundaries. | The current package uses wildcard tools and delegation; changing implementation metadata is outside this documentation update, and any restriction requires tested host support. | A specific host and policy require narrower capabilities and the restriction is verified end to end. |
| **Prose-only role limits**: describe no-edit or no-delegation constraints without host controls, using [custom-agent instructions](https://code.visualstudio.com/docs/agent-customization/custom-agents). | Portable role guidance is easy to read and maintain. | Instructions guide the model but do not technically prevent tool use; broad `'*'` access makes this limitation especially material. | Keep prose as a behavioral contract, not as the enforcement mechanism. | Never as a mandatory security or permission boundary; use controls outside prose. |

---

## Status

Accepted: describe current broad tool and delegation metadata accurately; use role prose for behavioral contracts and host controls for enforced boundaries. No agent source metadata is changed by this documentation decision.

---

## Date

2026-11-13

---
# Changelog

- 2026-11-14: Corrected the prior omission-by-default description to match the four current agent definitions, including wildcard tools and coordinator delegation metadata; clarified host enforcement and visibility limits.
