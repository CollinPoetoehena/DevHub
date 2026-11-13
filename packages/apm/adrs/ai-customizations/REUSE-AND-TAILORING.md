# ADR: Reuse Native Capabilities and Selectively Tailor Customizations

## Context

Creating or adopting a customization introduces maintenance, discovery metadata, and upstream assumptions. Default agents, harness features, and repository tools already supply much of the required capability; maintained examples can supply useful additions without making every convention local work.

The [creation ADR](AI-CUSTOMIZATION-CREATION.md) sets the value threshold for creating anything and how much detail to use. This record operationalizes that threshold: inspect what is already available, choose the smallest sufficient source or customization, and balance its benefit against adoption and maintenance cost rather than maximizing owned content.

---

## Decision

Reuse native product capabilities, repository assets, and suitable maintained components before authoring local additions. Adopt only the useful parts, tailor genuine local differences, and stop when representative tasks meet the standards with normal review.

### Two stages of restraint: 90/10 and 80/20

These ratios are design heuristics, not measured performance, quotas, or targets for file counts:

1. **Before customizing, aim for 90/10 native capability versus owned additions**: let the product, harness, existing tooling/tests, and clear requests do most of the work. Own only the missing context or capability. An 80/20 balance can fit unusual constraints, but do not manufacture a custom portion when nothing is missing.
2. **Once customization is justified, aim for 80/20 reuse versus tailoring**: reuse most of an appropriate component and own only the local differences. Prefer 90/10 when the source fits even better. Installing nothing is better than installing irrelevant content.

Reuse does not mean adopting an entire collection.

### Establish the gap before adding a layer

Check the capabilities available in the actual host and harness, plus existing repository tools and guidance, before selecting a customization. Defaults differ across hosts, so verify what the intended environment provides rather than assuming a feature is supported—or rebuilding it because it is unfamiliar. A named example or available package is not itself evidence that the project needs it.

Start with the least additional machinery that closes the observed gap: use a default agent and existing tools when sufficient; use instructions for durable local rules; use a skill for a repeatable procedure; and use a custom agent only when a distinct role contract or boundary cannot be met reliably by the default agent with relevant guidance. A custom orchestrator or tool wrapper needs an even clearer case: it should deliver a necessary capability or control that the harness does not already provide, not mirror its agent loop or delegation.

Compare the recurring benefit—such as less repeated prompting, fewer observed mistakes, or a required approval boundary—with the full ownership cost: keeping content discoverable and accurate, validating host compatibility, resolving overlap, and reviewing updates. If the gap is not concrete or the added layer does not improve the outcome enough to justify that cost, keep the native setup. This is the source-selection counterpart to the native-first value and detail principles in the [creation ADR](AI-CUSTOMIZATION-CREATION.md).

| Observed fit | Response |
|---|---|
| Native product or existing repository tool solves it | Use it without another wrapper |
| A reusable component fits unchanged | Adopt a reviewed, pinned dependency |
| Only a local difference is missing | Add a small scoped supplement |
| Useful content needs trimming or integration | Adapt it, retain attribution, and record meaningful differences |
| No reusable source fits and recurring benefit is clear | Create the smallest local component |
| The need is unique to one repository | Keep it in that repository |
| The problem is hypothetical or a one-off prompt suffices | Do not create a durable customization |

### Source selection and stopping

Start with [Awesome Copilot](https://github.com/github/awesome-copilot) for Copilot-oriented components and authoring examples, [Anthropic Skills](https://github.com/anthropics/skills) and [Matt Pocock's skills](https://github.com/mattpocock/skills/tree/main) for skill examples, and [ECC](https://github.com/affaan-m/ECC) for ideas needing harness-specific review. These are references, not installation checklists or proof of safety. [Anthropic's simple-pattern guidance](https://www.anthropic.com/research/building-effective-agents) provides background, not a prescription to replace Copilot's harness.

Review scope, license, provenance, permissions, tools, host assumptions, and overlap. Installing an entire collection adds irrelevant discovery metadata, competing workflows, update exposure, and maintenance. Pinning improves reviewability but does not establish correctness or compliance.

Add guidance when a real project adopts a tool, a recurring convention is missing, or an agent demonstrably gets something wrong. Do not anticipate every framework or perfect upstream content for its own sake. Once normal review establishes adequate results, spend time building software instead of continually tuning the wrapper. Retired approaches belong in the [archive](../../../../archive/AI-CUSTOMIZATIONS.md), not active policy.

---

## Consequences

### Positive

- **Less owned machinery**: Native capability and selective reuse avoid rebuilding existing tooling and procedures.
- **Purposeful adoption**: Small supplements and reviewed adaptations address local gaps without importing an entire workflow ecosystem.
- **Sustainable stopping point**: Usability, maintenance, and time constrain customization work instead of an unlimited catalog of possible improvements.

### Negative

- **Judgment required**: Neither percentage gives an automatic test for fit; concrete recurring needs and representative results still matter.
- **Upstream maintenance**: Reused content requires licensing, compatibility checks, update review, and adaptation as hosts and models evolve.
- **Local differences**: Adaptations and supplements need attribution and clear ownership to avoid drifting from their sources.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Install an entire collection](https://github.com/github/awesome-copilot): adopt every available agent, instruction, and skill instead of selecting useful parts. | Gives quick access to a broad set of examples and capabilities. | Unused content adds discovery noise, overlapping instructions, licensing review, and upstream behavior changes. | Availability is not evidence of fit; selective reuse better matches the intended thin setup. | A reviewed coherent bundle genuinely fits the full workload and its maintenance cost is justified. |
| [Author everything locally](https://agentskills.io/): write all procedures and role guidance from scratch. | Offers complete editorial control and avoids adapting upstream assumptions. | Reimplements existing capabilities and makes the maintainer responsible for every convention and update. | Native capabilities and suitable references should be reused before bespoke content is justified. | A demonstrated local requirement has no suitable reusable source. |

---

## Status

Accepted: the user selected native-capability and reuse/tailoring heuristics with selective adoption. This is the existing policy extracted into its own record, not implementation.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Extracted sourcing, reuse ratios, and stopping criteria from the [creation record](AI-CUSTOMIZATION-CREATION.md) so they can be maintained independently. The original policy and decision date are preserved.
- 2026-11-13: Expanded the native-capability gap check, value-versus-maintenance test, and limits for bespoke agents or orchestration; cross-linked the [creation ADR](AI-CUSTOMIZATION-CREATION.md)'s value threshold.
