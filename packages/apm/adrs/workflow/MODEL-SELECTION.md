# ADR: Let the Harness Select Models for Each Task

## Context

The same native agent can clarify a small change or reason about a large design using the planning skill, and an implementer may edit one function or integrate a complex change. A static model assignment by job title does not capture that variation and must be maintained as available models change.

Copilot's model selection and available tiers also vary by host. The decision drivers are task-appropriate routing, user control of quality/cost/latency, and avoiding a locally maintained static model catalog. [Minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) separately owns metadata and tool-policy choices.

---

## Decision

Use the **auto family / harness-managed model selection**, with **Copilot Fusion Standard as the default user-selected tier**. Do not pin specific models or reasoning effort in workflow skills, the Implementer, or review invocations. The active native agent invokes both workflow skills with the user's selected model/router; the skills do not choose another model. The [skills-first ADR](REUSABLE-WORKFLOWS-AS-SKILLS.md) owns this procedure-versus-role distinction.

This describes selection policy, not a portable literal `model: auto` value. Omit per-agent model overrides so the selected host model/router is inherited where supported. If the user selects a fixed model, omission inherits that choice; it does not force automatic routing. Confirm the intended behavior in the running host.

### Default tier and routing rationale

[Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion) is a runtime router, not one fixed model. Its Standard tier balances cost, quality, and latency for everyday work and selects one model for each task. That is the default preference because ordinary work should not automatically pay the coordination cost of a more intensive execution pattern.

- **Task rather than title**: A simple plan and a complex plan can require different capabilities; the same is true for implementation. Model choice should follow task complexity and availability, not a permanent "planner uses X, implementer uses Y" mapping.
- **User-selected trade-offs**: The user can select Fusion Standard, High, or Max as appropriate and available. A harder task can justify a higher tier without changing shared role definitions.
- **Evolving availability**: Harness routing can account for its available model pool and service conditions; the package should not maintain a parallel static routing catalog.
- **No substitute for workflow review**: Standard's one-model execution does not imply an independent reviewer ran. Higher-tier internal critique also does not establish the separate code/security reviews or acceptance evidence required by the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md).

This is a default preference, not a measured claim that Standard is always cheapest, fastest, or sufficient. Evaluate outcomes and raise the tier when the task warrants it. Runtime routing does not remove repository checks or human approval.

Verify inherited routing and tier behavior in the intended CLI and VS Code hosts during future implementation. The [Copilot configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration) describes omitted model inheritance; it does not guarantee identical routing across hosts.

---

## Consequences

### Positive

- **Adaptive selection**: The runtime can select a model appropriate to the actual task rather than a static role label.
- **User control**: Tier changes express the desired quality/cost/latency balance without editing shared agents.
- **Less model-specific upkeep**: Role definitions need not track changing model names, availability, and static capability assignments.

### Negative

- **Less fixed reproducibility**: Routing and defaults can evolve, so identical role text need not use the same model over time.
- **Host dependence**: Inheritance, tool defaults, and option support need runtime verification; omission alone does not establish automatic routing.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Static model per agent](https://docs.github.com/en/copilot/reference/custom-agents-configuration): pin a model to each role. | Makes the requested model explicit and can suit an evaluation or capability requirement. | Role labels do not predict task complexity; model availability and names require upkeep, and pins override user routing choices. | The harness should select for the task while the user selects the tier. | A verified compatibility or evaluation requirement needs a specific model; keep that exception scoped. |
| [Always select Fusion High or Max](https://docs.github.com/en/copilot/concepts/models/copilot-fusion): use a more intensive tier for all tasks. | Prioritizes additional capability or orchestration without deciding per request. | Ordinary tasks may incur additional latency and model usage without evidence that the extra effort is needed. | Standard is the everyday balance; users can deliberately raise the tier for harder work. | Representative results show the higher tier is justified for a particular workload. |

---

## Status

Accepted: the user selected auto-family routing and Copilot Fusion Standard by default. Optional agent configuration is recorded separately; no model settings or runtime behavior are changed by this record.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Reconciled role references with the skills-first workflow. Native-agent skill invocation retains the user's model/router; the model-selection policy and original decision date are unchanged.
- 2026-11-13: Extracted model routing from the combined agent-configuration record and grouped it with workflow decisions. [Minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) owns metadata and enforcement trade-offs. The routing policy and original decision date are unchanged.
