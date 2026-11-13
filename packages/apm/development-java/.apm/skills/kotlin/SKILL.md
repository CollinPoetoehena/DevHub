---
name: kotlin
description: 'Kotlin patterns, coroutines, Ktor, and testing for DevHub repositories: null safety, immutability, sealed types, scope and extension functions, delegation, DSLs, Gradle Kotlin DSL, coroutines and Flow, Ktor routing, plugins, and authentication, and Kotest, MockK, and coroutine tests. Use when writing, testing, or reviewing Kotlin code. Opens one focused reference per task.'
---

# Kotlin

Index for Kotlin work. Open only the reference the task needs; the Kotlin and common instructions take precedence over the references.

## When to Use This Skill

- Writing, refactoring, or reviewing Kotlin code or Gradle Kotlin DSL builds
- Writing coroutines, Flows, or concurrent code
- Building Ktor servers, routes, or plugins
- Writing Kotest, MockK, or coroutine tests

## Steps

1. **Write or change code.** Open [references/patterns.md](references/patterns.md) for null safety, immutability, sealed types, scope and extension functions, delegation, DSL builders, sequences, Gradle Kotlin DSL, and error handling.
2. **Write concurrent code.** Open [references/coroutines.md](references/coroutines.md) for structured concurrency, Flow operators, StateFlow and SharedFlow, dispatchers, and cancellation.
3. **Build a Ktor server.** Open [references/ktor.md](references/ktor.md) for application structure, routing, serialization, authentication, status pages, CORS, Koin, validation, WebSockets, and `testApplication`.
4. **Write or change tests.** Open [references/testing.md](references/testing.md) for Kotest specs, MockK, coroutine testing, property-based tests, and Kover coverage.
5. **Validate.** Run the validation commands from the Kotlin instructions and report each result.

## Gotchas

- **Swallowed cancellation:** `runCatching` and `catch (e: Exception)` also catch `CancellationException`, which breaks structured cancellation; rethrow it.
- **Cold Flows repeat work:** each `collect` re-runs a cold Flow; share results with `stateIn` or `shareIn`.
- **`lateinit` access:** reading a `lateinit` property before assignment throws; prefer constructor parameters or `by lazy`.
- **Mutable keys:** a data class with `var` properties changes its hash code when mutated, which breaks sets and map keys.
- **Platform types:** values from Java APIs can be `null` despite non-null Kotlin types; declare them nullable at the boundary.

## Related Skills

- `java`: JVM build tooling and Java interoperability.
- `springboot`: Spring Boot applications in Kotlin or Java.

## References

- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
