---
name: java
description: 'Java patterns, testing, and tooling for DevHub repositories: naming, immutability, records, Optional, streams, exceptions, generics, logging, JUnit 5 assertions, and Maven or Gradle builds with formatting, coverage, and dependency audits. Use when writing, testing, reviewing, or setting up Java code or builds. Opens one focused reference per task.'
---

# Java

Index for Java work. Open only the reference the task needs; the Java and common instructions take precedence over the references.

## When to Use This Skill

- Writing, refactoring, or reviewing Java code
- Writing or reviewing JUnit tests and assertions
- Setting up or changing Maven or Gradle builds, formatting, or checks

## Steps

1. **Write or change code.** Open [references/patterns.md](references/patterns.md) for naming, immutability, `Optional`, streams, dependency injection, exceptions, generics, project structure, logging, and configuration.
2. **Write or change tests.** Open [references/testing.md](references/testing.md) for JUnit 5 assertions; for Spring tests, use the `springboot` skill's testing reference.
3. **Set up or change tooling.** Open [references/tooling.md](references/tooling.md) for wrapper commands, toolchains, formatting, coverage, and dependency audits.
4. **Validate.** Run the validation commands from the Java instructions and report each result.

## Gotchas

- **Boxed comparisons:** `==` on `Integer` or `Long` compares references and only appears to work for small cached values; use `equals`.
- **Immutable versus fixed-size lists:** `List.of` rejects `null` and all changes, while `Arrays.asList` allows `set` but not `add` or `remove`.
- **Modifying while iterating:** removing from a collection inside a for-each loop throws `ConcurrentModificationException`; use `removeIf` or an iterator.
- **Money and decimals:** use `BigDecimal` created from strings, such as `new BigDecimal("0.10")`, never from a `double`.
- **`equals` without `hashCode`:** override both, or use a record, which generates them.
- **`Optional.get()`:** throws when empty; use `orElseThrow` with a meaningful exception or a safe default.

## Related Skills

- `springboot`: Spring Boot applications, JPA, security, and verification.
- `kotlin`: Kotlin code, coroutines, and Ktor.

## References

- [Java SE documentation](https://docs.oracle.com/en/java/javase/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
