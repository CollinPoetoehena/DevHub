# ADR: Keep Shared Agent Configuration Minimal

## Context

Supported agent fields, tool names, and defaults vary by host. Fully specifying shared profiles can couple role definitions to one harness and hide controls that another ignores. The selected roles need explicit responsibilities without recreating the harness or mistaking prose for enforceable permissions.

The decision drivers are a small compatibility surface, clear role contracts, and real enforcement of mandatory boundaries. [Model selection](MODEL-SELECTION.md) separately owns auto-family routing and the default tier.

---

## Decision

Keep agent metadata to required discovery information and a useful name. By default, omit explicit `tools` lists, model/effort overrides, target-specific handoffs, subagent catalogs, and other optional host-specific settings. Avoid binding shared definitions to one host's tool names or unsupported attributes.

In the Markdown definition, state what the role can and cannot do: responsibilities, required inputs, outputs, delegation boundaries, approval/escalation conditions, and when to stop. Shared rules stay in instructions; reusable procedures stay in skills. The [thin-customization ADR](../ai-customizations/AI-CUSTOMIZATION-CREATION.md) owns that detail boundary.

Omission delegates configuration to the host; it is not a restriction. The [Copilot configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration) states that omitted tools default to all tools and an omitted model inherits the default. Supported fields and their handling differ by [harness](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference).

Consequently, "the planning skill must not implement" and "Implementer must not delegate" are procedure and role contracts, not technical permission boundaries. The [skills-first ADR](REUSABLE-WORKFLOWS-AS-SKILLS.md) retains the native agent for coordination and only the specialized Implementer as a custom role. Enforce necessary restrictions with supported host/session controls, CI, and system permissions. If those are insufficient, a narrowly justified host-specific configuration exception is required before relying on that boundary. Portability does not justify weakening mandatory controls.

Verify inherited defaults, available tools, role compliance, and reviewer/delegation capabilities in the intended CLI and VS Code hosts during implementation. Minimal metadata improves compatibility; it does not guarantee identical behavior everywhere.

---

## Consequences

### Positive

- **Smaller compatibility surface**: Fewer optional fields and tool aliases reduce configuration tied to a particular host.
- **Focused definitions**: Roles describe their responsibilities rather than duplicate shared rules or a host's routing machinery.

### Negative

- **Host dependence**: Defaults and option support need runtime verification; omission is not proof of the intended capabilities.
- **Enforcement outside prose**: Broad default tools mean role prohibitions need real host controls where mandatory, potentially requiring explicit exceptions.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Fully specified host-specific profiles](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): enumerate tools, models, handoffs, and optional settings in shared agents. | Can make supported capabilities and restrictions explicit in one tested host. | Tool names and fields differ across harnesses, increasing maintenance and potentially hiding ignored controls. | The shared baseline uses minimal metadata and role contracts, with actual enforcement supplied by the host. | A mandatory permission or capability boundary cannot be achieved through the chosen host/session controls; configure and test a narrow exception. |

---

## Status

Accepted: the user selected omitted optional agent configuration in favor of role definitions and host controls. This is an existing policy extracted into a focused record, not an agent configuration change.

---

## Date

2026-11-13
