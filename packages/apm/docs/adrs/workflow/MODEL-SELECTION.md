# ADR: Keep Model Selection User-Selectable

## Context

The [current agent definitions](../../../development-core/.apm/agents/) omit model and reasoning-effort metadata. Available models, routing, and model-selection controls vary by host and user configuration. The user has a documented preference for the **Auto family / Copilot Fusion Standard tier** as a selectable starting choice where available. That preference is not part of role metadata and does not establish a runtime requirement. A fresh Reviewer context can support separate assessment, but model or provider diversity depends on what the host offers and permits.

The decision drivers are preserving this user-selectable starting preference without turning it into a role pin or runtime constraint, retaining host/session control, and obtaining a review without making unavailable model diversity a blocker. [Minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) separately owns role metadata and tool policy.

---

## Decision

Preserve **Auto / Copilot Fusion Standard** as the user's selectable starting preference where that choice is available. It is not a fixed model, a required tier, or a mandatory runtime default. Do not set or imply a model, provider, reasoning effort, or tier in shared role definitions or invocations. All roles continue to omit model metadata; the active host/session choice remains authoritative. Omission does not guarantee automatic routing, a particular inheritance rule, or any specific default, so verify behavior in the intended host.

For STANDARD work, prefer a different model or provider for the Reviewer when the host supports and permits it. If not, use the available default and continue. A different model is a preference, not a gate or proof of independence. Fresh context, evidence, and read-only review responsibilities remain important regardless of model choice.

### Default tier and routing rationale

[Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion) is a runtime router, not one fixed model. Its Standard tier balances cost, quality, and latency for everyday work and selects one model for each task. That is the default preference because ordinary work should not automatically pay the coordination cost of a more intensive execution pattern.

- **Task rather than title**: A simple plan and a complex plan can require different capabilities; the same is true for implementation. Model choice should follow task complexity and availability, not a permanent "planner uses X, implementer uses Y" mapping.
- **User-selected trade-offs**: The user can select Fusion Standard, High, or Max as appropriate and available. A harder task can justify a higher tier without changing shared role definitions.
- **Evolving availability**: Harness routing can account for its available model pool and service conditions; the package should not maintain a parallel static routing catalog.

This is a default preference, not a measured claim that Standard is always cheapest, fastest, or sufficient. Evaluate outcomes and raise the tier when the task warrants it. Runtime routing does not remove repository checks or human approval.

Verify inherited routing and tier behavior in the intended CLI and VS Code hosts during future implementation. The [Copilot configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration) describes omitted model inheritance; it does not guarantee identical routing across hosts.

---

## Consequences

### Positive

- **Selectable starting point**: The user retains the Auto/Fusion Standard preference without requiring every session or role to use it.
- **No role-level pin**: The source continues to omit model metadata, leaving selection to the active host and session.
- **Review flexibility**: Reviewer diversity is preferred when available without blocking work when it is not.

### Negative

- **Less fixed reproducibility**: Host routing and availability can evolve, so identical role text need not use the same model over time.
- **Host dependence**: Inheritance, delegation-level model selection, and option support need runtime verification; omission alone establishes no particular routing behavior.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Pin a model in custom-agent metadata](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_model-preferences): request a particular model or ordered model list per role. | Can support a verified compatibility requirement or reproducible evaluation where the named option is available. | Availability and semantics vary by host; a pin can conflict with user configuration or become stale. It would also turn a selectable starting preference into role-level configuration. | The preference belongs to the user/session, not the role definitions; all current roles omit model metadata. | A measured compatibility or evaluation need requires a scoped exception and the intended host supports it. |
| **Require a different Reviewer model**: project-defined policy using host model selection for every review. | May reduce shared-model bias for a review when different-model selection is genuinely available. | Some hosts or policies cannot select a distinct model; model difference alone does not guarantee independent reasoning. | Diversity is preferred when available and permitted, but cannot be a universal gate or assurance. | A controlled evaluation demonstrates material review benefit and the target host can satisfy the requirement consistently. |
| [Require Copilot Fusion Standard for every role and session](https://docs.github.com/en/copilot/concepts/models/copilot-fusion): convert the user-selectable starting preference into a mandatory tier. | Would make a preferred starting point consistent in an environment where it is available. | Treats a preference as a runtime requirement, overrides later host/session choices, and depends on tier availability. | The preference is a selectable starting point, not a constraint on user or host selection. | The user explicitly changes the preference into a requirement for a defined environment. |

---

## Status

Accepted: preserve Auto / Copilot Fusion Standard as the user's selectable starting preference where available, without pinning or requiring it in role metadata or runtime behavior. The host/session choice remains authoritative. Prefer Reviewer model/provider diversity when supported and permitted; otherwise use the available default without claiming guaranteed independence.

---

## Date

2026-11-13

---
# Changelog

- 2026-11-14: Interim update—removed the Copilot Fusion Standard starting preference; this was corrected below to preserve it as user-selectable. Current agent metadata specifies no model, and reviewer diversity remains a conditional preference rather than a guarantee.
- 2026-11-14: Reconciled the starting preference: Auto / Copilot Fusion Standard remains user-selectable, not a role pin or runtime requirement. Preserved the no-model metadata and conditional Reviewer preference.
