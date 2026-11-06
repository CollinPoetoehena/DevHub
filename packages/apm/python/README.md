# DevHub Python Package

`devhub-python` is an opt-in APM package with Python guidance for repositories that use Python. It extends the [common package](../common/README.md), which stays the engineering baseline.

> Placeholder: the files below define the structure; their content is still to be adapted. Do not depend on this package yet.

The common package still contains a `python.instructions.md`. Move its rules here when this package is filled in, because both files deploy to `.github/instructions/python.instructions.md` and would collide.

Follow the [language and framework guidance](../README.md#language-and-framework-guidance) and [package design](../README.md#package-design) in the APM guide.

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`python.instructions.md`](.apm/instructions/python.instructions.md) | Instruction (`**/*.py,**/*.pyi,**/pyproject.toml`) | Toolchain, mandatory rules, validation commands; points to the skills |
| [`python`](.apm/skills/python/SKILL.md) | Skill | Index and gotchas; opens one reference per task |
| [`references/patterns.md`](.apm/skills/python/references/patterns.md) | Skill reference | Idioms, types, error handling, and structure |
| [`references/testing.md`](.apm/skills/python/references/testing.md) | Skill reference | Test layout, fixtures, mocking, and coverage |
| [`references/tooling.md`](.apm/skills/python/references/tooling.md) | Skill reference | Toolchain, formatting, linting, type checking, and dependency management |
| [`fastapi`](.apm/skills/fastapi/SKILL.md) | Skill | FastAPI patterns and testing |

---

## Reuse registry

Reused parts and their local changes, following the [reuse approach](../README.md#reuse-registry).

| Part | Source | Type | Local changes |
|---|---|---|---|
| `python` skill `references/patterns.md` | [ECC `python-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) | TODO | TODO |
| `python` skill `references/testing.md` | [ECC `python-testing`](https://github.com/affaan-m/ECC/blob/main/skills/python-testing/SKILL.md) | TODO | TODO |

---

## Consumption

Add the package next to the common package in the consumer's `apm.yml`:

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/common
    - CollinPoetoehena/DevHub/packages/apm/python
```
