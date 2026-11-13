# DevHub Rust Package

`devhub-development-rust` is an opt-in APM package for local development environments that use Rust. It adds Rust guidance, a skill, and focused references and depends on [`development-core`](../development-core/README.md). Adopt shared repository standards separately through [`guidelines-core`](../guidelines-core/README.md).

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content).

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`rust.instructions.md`](.apm/instructions/rust.instructions.md) | Instruction (`**/*.rs`, `**/Cargo.toml`, `**/Cargo.lock`, `**/rust-toolchain.toml`) | Toolchain defaults, mandatory rules, and validation commands; points to the skill |
| [`rust`](.apm/skills/rust/SKILL.md) | Skill | Index and gotchas for Rust work |
| [`rust/references/patterns.md`](.apm/skills/rust/references/patterns.md) | Skill reference | Ownership, error handling, enums, traits and generics, iterators, concurrency, unsafe code, and crate structure |
| [`rust/references/conventions.md`](.apm/skills/rust/references/conventions.md) | Skill reference | Naming, API design guidelines, patterns to follow and avoid, and the quality checklist |
| [`rust/references/testing.md`](.apm/skills/rust/references/testing.md) | Skill reference | Unit, integration, async, property-based, mock, and doc tests, benchmarks, and coverage |
| [`rust/references/tooling.md`](.apm/skills/rust/references/tooling.md) | Skill reference | Commands, toolchain and lint configuration, and dependency audits |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `rust/references/patterns.md` | [ECC `rust-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/rust-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Moved the tooling section to `tooling.md` |
| `rust/references/conventions.md` | [awesome-copilot `rust.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/rust.instructions.md) | Adapted | `797337f` (2026-11-06) | None |
| `rust/references/testing.md` | [ECC `rust-testing`](https://github.com/affaan-m/ECC/blob/main/skills/rust-testing/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `rust/references/tooling.md` | Tooling section of [ECC `rust-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/rust-patterns/SKILL.md) | Authored | `b38be6a` (2026-11-06) | Expanded with DevHub defaults, toolchain and lint configuration, and coverage |
| Instruction and `SKILL.md` index | DevHub | Authored | Not applicable | None |

---

## Consumption

The package depends on [`development-core`](../development-core/README.md) for shared local capabilities. Add the stack package to the consumer's `apm.yml`, then install and verify it using the host-specific procedure described in the [APM guide](../README.md#repository-setup):

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/development-rust
```

State the Rust toolchain and validation commands in the repository's `AGENTS.md`. Changes are recorded in the [changelog](CHANGELOG.md).
