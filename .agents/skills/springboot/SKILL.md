---
name: springboot
description: 'Spring Boot patterns: REST controllers, layered services, DTOs and validation, exception handling, configuration, JPA and Hibernate, Spring Security, slice and integration tests with Testcontainers, and the build, analysis, test, and security verification loop. Use when building, testing, securing, or reviewing Spring Boot applications, data access, or configuration.'
---

# Spring Boot

Index for Spring Boot work; apply it together with the `java` or `kotlin` skill. The Java, Kotlin, and common instructions take precedence over the references.

## When to Use This Skill

- Building or changing Spring Boot controllers, services, or configuration
- Designing JPA entities, repositories, queries, or transactions
- Adding authentication, authorization, validation, or security headers
- Writing unit, web, persistence, or integration tests
- Verifying a Spring Boot service before review or release

## Steps

1. **Structure the change.** Open [references/patterns.md](references/patterns.md) for REST structure, repositories, transactional services, DTOs and validation, exception handling, caching, async processing, filters, pagination, resilience, and observability.
2. **Check conventions.** Open [references/conventions.md](references/conventions.md) for project setup, configuration, and build commands.
3. **Change data access.** Open [references/jpa.md](references/jpa.md) for entity design, relationships, N+1 prevention, transactions, auditing, indexing, pagination, and pooling.
4. **Change security.** Open [references/security.md](references/security.md) for authentication, authorization, validation, CSRF, secrets, headers, CORS, and rate limiting.
5. **Write tests.** Open [references/testing.md](references/testing.md) for unit, MockMvc, persistence, and Testcontainers tests and coverage.
6. **Verify.** Follow [references/verification.md](references/verification.md) for the build, static analysis, tests with coverage, security scan, and diff review, and report each result.

## Gotchas

- **Proxy-based `@Transactional`:** it has no effect on private methods or calls from within the same class; call a public method on another bean.
- **Open session in view:** `spring.jpa.open-in-view` is enabled by default and hides lazy loading in the web layer; set it to `false`.
- **Eager to-one relations:** `@ManyToOne` and `@OneToOne` fetch eagerly by default; set `fetch = FetchType.LAZY` and fetch explicitly where needed.
- **Entities in APIs:** never return JPA entities from controllers; map them to DTOs.
- **Full contexts in tests:** `@SpringBootTest` starts the whole application; prefer slices such as `@WebMvcTest` and `@DataJpaTest`.
- **Jakarta namespace:** Spring Boot 3 and later use `jakarta.*` packages; never add `javax.*` imports for servlet, validation, or persistence APIs.

## Related Skills

- `java`: Java patterns, testing, and build tooling.
- `kotlin`: Kotlin patterns and coroutines.

## References

- [Spring Boot reference](https://docs.spring.io/spring-boot/index.html)
- [Spring Framework reference](https://docs.spring.io/spring-framework/reference/)
- [Spring Security reference](https://docs.spring.io/spring-security/reference/)
