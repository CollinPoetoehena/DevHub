# DevHub Java Package

`devhub-java` is an opt-in APM package with Java guidance for repositories that use Java. It extends the [common package](../common/README.md), which stays the engineering baseline.

> Placeholder: the files below define the structure; their content is still to be adapted. Do not depend on this package yet.

Follow the [language and framework guidance](../README.md#language-and-framework-guidance) and [package design](../README.md#package-design) in the APM guide.

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`java.instructions.md`](.apm/instructions/java.instructions.md) | Instruction (`**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts`) | Toolchain, mandatory rules, validation commands; points to the skills |
| [`java`](.apm/skills/java/SKILL.md) | Skill | Index and gotchas; opens one reference per task |
| [`references/patterns.md`](.apm/skills/java/references/patterns.md) | Skill reference | Idioms, types, error handling, and structure |
| [`references/testing.md`](.apm/skills/java/references/testing.md) | Skill reference | Test layout, fixtures, mocking, and coverage |
| [`references/tooling.md`](.apm/skills/java/references/tooling.md) | Skill reference | Toolchain, formatting, linting, type checking, and dependency management |
| [`spring-boot`](.apm/skills/spring-boot/SKILL.md) | Skill | Spring Boot patterns and testing |

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
    - CollinPoetoehena/DevHub/packages/apm/java
```
