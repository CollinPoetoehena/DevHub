---
description: "Use when writing, testing, or reviewing Java code or Maven and Gradle builds: toolchain defaults, mandatory rules, and validation commands on top of the common instructions."
applyTo: "**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts,**/settings.gradle,**/settings.gradle.kts"
---

# Java Instructions

These rules add Java specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `java` skill before adding classes, tests, or build configuration; it opens one reference per task.
- Apply the `springboot` skill for Spring Boot code and the `kotlin` skill for Kotlin code.

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

## References

- [Java SE documentation](https://docs.oracle.com/en/java/javase/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Maven guides](https://maven.apache.org/guides/)
- [Gradle user manual](https://docs.gradle.org/current/userguide/userguide.html)
- [JUnit User Guide](https://docs.junit.org/current/user-guide/)
