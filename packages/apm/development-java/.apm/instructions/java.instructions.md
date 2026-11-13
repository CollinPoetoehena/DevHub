---
description: "Use when writing, testing, or reviewing Java code or Maven and Gradle builds: toolchain defaults, essential conventions, and validation commands alongside the common guidelines."
applyTo: "**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts,**/settings.gradle,**/settings.gradle.kts"
---

# Java Guidelines

Use general best practices for Java and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Java, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

## Toolchain

Follow the repository's existing build and tooling. For new projects, default to:

- **JDK:** the latest LTS release supported by the framework, declared as a toolchain or compiler release level in the build.
- **Build:** Maven or Gradle through the committed wrapper (`./mvnw` or `./gradlew`), never a system installation.
- **Formatting:** Spotless with google-java-format.
- **Tests:** JUnit 5 with AssertJ or Jupiter assertions and Mockito; JaCoCo for coverage.
- **Static analysis and audit:** the configured SpotBugs, PMD, or Checkstyle rules, and OWASP Dependency-Check.

## Rules

- Prefer immutability: `final` fields, records for data carriers, and unmodifiable collections such as `List.of` and `List.copyOf`.
- Use constructor injection; never field injection.
- Return `Optional` only from methods that may have no result; never use it for fields or parameters, and never return `null` collections.
- Catch specific exceptions, keep the cause when wrapping, and never swallow exceptions; close resources with try-with-resources.
- Log with SLF4J placeholders, such as `log.info("Created {}", id)`, never `System.out` or string concatenation, and never log secrets.
- Use only language features supported by the build's release level, such as records from Java 16, sealed classes from Java 17, and pattern matching for `switch` and virtual threads from Java 21.
- Use explicit imports, not wildcard imports.

## Validation

Run from the project root; use the repository's configured commands when they differ:

```sh
./mvnw -B verify      # Maven: compile, test, and configured checks
./gradlew check       # Gradle: compile, test, and configured checks
```

Also run the formatter check and dependency audit when the build configures them, such as `spotless:check` and OWASP Dependency-Check.

## Relevant Skills

- Use the `java` skill for additional Java procedures and references.
- Use the `springboot` skill for Spring Boot, and the `kotlin` skill for Kotlin.

## References

- [Java SE documentation](https://docs.oracle.com/en/java/javase/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Maven guides](https://maven.apache.org/guides/)
- [Gradle user manual](https://docs.gradle.org/current/userguide/userguide.html)
- [JUnit User Guide](https://docs.junit.org/current/user-guide/)

Use relevant available skills for additional procedures and references.
