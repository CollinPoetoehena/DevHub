# ADR: Use One JSON Inventory for Repository Fleet Tools

## Context

Terraform and Python `repo-fleet` both need repository names and attributes to manage the same fleet. The current [`repositories.auto.tfvars.json`](../terraform/repositories.auto.tfvars.json) is loaded automatically by Terraform and read directly by `repo-fleet`. Terraform validates its typed input; Python parses the JSON, rejects unknown and duplicate keys, and validates repository fields before operations.

The inventory must have one authoritative value for settings and content planning, be directly consumable by both tools, and remain reviewable as a normal tracked file. It must not depend on Terraform state, credentials, or local repository checkouts to discover the fleet.

---

## Decision

Keep a single JSON inventory at `tools/repo/terraform/repositories.auto.tfvars.json`. Terraform consumes it as an automatically loaded variable file; `repo-fleet` reads the same document using Python's JSON library and validates the inventory contract itself. Keep repository membership explicit and do not infer it from an account listing or local checkouts.

This decision selects the source format and ownership boundary. Both consumers remain responsible for validating the fields they use; changes to the contract must keep those validations aligned.

---

## Consequences

### Positive

- **One source of truth**: Terraform settings and Python content operations plan against the same explicit repository set and attributes.
- **Native consumption**: Terraform automatically loads `.auto.tfvars.json`, and Python reads JSON without an HCL parser or Terraform process.
- **Reviewable membership**: Repository additions, visibility, profile, and archive changes are visible in one versioned input file before either tool acts.
- **Independent validation**: Each consumer can reject invalid values before using them, rather than treating a syntactically valid file as an accepted contract.

### Negative

- **Duplicated contract checks**: Terraform and Python validation must evolve together to avoid accepting different inventory values.
- **JSON limits**: JSON has no comments, so explanations for unusual repository entries belong in nearby documentation or commit history.
- **Schema coordination**: Optional fields and defaults must be supported consistently by both consumers.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [JSON variable definitions](https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files): use one `.auto.tfvars.json` file directly in Terraform and parse the same JSON with [Python's `json` module](https://docs.python.org/3/library/json.html). | Both tools consume the same ordinary data format without a custom parser or generated copy. Terraform's automatic filename convention and Python's standard library match the current implementation. | No comments; each tool must validate the shared schema, and both validations can drift if contract changes are not reviewed together. | Selected because direct consumption keeps the inventory explicit and avoids a new transformation or runtime dependency. | Reconsider if the schema becomes difficult to validate consistently or the lack of comments materially impairs safe maintenance. |
| **Separate Terraform and Python inventories**, a project-defined approach using a Terraform variable file and a Python JSON or YAML configuration; see the current [inventory contract](../README.md#inventory). | Each tool could express only the fields it needs and evolve its format independently. | Repository membership and attributes would be repeated, allowing one tool to plan a different fleet or settings than the other. Synchronization would become an operational requirement. | Duplicated declarations undermine the single fleet boundary and would add drift checks to every change. | Reconsider only if the tools are split into independently owned fleets with no shared repository membership or lifecycle. |
| [Terraform HCL input](https://developer.hashicorp.com/terraform/language/syntax): keep the inventory only in HCL and have Python obtain it through Terraform output or by parsing configuration. | HCL supports Terraform-native expressions and comments, and it could remain the only authored settings file. | Python would need to invoke Terraform or understand HCL/configuration semantics, coupling file planning to Terraform availability, execution, or internals. | The content tool needs simple inventory data, not Terraform expressions; JSON is directly readable and avoids adding that coupling. | Reconsider if inventory values genuinely require Terraform expressions and a stable, supported data-export interface becomes part of the tool contract. |

---

## Status

Proposed. The current implementation uses one JSON inventory; separate approval of this ADR has not been recorded.

---

## Date

2026-11-13
