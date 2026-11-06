---
description: "Use when writing, testing, or reviewing Kotlin code or Gradle Kotlin DSL builds: toolchain defaults, mandatory rules, and validation commands on top of the common instructions."
applyTo: "**/*.kt,**/*.kts"
---

# Kotlin Instructions

These rules add Kotlin specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `kotlin` skill before adding classes, coroutines, Ktor routes, or tests; it opens one reference per task.
- Apply the `springboot` skill for Spring Boot code and the `java` skill for Java interoperability and build tooling.

## Toolchain

Follow the repository's existing build and tooling. For new projects, default to:

- **Build:** Gradle with the Kotlin DSL through the committed wrapper, and a JVM toolchain declared in the build.
- **Formatting and linting:** ktlint or detekt through their Gradle plugins.
- **Tests:** Kotest or JUnit 5 with MockK and `kotlinx-coroutines-test`; Kover for coverage.

## Rules

- Prefer `val`, read-only collections, and data classes for value carriers.
- Avoid `!!`; use safe calls, `?:`, or `requireNotNull` with a message, and treat Java platform types as nullable.
- Launch coroutines in a lifecycle-bound scope, never `GlobalScope`; inject dispatchers, and never call `runBlocking` in production code paths.
- Rethrow `CancellationException`; do not swallow it with `catch (e: Exception)` or `runCatching` in suspending code.
- Model closed hierarchies with sealed classes or interfaces and handle them with exhaustive `when` expressions without `else`.
- Use scope functions only when they improve clarity, and do not nest them.

## Validation

Run from the project root; use the repository's configured tasks when they differ:

```sh
./gradlew check
```

Also run the configured lint and coverage tasks, such as `ktlintCheck`, `detekt`, or `koverVerify`.

## References

- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- [Coroutines guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Gradle Kotlin DSL](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
