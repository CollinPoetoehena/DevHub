# Repository Fleet Architecture Decision Records

These records capture significant design decisions for [repository fleet management](../README.md). The README remains the operating guide; each ADR owns its decision rationale, alternatives, and trade-offs.

Follow the [central ADR guidelines](../../../docs/GUIDELINES.md#architecture-decision-records-adrs) for scope, placement, and referencing decisions.

| ADR | Decision |
|---|---|
| [Tool boundaries](TOOL-BOUNDARIES.md) | Separate Terraform-managed repository settings from Python-managed shared content. |
| [Shared inventory](SHARED-INVENTORY.md) | Use one JSON inventory consumed and validated by both tools. |
| [Central fleet sync](CENTRAL-FLEET-SYNC.md) | Use one protected DevHub workflow to preflight the fleet, apply an approved settings plan, and open content pull requests. |