# DevHub Python Package

`devhub-development-python` is an opt-in APM package for local development environments that use Python. It adds Python, FastAPI, and Django instruction maps, skills, and references and depends on [`development-core`](../development-core/README.md). Adopt shared repository standards separately through [`guidelines-core`](../guidelines-core/README.md).

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content).

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`python.instructions.md`](.apm/instructions/python.instructions.md) | Instruction (`**/*.py`, `**/*.pyi`, `**/pyproject.toml`) | Toolchain defaults, mandatory rules, and validation commands; points to the skills |
| [`python`](.apm/skills/python/SKILL.md) | Skill | Index and gotchas for Python work |
| [`python/references/patterns.md`](.apm/skills/python/references/patterns.md) | Skill reference | Idioms, type hints, error handling, data classes, decorators, concurrency, and package layout |
| [`python/references/testing.md`](.apm/skills/python/references/testing.md) | Skill reference | pytest structure, fixtures, parametrization, markers, mocking, and async tests |
| [`python/references/tooling.md`](.apm/skills/python/references/tooling.md) | Skill reference | uv, ruff, mypy, pytest configuration, and pip-audit |
| [`fastapi`](.apm/skills/fastapi/SKILL.md) | Skill | Index and gotchas for FastAPI work |
| [`fastapi/references/patterns.md`](.apm/skills/fastapi/references/patterns.md) | Skill reference | Project layout, lifespan, settings, schemas, dependency injection, routers, services, and testing |
| [`django`](.apm/skills/django/SKILL.md) | Skill | Index and gotchas for Django work |
| [`django/references/patterns.md`](.apm/skills/django/references/patterns.md) | Skill reference | Layout, settings, models, QuerySets, REST framework, services, caching, signals, and performance |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `python/references/patterns.md` | [ECC `python-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Moved the tooling section to `tooling.md`; replaced the isort hint with a pointer to `tooling.md` |
| `python/references/testing.md` | [ECC `python-testing`](https://github.com/affaan-m/ECC/blob/main/skills/python-testing/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `python/references/tooling.md` | Tooling section of [ECC `python-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) | Authored | `b38be6a` (2026-11-06) | Rewritten for DevHub defaults: uv, ruff instead of black and isort, mypy, pytest, and pip-audit |
| `fastapi/references/patterns.md` | [ECC `fastapi-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/fastapi-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `django/references/patterns.md` | [ECC `django-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/django-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| Instruction and `SKILL.md` indexes | DevHub | Authored | Not applicable | Includes the Python rules previously in `devhub-common` |

---

## Consumption

The package depends on [`development-core`](../development-core/README.md) for shared local capabilities. Add the stack package to the consumer's `apm.yml`, then install and verify it using the host-specific procedure described in the [APM guide](../README.md#repository-setup):

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/development-python
```

State the Python version, framework, and validation commands in the repository's `AGENTS.md` so agents know which skills apply. Changes are recorded in the [changelog](CHANGELOG.md).
