# Java Tooling

DevHub defaults for Java builds and checks; the static analysis and coverage steps follow [ECC `springboot-verification`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-verification/SKILL.md). Repository configuration and the Java and common instructions take precedence over this reference.

## Defaults

| Concern | Tool | Notes |
|---|---|---|
| JDK | Build toolchain or compiler release | Latest LTS supported by the framework |
| Build | Maven or Gradle wrapper | Commit `mvnw` or `gradlew` with their wrapper properties |
| Formatting | Spotless with google-java-format | Check in CI, apply locally |
| Static analysis | SpotBugs, PMD, Checkstyle | Only the tools the build configures |
| Tests and coverage | JUnit 5, Mockito, AssertJ, JaCoCo | |
| Dependency audit | OWASP Dependency-Check | |

## Commands

| Task | Maven | Gradle |
|---|---|---|
| Build, test, and configured checks | `./mvnw -B verify` | `./gradlew build` |
| Tests only | `./mvnw test` | `./gradlew test` |
| One test class | `./mvnw test -Dtest=UserServiceTest` | `./gradlew test --tests UserServiceTest` |
| Format | `./mvnw spotless:apply` | `./gradlew spotlessApply` |
| Format check | `./mvnw spotless:check` | `./gradlew spotlessCheck` |
| Coverage report | `./mvnw jacoco:report` | `./gradlew jacocoTestReport` |
| Dependency audit | `./mvnw org.owasp:dependency-check-maven:check` | `./gradlew dependencyCheckAnalyze` |

## Java Version

Declare the Java version in the build so every machine compiles the same way.

Gradle:

```kotlin
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
    }
}
```

Maven:

```xml
<properties>
  <maven.compiler.release>25</maven.compiler.release>
</properties>
```

## Formatting

Gradle with Spotless:

```kotlin
plugins {
    id("com.diffplug.spotless") version "<version>"
}

spotless {
    java {
        googleJavaFormat()
    }
}
```

Update a wrapper with `./gradlew wrapper --gradle-version <version>` or `./mvnw wrapper:wrapper -Dmaven=<version>`, and commit the result.

## References

- [Maven guides](https://maven.apache.org/guides/)
- [Maven Wrapper](https://maven.apache.org/tools/wrapper/)
- [Gradle user manual](https://docs.gradle.org/current/userguide/userguide.html)
- [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html)
- [Gradle Java toolchains](https://docs.gradle.org/current/userguide/toolchains.html)
- [Spotless](https://github.com/diffplug/spotless)
- [google-java-format](https://github.com/google/google-java-format)
- [JaCoCo](https://www.jacoco.org/jacoco/trunk/doc/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
