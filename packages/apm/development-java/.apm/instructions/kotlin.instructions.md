---
description: "Use when writing, testing, or reviewing Kotlin code or Gradle Kotlin DSL builds: toolchain defaults, essential conventions, and validation commands alongside the common guidelines."
applyTo: "**/*.kt,**/*.kts"
---

# Kotlin Guidelines

Use general best practices for Kotlin and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Kotlin, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

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

Use the `kotlin` and `springboot` skills for additional procedures; use the `java` skill for Java interoperability and build tooling.

## References

- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- [Coroutines guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Gradle Kotlin DSL](https://docs.gradle.org/current/userguide/kotlin_dsl.html)

Use relevant available skills for additional procedures and references.
