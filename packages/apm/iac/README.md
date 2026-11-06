# DevHub Infrastructure as Code Package

`devhub-iac` is an opt-in APM package for repositories with infrastructure as code. It adds Ansible, Terraform, and Bicep instructions and the `ansible`, `terraform`, and `bicep` skills with focused references on top of the [common package](../common/README.md), whose instructions always apply.

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content). The Ansible instructions include the DevHub Ansible rules, and every instruction forbids applying changes to live infrastructure merely to validate an edit.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`ansible.instructions.md`](.apm/instructions/ansible.instructions.md) | Instruction (`ansible/`, playbooks, roles, inventories, variables, `ansible.cfg`) | DevHub Ansible rules and validation commands; points to the skill |
| [`terraform.instructions.md`](.apm/instructions/terraform.instructions.md) | Instruction (`*.tf`, `*.tfvars`, `*.tftest.hcl`, lock file) | Version pinning, state, secrets, and plan rules and validation commands; points to the skill |
| [`bicep.instructions.md`](.apm/instructions/bicep.instructions.md) | Instruction (`*.bicep`, `*.bicepparam`) | Naming, parameter, reference, and security rules and validation commands; points to the skill |
| [`ansible`](.apm/skills/ansible/SKILL.md) | Skill | Index and gotchas for Ansible work |
| [`ansible/references/patterns.md`](.apm/skills/ansible/references/patterns.md) | Skill reference | Naming, idempotency, FQCN, privileges, secret management, style, and linting |
| [`terraform`](.apm/skills/terraform/SKILL.md) | Skill | Index and gotchas for Terraform work |
| [`terraform/references/patterns.md`](.apm/skills/terraform/references/patterns.md) | Skill reference | Security, modularity, maintainability, style, documentation, and testing |
| [`bicep`](.apm/skills/bicep/SKILL.md) | Skill | Index and gotchas for Bicep work |
| [`bicep/references/patterns.md`](.apm/skills/bicep/references/patterns.md) | Skill reference | Naming, structure, parameters, variables, resource references, names, child resources, and security |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `ansible/references/patterns.md` | [awesome-copilot `ansible.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/ansible.instructions.md) | Adapted | `797337f` (2026-11-06) | Moved the source list from an HTML comment into the references |
| `terraform/references/patterns.md` | [awesome-copilot `terraform.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/terraform.instructions.md) | Adapted | `797337f` (2026-11-06) | Added a note that the AWS examples apply to the equivalent controls of other providers |
| `bicep/references/patterns.md` | [awesome-copilot `bicep-code-best-practices.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/bicep-code-best-practices.instructions.md) | Adapted | `797337f` (2026-11-06) | Replaced the comment guidance with the common comment policy; normalized list markers |
| Ansible instruction | DevHub Ansible instructions previously in `devhub-common` | Authored | Not applicable | Moved, with lint, naming, privilege, and validation rules added and `ansible/` directories matched |
| Terraform and Bicep instructions, `SKILL.md` indexes | DevHub | Authored | Not applicable | None |

---

## Consumption

The package depends on the [common package](../common/README.md), so installing it also installs `devhub-common`. List both in the consumer's `apm.yml` to keep the baseline explicit, then run `apm install`:

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/common
    - CollinPoetoehena/DevHub/packages/apm/iac
```

State the inventories, state backends, and environments that agents may use, and the validation commands, in the repository's `AGENTS.md`. Changes are recorded in the [changelog](CHANGELOG.md).
