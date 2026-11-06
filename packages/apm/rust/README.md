# DevHub Rust Package

`devhub-rust` is an opt-in APM package with Rust guidance for repositories that use Rust. It extends the [common package](../common/README.md), which stays the engineering baseline.

> Placeholder: the files below define the structure; their content is still to be adapted. Do not depend on this package yet.

Follow the [language and framework guidance](../README.md#language-and-framework-guidance) and [package design](../README.md#package-design) in the APM guide.

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`rust.instructions.md`](.apm/instructions/rust.instructions.md) | Instruction (`**/*.rs,**/Cargo.toml`) | Toolchain, mandatory rules, validation commands; points to the skills |
| [`rust`](.apm/skills/rust/SKILL.md) | Skill | Index and gotchas; opens one reference per task |
| [`references/patterns.md`](.apm/skills/rust/references/patterns.md) | Skill reference | Idioms, types, error handling, and structure |
| [`references/testing.md`](.apm/skills/rust/references/testing.md) | Skill reference | Test layout, fixtures, mocking, and coverage |
| [`references/tooling.md`](.apm/skills/rust/references/tooling.md) | Skill reference | Toolchain, formatting, linting, type checking, and dependency management |

---

## Reuse registry

Reused parts and their local changes, following the [reuse approach](../README.md#reuse-registry).

| Part | Source | Type | Local changes |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

---

## Consumption

Add the package next to the common package in the consumer's `apm.yml`:

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/common
    - CollinPoetoehena/DevHub/packages/apm/rust
```
