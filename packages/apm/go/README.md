# DevHub Go Package

`devhub-go` is an opt-in APM package with Go guidance for repositories that use Go. It extends the [common package](../common/README.md), which stays the engineering baseline.

> Placeholder: the files below define the structure; their content is still to be adapted. Do not depend on this package yet.

Follow the [language and framework guidance](../README.md#language-and-framework-guidance) and [package design](../README.md#package-design) in the APM guide.

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`go.instructions.md`](.apm/instructions/go.instructions.md) | Instruction (`**/*.go,**/go.mod,**/go.sum`) | Toolchain, mandatory rules, validation commands; points to the skills |
| [`go`](.apm/skills/go/SKILL.md) | Skill | Index and gotchas; opens one reference per task |
| [`references/patterns.md`](.apm/skills/go/references/patterns.md) | Skill reference | Idioms, types, error handling, and structure |
| [`references/testing.md`](.apm/skills/go/references/testing.md) | Skill reference | Test layout, fixtures, mocking, and coverage |
| [`references/tooling.md`](.apm/skills/go/references/tooling.md) | Skill reference | Toolchain, formatting, linting, type checking, and dependency management |

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
    - CollinPoetoehena/DevHub/packages/apm/go
```
