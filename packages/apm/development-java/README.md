# DevHub Java Package

`devhub-development-java` is an opt-in APM package for local development environments working on the JVM. It adds Java, Kotlin, and Spring Boot instruction maps, skills, and references and depends on [`development-core`](../development-core/README.md). Adopt shared repository standards separately through [`guidelines-core`](../guidelines-core/README.md).

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content). Kotlin shares this package because it shares the JVM, the build tools, and Spring Boot.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`java.instructions.md`](.apm/instructions/java.instructions.md) | Instruction (`**/*.java`, Maven and Gradle build files) | Toolchain defaults, mandatory rules, and validation commands; points to the skills |
| [`kotlin.instructions.md`](.apm/instructions/kotlin.instructions.md) | Instruction (`**/*.kt`, `**/*.kts`) | Toolchain defaults, mandatory rules, and validation commands; points to the skills |
| [`java`](.apm/skills/java/SKILL.md) | Skill | Index and gotchas for Java work |
| [`java/references/patterns.md`](.apm/skills/java/references/patterns.md) | Skill reference | Naming, immutability, `Optional`, streams, injection, exceptions, generics, structure, logging, and configuration |
| [`java/references/testing.md`](.apm/skills/java/references/testing.md) | Skill reference | JUnit 5 assertions |
| [`java/references/tooling.md`](.apm/skills/java/references/tooling.md) | Skill reference | Wrapper commands, toolchains, formatting, coverage, and dependency audits |
| [`kotlin`](.apm/skills/kotlin/SKILL.md) | Skill | Index and gotchas for Kotlin work |
| [`kotlin/references/patterns.md`](.apm/skills/kotlin/references/patterns.md) | Skill reference | Null safety, immutability, sealed types, scope functions, delegation, DSLs, and Gradle Kotlin DSL |
| [`kotlin/references/coroutines.md`](.apm/skills/kotlin/references/coroutines.md) | Skill reference | Structured concurrency, Flow, dispatchers, and cancellation |
| [`kotlin/references/ktor.md`](.apm/skills/kotlin/references/ktor.md) | Skill reference | Ktor routing, plugins, authentication, Koin, validation, and testing |
| [`kotlin/references/testing.md`](.apm/skills/kotlin/references/testing.md) | Skill reference | Kotest, MockK, coroutine tests, property-based tests, and Kover |
| [`springboot`](.apm/skills/springboot/SKILL.md) | Skill | Index and gotchas for Spring Boot work |
| [`springboot/references/patterns.md`](.apm/skills/springboot/references/patterns.md) | Skill reference | REST structure, services, DTOs, exceptions, caching, async, filters, resilience, and observability |
| [`springboot/references/conventions.md`](.apm/skills/springboot/references/conventions.md) | Skill reference | Project setup, configuration, and build commands |
| [`springboot/references/jpa.md`](.apm/skills/springboot/references/jpa.md) | Skill reference | Entities, relationships, queries, transactions, auditing, indexing, and pooling |
| [`springboot/references/security.md`](.apm/skills/springboot/references/security.md) | Skill reference | Authentication, authorization, validation, CSRF, secrets, headers, CORS, and rate limiting |
| [`springboot/references/testing.md`](.apm/skills/springboot/references/testing.md) | Skill reference | Unit, MockMvc, persistence, and Testcontainers tests and coverage |
| [`springboot/references/verification.md`](.apm/skills/springboot/references/verification.md) | Skill reference | Build, static analysis, tests, security scan, and diff review |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `java/references/patterns.md` | [ECC `java-coding-standards`](https://github.com/affaan-m/ECC/blob/main/skills/java-coding-standards/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `java/references/testing.md` | [awesome-copilot `java-junit5-assertions.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/java-junit5-assertions.instructions.md) | Adapted | `797337f` (2026-11-06) | Replaced emoji markers with text; removed the pointer to a `java-junit` skill that DevHub does not include |
| `java/references/tooling.md` | DevHub, with steps from [ECC `springboot-verification`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-verification/SKILL.md) | Authored | `b38be6a` (2026-11-06) | Not applicable |
| `kotlin/references/patterns.md` | [ECC `kotlin-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `kotlin/references/coroutines.md` | [ECC `kotlin-coroutines-flows`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-coroutines-flows/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Removed pointers to Android and Compose skills that DevHub does not include |
| `kotlin/references/ktor.md` | [ECC `kotlin-ktor-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-ktor-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `kotlin/references/testing.md` | [ECC `kotlin-testing`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-testing/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `springboot/references/patterns.md` | [ECC `springboot-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `springboot/references/conventions.md` | [awesome-copilot `springboot.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/springboot.instructions.md) | Adapted | `797337f` (2026-11-06) | None |
| `springboot/references/jpa.md` | [ECC `jpa-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/jpa-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `springboot/references/security.md` | [ECC `springboot-security`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-security/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `springboot/references/testing.md` | [ECC `springboot-tdd`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-tdd/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `springboot/references/verification.md` | [ECC `springboot-verification`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-verification/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Removed the report template and continuous mode, which the common agents' reports and workflow own |
| Instructions and `SKILL.md` indexes | DevHub | Authored | Not applicable | None |

---

## Consumption

The package depends on [`development-core`](../development-core/README.md) for shared local capabilities. Add the stack package to the consumer's `apm.yml`, then install and verify it using the host-specific procedure described in the [APM guide](../README.md#repository-setup):

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/development-java
```

State the JDK, build tool, framework, and validation commands in the repository's `AGENTS.md`. Changes are recorded in the [changelog](CHANGELOG.md).
