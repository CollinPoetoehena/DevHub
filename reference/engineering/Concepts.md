# Engineering Concepts

These are generic, language-independent engineering concepts. They apply across applications, libraries, automation, and infrastructure; the linked sources provide detail, not a requirement to adopt a particular product.

See [Scope and approach](README.md#scope-and-approach) for why this guide highlights the main points rather than attempting complete coverage, and where to explore further.

For implementation-specific practices, see [Languages & Tools](Languages_and_Tools.md). For design trade-offs, see [Software Engineering Principles](Software_Engineering_Principles.md).

---

## Table of Contents

- [Software development lifecycle](#software-development-lifecycle)
- [Reusability and build versus adopt](#reusability-and-build-versus-adopt)
  - [Personal example: monitoring and alerting](#personal-example-monitoring-and-alerting)
- [Automation and continuous delivery](#automation-and-continuous-delivery)
- [Security and privacy by design](#security-and-privacy-by-design)
- [Observability](#observability)
- [Error handling and resilience](#error-handling-and-resilience)
- [Testing and validation](#testing-and-validation)
- [Configuration and lifecycle](#configuration-and-lifecycle)
- [Data modeling and contracts](#data-modeling-and-contracts)
- [Documentation](#documentation)
  - [Personal perspective](#personal-perspective)

---

## Software development lifecycle

The software development lifecycle (SDLC) outlines the tasks required to build and maintain a software application as teams add features and fix bugs. The details vary between teams, but common phases are Plan, Design, Implement, Test, Deploy, and Maintain. These phases can overlap and repeat rather than requiring a rigid waterfall process. See [SDLC overview](https://aws.amazon.com/what-is/sdlc/).

- **Plan:** Collect requirements from stakeholders, including customers, subject-matter experts, and managers, and establish shared goals and expectations. Record them in a software requirements specification where appropriate. Planning typically includes cost-benefit analysis, scheduling, resource estimation, and allocation so the team has a realistic plan for achieving its goals.
- **Design:** Analyze the requirements and compare solutions before implementation. Consider reusing existing modules, selecting technologies and development tools, defining interfaces, and integrating the application with existing infrastructure. Record significant decisions and trade-offs so the design explains how the proposed solution meets the requirements.
- **Implement:** Code the product by breaking requirements into smaller, manageable development tasks. Work toward the agreed design and goals through incremental changes, reviewing the implementation and keeping directly affected documentation consistent with the behavior being built.
- **Test:** Combine automated and manual testing as appropriate to find defects and check whether the software meets requirements and user expectations. Testing often runs alongside implementation because teams validate changes as they write them; it is not necessarily a separate activity postponed until all coding is complete.
- **Deploy:** Move a validated build into the production environment used by customers. Build and test changes in separate environments so ongoing development does not directly disrupt the live application. Deployment includes packaging, environment configuration, and installation, with verification and rollback or recovery planning appropriate to the change.
- **Maintain:** Fix bugs, resolve user issues, and manage changes after deployment. Monitor performance, security, and user experience to identify improvements, and feed those findings into further planning and development rather than treating release as the end of the lifecycle.

---

## Reusability and build versus adopt

Reuse applies to architecture and complete systems, not only functions and libraries. The [DRY principle](Software_Engineering_Principles.md#dry--dont-repeat-yourself) helps avoid duplicating knowledge; build-versus-adopt decisions also ask whether an existing system already owns a capability better than a new local implementation could.

- **Look beyond code reuse:** Consider established libraries, platforms, protocols, hosted services, and operational tooling before implementing a scheduler, identity service, alerting engine, or other substantial subsystem.
- **Spend effort on differentiating needs:** Reuse standard capabilities and build the domain-specific behavior that actually adds value. Implementing an integration can be worthwhile without reimplementing the system behind it.
- **Choose deliberately:** Assess maturity, active maintenance, documentation, adoption, interoperability, security response, licensing, operational fit, and an exit path. Broad adoption is useful evidence, not proof that a tool fits every situation; a newly released project with little support needs a stronger justification.
- **Compare lifetime costs:** Count development, edge cases, testing, upgrades, on-call support, state management, and failure recovery—not just the time to produce a working prototype. Established systems also need configuration and maintenance, but their capabilities can be shared across many users and maintainers.
- **Avoid unnecessary wrappers:** Adopt a tool's supported interfaces and extend only what is missing. A full shadow implementation can erase the value of reuse; see [shared SDK boundaries](Packages.md#keep-the-scope-deliberate).
- **Keep a justified escape hatch:** Build a component when existing options fail important requirements or create greater cost and risk. Record the reason and revisit it as tools and requirements change; reuse is a default to evaluate, not a ban on innovation.

### Personal example: monitoring and alerting

I once built a monitoring framework that ran operational checks and also implemented their state tracking and alert handling and dispatching/routing. It worked, but I had effectively taken on responsibility for a monitoring and alerting platform: repeated failures, recovery, notification timing, and related edge cases all became my code to design, test, and maintain.

Later, I moved toward exporting measurements and check outcomes to [Prometheus](https://prometheus.io/docs/introduction/overview/) rather than owning the entire alerting lifecycle. Prometheus evaluates [alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) and tracks their pending/firing state; [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) handles notification grouping, deduplication, routing, silences, and inhibition. Domain-specific probes or exporters can still run the checks; this does not replace application unit or integration tests.

These are mature, widely adopted components with an established ecosystem, not a small new dependency chosen merely because it exists. Reusing them let me focus on meaningful measurements, domain checks, and useful alert policies instead of building a less complete alternative with far less time and fewer contributors. I still own the integration, configuration, and operational suitability—the lesson is to reuse established capabilities, not to assume a tool removes all responsibility.

---

## Automation and continuous delivery

Automation makes repeatable work explicit and executable; continuous integration (CI) validates integrated changes frequently, while continuous delivery keeps software releasable. Continuous deployment additionally releases qualifying changes automatically. See [DORA continuous integration](https://dora.dev/capabilities/continuous-integration/) and [continuous delivery](https://dora.dev/capabilities/continuous-delivery/).

- **Automate the stable procedure:** Start with a process that is understood, then encode recurring builds, checks, releases, configuration, or operational tasks. Do not automate an unclear or unnecessary process just to preserve it.
- **Make execution predictable:** Use explicit inputs, controlled dependencies, clear failure messages, and safe handling of partial completion. Consider idempotency, retries, and a dry-run mode where they improve safety.
- **Keep feedback fast and meaningful:** Run focused checks early and more expensive checks where their risk coverage justifies the cost. A green pipeline only demonstrates what its checks actually cover.
- **Protect consequential actions:** Separate validation from deployment, use least-privilege credentials, identify safe targets, and require approvals where warranted. Infrastructure and data changes need recovery planning, not just a convenient command.
- **Own the automation:** Version and review scripts and pipelines like other software. Record prerequisites, usage, and failure/recovery steps; avoid a collection of undocumented commands that only its author can operate.

---

## Security and privacy by design

Security is part of requirements, design, implementation, delivery, and operation—not a scan added at the end. See the [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf).

- Identify trust boundaries, sensitive data, likely misuse, and who is authorized to do what; validate inputs and apply least privilege rather than relying on a trusted environment.
- Minimize collected data and exposed secrets, protect credentials and artifacts, and keep logs and examples free of sensitive content.
- Track dependencies and support lifecycles, review changes, and define how vulnerabilities and incidents are reported and handled. Automated checks support these decisions but do not establish that a system is secure.

---

## Observability

Observability helps explain a system's behavior through its outputs; monitoring uses selected signals to detect known conditions. See [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/observability-primer/) and [Google SRE monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/).

- **Logs:** Records of events with enough context to investigate; use consistent structure and severity without exposing secrets or personal data. See [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/).
- **Metrics:** Measurements aggregated over time for trends, capacity, and service health; control label cardinality. See [OpenTelemetry metrics](https://opentelemetry.io/docs/concepts/signals/metrics/) and [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/).
- **Traces:** The path and timing of work across components; propagate correlation context where useful. See [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/) and [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/).
- **Alerting:** Notify an owner about actionable conditions, preferably tied to user impact and service objectives, not every anomalous event. See [Google SRE alerting guidance](https://sre.google/workbook/alerting-on-slos/).
- **Ownership:** Libraries emit useful signals without choosing the application's logging/export configuration. Applications and platforms own collection, retention, access, and alert routing.

---

## Error handling and resilience

- Treat failures as part of the public contract: distinguish invalid input, programming errors, and expected operational failures; expose enough context for callers to decide what to do.
- Catch only failures that can be handled meaningfully, preserve the cause when translating errors at a boundary, and avoid silent success-shaped fallbacks or repeated logging of the same propagated failure.
- Use timeouts and bounded retries with backoff for suitable transient failures; consider idempotency before retrying work with side effects. See [AWS guidance on timeouts, retries, and backoff](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).
- Define failure responses consistently at service boundaries. For HTTP APIs, [RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457) is one standardized representation; it does not replace language-level errors.

---

## Testing and validation

- Test observable contracts, meaningful edge cases, and failure paths; use unit, integration, and end-to-end checks according to the risks rather than a fixed quota. See [Google's testing overview](https://abseil.io/resources/swe-book/html/ch11.html).
- Keep test code and fixtures simple; mock external boundaries when necessary rather than tying tests to private implementation details.
- Static analysis, formatting, and dry runs complement tests but do not prove runtime correctness. State what was actually verified and what still needs a safe environment.
- When using AI to generate tests, provide the code, contracts, project setup, and risks first; review the plan and assertions, then implement in bounded steps. AI output is not an independent correctness oracle.

---

## Configuration and lifecycle

- Separate deploy-specific configuration from code, validate required settings early, and manage secrets outside source control. See [Twelve-Factor configuration](https://12factor.net/config).
- Make startup, cancellation, resource cleanup, and graceful shutdown explicit; keep dependencies and runtime assumptions reproducible. See [Twelve-Factor disposability](https://12factor.net/disposability) and [dependencies](https://12factor.net/dependencies).

---

## Data modeling and contracts

- Make inputs, outputs, invariants, and ownership clear; choose functions, mappings, value objects, or classes according to the contract rather than a preferred syntax.
- Object-oriented programming groups state and behavior through objects; encapsulation, abstraction, polymorphism, and inheritance are tools, not requirements. See [Microsoft's OOP overview](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/tutorials/oop) for an introduction illustrated in one language, and the [design principles](Software_Engineering_Principles.md#oop--object-oriented-programming) for general trade-offs.

---

## Documentation

Documentation helps a reader use a system, understand its supported behavior, operate it safely, or maintain an important decision. It is part of the product, not a measure of how much the author knows. See [Write the Docs](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/), [Diataxis](https://diataxis.fr/), and [architecture decision records](https://adr.github.io/).

- **Document for added value, not volume:** Every written explanation creates a potential liability and an ongoing maintenance commitment: it must stay accurate, consistent with the implementation and its sources, and worth the effort to review and update. Include documentation when it helps users or maintainers make a decision, understand supported behavior, or avoid a meaningful risk. Do not document something merely because it can be documented; duplicated, stale, misleading, or unnecessary text adds work without corresponding value.
- **Reader and purpose first:** Identify who needs the information and what they should be able to do afterward, such as install a package, diagnose a failure, or change behavior safely. Tutorials, task-oriented guides, reference, and explanation serve different needs; an incident runbook should not become a language lesson.
- **Decisions over copied theory:** Preserve significant choices, relevant alternatives, constraints, and consequences that readers cannot reconstruct from code alone. Official documentation can explain a language feature or API, but cannot recover why a particular project selected it. Record when an important decision should be revisited rather than retaining a transcript of the implementation process.
- **Concise, discoverable format:** Use descriptive headings, scannable bullets, and authoritative links for shared practices. Put purpose, scope, and commonly needed information first; use tables for real comparisons, not to make prose appear comprehensive. Expand where misunderstanding has a cost, and keep indexes and heading links current.
- **README references and one source of truth:** Keep shared practices in their central guide and link to it once from each consuming package or application's README, pointing to relevant sections where useful. The README is the discoverable entry point for shared guidance, not a reason to repeat the same links, general rules, or compliance comments throughout source files. Keep package-specific documentation focused on its behavior, usage, and exceptions rather than copying shared explanations; one central update should not require editing the same guidance in every consumer.
- **Keep guidance with code:** Version and review essential engineering context alongside the software so it is searchable in the IDE and available offline after cloning. A separate documentation service can support collaboration, but should not be the only home of information required to maintain the implementation.
- **High-level versus local:** Use the README as the entry point for purpose, scope, supported environments, design, development, testing, installation, and usage. Move substantial explanations into linked `docs/` pages, significant choices into decision records, and operational diagnosis and recovery into runbooks. Source comments should not become a second README or whole-system design essay.
- **Code documentation for contracts and constraints:** Document public behavior, supported contracts, important constraints, and non-obvious choices readers need to use or maintain the code correctly. Use native API documentation or docstrings for relevant inputs, units, defaults, results, errors, side effects, resource ownership, or concurrency requirements. Do not mechanically fill every category, repeat signatures or type annotations, explain routine language syntax, or document every private implementation detail. Routine mechanics can change without affecting the contract; describing them anyway creates documentation updates without helping the reader.
- **What not to document (if needed learn via online docs, AI, or experiments; do not put that in comments):** Do not explain general language theory, concepts, or syntax in production code comments, docstrings, READMEs, or project documentation—not even as a reminder while learning. What a loop, import, class, inheritance, dataclass, generic, or context manager is belongs in language learning material and authoritative language documentation, not alongside the software. To learn these topics, consult official documentation or reliable online sources, ask AI and verify its answers, or experiment in a separate project or a dedicated repository for multiple experiments. Keep those learning notes and experiments separate from the code and its supported documentation. A narrow exception is useful when a language feature is chosen for a specific project reason or has a non-obvious effect on the software: briefly explain why this code uses it or what behavior, constraint, or contract follows from it, without teaching the feature's general theory or syntax. For example, document why a resource's ownership and cleanup requirements matter here, not how context-manager syntax works. Also avoid line-by-line narration, paraphrased function signatures, copied vendor API references, exhaustive descriptions of private helpers, and repeated claims that code follows a general best practice. Purpose-built learning material can explain fundamentals for its audience, but a package README or source file should not become a tutorial merely because the author learned something while implementing it.
- **Comments for local specifics:** Prefer clear names, types, and straightforward code, then add a brief comment only for an important, non-obvious implementation constraint, workaround, or special case that the code itself does not explain. Keep it close to the affected code: for example, explain why a non-idempotent operation must not be retried or what would allow a provider workaround to be removed. Do not use local comments to repeat shared guidance, narrate loops or imports, justify every dataclass, or reproduce general design rationale that belongs in discoverable design documentation.
- **Let code be the example:** The working implementation often explains routine setup sufficiently; duplicating a complete logging configuration or build file in prose creates another copy that can drift. Use a small representative example when it helps demonstrate supported usage, label illustrative pseudocode, and keep copyable examples current.
- **Make instructions usable and safe:** State relevant prerequisites, versions, environment assumptions, and optional steps. Write procedures in execution order with an observable success condition and a next step after consequential failures. Use safe placeholders, never credentials or private data; flag destructive operations, their target, and recovery needs before the commands.
- **Exceptions and special cases:** When a package or application intentionally differs from shared guidance, record the relevant practice, reason for departing from it, scope, and consequences for maintainers or consumers in its README or design documentation linked from it. Readers should be able to discover the rationale without searching implementation comments. Add a local comment only if a specific implementation detail also needs explanation; it complements rather than replaces the documented decision. If the exception becomes a shared practice, update the central guide instead of duplicating the new rule across packages.
- **Use documentation as working context:** Read relevant guidance and decisions during development, review, onboarding, and incident response, not only when writing a new document. Use recurring questions and mistakes to improve the authoritative explanation rather than creating another overlapping guide.
- **Maintain and remove:** Review documentation with behavior changes, refresh examples and links, and remove obsolete or redundant claims. Give shared and operational guidance an owner; revisit it when dependencies or workflows change and mark known gaps honestly. Existing documentation checks or generated references can help, but do not replace readable contracts and human review.
- **Use AI with a concrete purpose:** Ask for the audience, behavior, decisions, or risks to be explained, not maximum comments or an explanation of every line. Verify generated claims, commands, examples, and links against actual behavior and authoritative sources; fluent text is not evidence that a procedure works. The [AI skill documentation guidance](../../.github/skills/README.md#comments-and-code-documentation) and [documentation skill](../../.github/skills/devhub-docs/SKILL.md) apply these practices in reusable workflows.
- **Keep reusable skills self-contained:** Essential rules remain inside each installed skill, while this conceptual guide is optional background. That limited duplication serves portability when DevHub is unavailable; it is different from repeating general design explanations throughout application code.

### Personal perspective

Early in my career I often treated documenting more as documenting better. I added best-practice links throughout source files and very large comment blocks explaining basic language concepts or every implementation choice. In places, the comments grew to more than three times the amount of actual code.

For example, I might explain what a dataclass is above a straightforward value model, describe inheritance syntax next to a class, or repeat links to logging and package-design guidance in every module. Those explanations could help me while learning, but keeping them all in production code did not make the software proportionately clearer. They pushed related statements apart and made readers work through a tutorial before finding the behavior they needed.

The burden then repeated with every change: code, comments, examples, and linked explanations all had to remain consistent. If I changed the implementation without rewriting the commentary, the documentation became misleading. Repeating the same reference across many files also created maintenance work without adding new context. I had produced more information to check and trust, not necessarily more useful knowledge.

I now try to separate learning from the supported explanation of the software:

- A simple dataclass usually needs a clear name and fields, not a local essay about dataclasses. A comment is worthwhile if a specific invariant or compatibility constraint is not apparent.
- A package can link the shared logging guidance from its README and apply it in code. Every logger declaration does not need that link again.
- A short note explaining why a timeout differs from the normal default can preserve important reasoning; a paragraph explaining every argument of a routine call usually cannot.
- A design decision belongs where maintainers can find its context and consequences. Routine syntax can be refreshed through official documentation, reliable online material, or AI with verification.

This is not a reason to leave important contracts or operational risks undocumented. It is a reason to trust your ability to read code in general, document the information that would otherwise be lost, and stop explaining once the reader has what they need. Concise, relevant documentation gives me more time to maintain the software and makes the remaining explanations easier to find and keep accurate.
