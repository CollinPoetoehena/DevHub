# Languages & Tools

Concise practices for programming languages, automation tools, and packaging formats. Use the linked official documentation for syntax, theory, layouts, and current behavior.

See [Scope and approach](README.md#scope-and-approach) for why this guide is selective rather than a complete language/tool reference, and where to explore further.

Shared [engineering concepts](Concepts.md), [design principles](Software_Engineering_Principles.md), and [package organization](Packages.md) live separately. Apply these practices where they fit the project rather than imposing one language, build backend, or test layout on every package.

---

## Table of Contents

- [Scope and framework boundary](#scope-and-framework-boundary)
- [Languages and tools](#languages-and-tools)
  - [Python](#python)
  - [Go](#go)
  - [Java](#java)
  - [JavaScript](#javascript)
  - [TypeScript](#typescript)
  - [Rust](#rust)
  - [C](#c)
  - [C++](#c-1)
  - [Shell](#shell)
  - [Ansible](#ansible)
  - [Terraform](#terraform)
  - [Helm](#helm)
  - [Docker](#docker)
  - [Configuration and markup](#configuration-and-markup)

---

## Scope and framework boundary

- Focus on language, runtime, build/package, and tool-level practices. This is a selective reference, not a complete catalog of every ecosystem or a promise that every listed language is used in each project.
- The [overview table](#languages-and-tools) briefly explains what each item is, typical uses, benefits, and trade-offs, with links to its short practice notes. This is high-level orientation, not a complete comparison or selection framework; deeper language and tool details belong in the linked official documentation.
- Framework-specific architecture, APIs, configuration, and tutorials belong in the framework's official documentation and the project that uses it, not in expanding subsections here.
- A short pointer can help orientation: [FastAPI](https://fastapi.tiangolo.com/) is one option for Python HTTP APIs, and [Spring Boot](https://docs.spring.io/spring-boot/index.html) supports Java application setup and conventions. These are examples, not default requirements or endorsements for every use case.
- Choose an appropriate supported language/runtime version and established project tooling. Record concrete framework choices and their reasons with the consuming application instead of duplicating framework theory here.

---

## Languages and tools

Use this overview to orient yourself, then follow an item's link for focused practices and official references. Benefits and trade-offs depend on the workload, ecosystem, and team's experience; these summaries are not rankings or reasons to replace suitable existing tooling.

| Language or tool | What it is | Typical use | Benefits | Trade-offs |
|------------------|------------|-------------|----------|------------|
| [Python](#python) | Dynamically typed, general-purpose language. | Automation, services, data processing. | Readable; broad library ecosystem. | Runtime type errors; Python-level CPU work can be slow. |
| [Go](#go) | Statically typed, compiled language with garbage collection. | Network services, CLIs, infrastructure tooling. | Straightforward deployment; built-in concurrency support. | Garbage-collection overhead; less control over memory layout. |
| [Java](#java) | Statically typed language commonly run on the JVM. | Backend services and long-lived applications. | Mature tooling; portability across compatible JVMs. | Runtime footprint; startup and build complexity. |
| [JavaScript](#javascript) | Dynamically typed language used in browsers and other runtimes. | Interactive web applications and server-side services. | Native browser support; broad ecosystem. | Runtime type errors; runtime and dependency differences. |
| [TypeScript](#typescript) | JavaScript with static type checking, usually emitted as JavaScript. | Larger browser and server-side codebases. | Earlier feedback; clearer interfaces and refactoring. | Extra tooling; types do not validate runtime data. |
| [Rust](#rust) | Compiled language with ownership-based memory safety. | Systems software, CLIs, performance-sensitive services. | Native performance; strong safe-code guarantees without garbage collection. | Ownership learning curve; compilation cost. |
| [C](#c) | Compiled language with direct memory access and a small runtime. | Embedded systems, operating systems, native interfaces. | Hardware control; widely supported toolchains. | Manual memory safety; portability requires care. |
| [C++](#c-1) | Compiled language combining low-level control and high-level abstractions. | Native applications, engines, performance-sensitive libraries. | Performance; rich abstractions and ecosystem. | Language complexity; lifetime and undefined-behavior risks. |
| [Shell](#shell) | Command interpreter and scripting environment. | Command orchestration and small operational scripts. | Direct reuse of existing command-line tools. | Quoting and portability hazards; complex logic becomes fragile. |
| [Ansible](#ansible) | Automation tool using playbooks and modules. | Configuration management and operational workflows. | Readable tasks; many idempotent modules. | Module-dependent behavior; inventory and variable complexity. |
| [Terraform](#terraform) | Declarative infrastructure provisioning tool using providers and state. | Managing infrastructure resources and their lifecycle. | Reviewable plans; reusable modules. | State management; provider differences and replacement risks. |
| [Helm](#helm) | Kubernetes package manager using templated charts. | Packaging and releasing Kubernetes resources. | Reusable deployment configuration; release management. | Template complexity; rendered resources still need validation. |
| [Docker](#docker) | Tooling for building and running container images. | Packaging applications for development, CI, and deployment. | Consistent application environments; process isolation. | Image maintenance; host-kernel dependence, not VM isolation. |
| [YAML](#configuration-and-markup) | Structured data format commonly used for configuration. | Tool configuration and declarative manifests. | Human-readable mappings and lists. | Indentation and implicit-type pitfalls; schema validation needed. |
| [Markdown](#configuration-and-markup) | Lightweight text markup format. | READMEs and version-controlled documentation. | Easy to edit, review, and render. | Renderer differences; links and examples need maintenance. |

### Python

Official references: [Python documentation](https://docs.python.org/3/), [PEP 8](https://peps.python.org/pep-0008/), [PEP 257](https://peps.python.org/pep-0257/), and [Python Packaging User Guide](https://packaging.python.org/en/latest/).

- **Packages:** Declare metadata, direct dependencies, and build configuration in `pyproject.toml`; choose a suitable backend and consider a `src/` layout to avoid accidental local imports. See [packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and [src versus flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
- **Releases:** Build and publish distributions using the project's chosen tooling; keep metadata, artifacts, and source tags consistent. See [publishing packages](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and the shared [release guidance](Packages.md#versioning-and-distribution).
- **Imports:** Keep the supported public surface small, avoid application startup logic in `__init__.py`, and import internal symbols from their defining modules rather than through facades that can create cycles. See [packages](https://docs.python.org/3/tutorial/modules.html#packages) and [`__all__`](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package).
- **Functions and models:** Type-annotate public APIs and keep return contracts predictable; use dataclasses, protocols, and generics only when they clarify a real contract. See [typing](https://docs.python.org/3/library/typing.html) and [dataclasses](https://docs.python.org/3/library/dataclasses.html).
- **Errors:** Catch specific exceptions, preserve causes with exception chaining, and introduce domain exception types only when callers need that distinction. See [exception handling](https://docs.python.org/3/tutorial/errors.html).
- **Logging:** Libraries use module loggers without configuring application handlers or levels; a top-level `NullHandler` is appropriate for library loggers. Applications configure logging at startup. See [library logging](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library) and the [logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html).
- **Tests:** Test public behavior and failures, keep fixtures local to their consumers, and patch at the lookup seam when mocking is necessary. See [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) and [where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch).
- **Analysis:** Use the project's formatter, linter, and type checker; address actionable findings rather than optimizing a score. See [Pylint](https://pylint.readthedocs.io/en/latest/) and [typing guidance](https://typing.python.org/en/latest/).

### Go

Official references: [Go documentation](https://go.dev/doc/) and [Effective Go](https://go.dev/doc/effective_go).

- **Packages:** Use modules for dependency and release boundaries; keep package names focused and separate commands from reusable code when useful. See [module layout](https://go.dev/doc/modules/layout) and [module versioning](https://go.dev/doc/modules/version-numbers).
- **Releases:** Follow Go's version-tag and module-path rules, including subdirectory prefixes where applicable; publish a new version rather than changing a released tag. See [publishing modules](https://go.dev/doc/modules/publishing) and [module version tags](https://go.dev/ref/mod#vcs-version).
- **Style and checks:** Format with `gofmt`, use `go vet`, and follow the project's established checks. See [formatting](https://go.dev/doc/effective_go#formatting) and [vet](https://pkg.go.dev/cmd/vet).
- **Errors and concurrency:** Handle returned errors explicitly, wrap them when context helps, and pass cancellation through `context.Context`; give goroutines a clear termination path. See [error wrapping](https://go.dev/blog/go1.13-errors) and [context](https://pkg.go.dev/context).
- **Tests:** Use the standard testing package; run the race detector for relevant concurrent behavior. See [testing](https://pkg.go.dev/testing) and the [race detector](https://go.dev/doc/articles/race_detector).

### Java

Official references: [Java learning resources](https://dev.java/learn/) and [Java SE documentation](https://docs.oracle.com/en/java/javase/).

- **Packages and builds:** Keep public APIs and package boundaries intentional; declare dependencies and supported JDK versions in the build. Use the project's chosen build system, such as [Maven](https://maven.apache.org/guides/) or [Gradle](https://docs.gradle.org/current/userguide/userguide.html), rather than introducing another one without a need.
- **Resources and errors:** Close owned resources with try-with-resources, preserve exception causes, and avoid exposing implementation-specific failures unnecessarily. See [exceptions and resource management](https://dev.java/learn/exceptions/).
- **Models and interfaces:** Use small interfaces and appropriate value types, including records when their semantics fit; do not turn every abstraction into a framework extension. See [records](https://dev.java/learn/records/).
- **Tests and analysis:** Follow the project's test framework and static checks; verify behavior against the supported JDK/toolchain. See the [JUnit User Guide](https://docs.junit.org/current/user-guide/).

### JavaScript

References: the [ECMAScript specification](https://tc39.es/ecma262/), [MDN JavaScript guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide), and [Node.js documentation](https://nodejs.org/api/) for that runtime.

- **Runtime and modules:** State whether code targets browsers, Node.js, or another runtime, and use a consistent module system. Declare package metadata and public entry points deliberately; see [Node.js packages](https://nodejs.org/api/packages.html).
- **Dependencies:** Keep runtime and development dependencies distinct, use the chosen package manager consistently, and retain its lockfile when reproducible installs are required. See [npm package metadata](https://docs.npmjs.com/cli/configuring-npm/package-json).
- **Asynchronous behavior:** Handle rejected promises, cancellation/timeouts where supported, and resource cleanup rather than allowing work to fail silently. See [MDN promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises).
- **Checks:** Apply the project's formatting, linting, and behavior tests in its actual runtime; do not assume browser and server APIs are interchangeable. See the [Node.js test runner](https://nodejs.org/api/test.html) for one runtime-provided option.

### TypeScript

Official references: [TypeScript documentation](https://www.typescriptlang.org/docs/) and [TSConfig reference](https://www.typescriptlang.org/tsconfig/).

- **Contracts:** Prefer strict checking and precise types; narrow `unknown` inputs and avoid unnecessary `any` or assertions that bypass a real check. See [type narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).
- **Runtime boundaries:** Types do not validate external data at runtime. Validate untrusted inputs and handle failures explicitly; apply the [JavaScript runtime practices](#javascript) as well.
- **Builds and packages:** Align module settings, emitted code, declarations, and supported runtime; make the public type surface intentional. See [module guidance](https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html).
- **Validation:** Run the project's type check and behavior tests; compilation alone does not establish correct runtime behavior.

### Rust

Official references: [The Rust Programming Language](https://doc.rust-lang.org/book/), [Rust Reference](https://doc.rust-lang.org/reference/), and [Cargo Book](https://doc.rust-lang.org/cargo/).

- **Packages:** Use focused crates and workspaces where shared development benefits from them; keep exported APIs deliberate. See [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html).
- **Ownership and errors:** Express lifetimes and ownership clearly, return `Result` for recoverable failures, and reserve panics for cases where the contract justifies them. See [error handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html).
- **Safety:** Keep `unsafe` code small and document its required invariants; safe callers must not need undocumented assumptions to avoid undefined behavior. See [unsafe Rust](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html).
- **Checks:** Use the project's `cargo fmt`, Clippy, and tests; review findings rather than applying suggestions blindly. See [Clippy](https://doc.rust-lang.org/clippy/) and [testing](https://doc.rust-lang.org/book/ch11-00-testing.html).

### C

Official references: the [ISO C working group](https://www.open-std.org/jtc1/sc22/wg14/) and the chosen compiler's documentation, such as [GCC](https://gcc.gnu.org/onlinedocs/) or [Clang](https://clang.llvm.org/docs/).

- **Interfaces and builds:** State the supported C standard, platforms, compiler assumptions, dependencies, and public headers. Keep implementation details out of the public interface where possible.
- **Memory and resources:** Make allocation, ownership, buffer sizes, and cleanup explicit; validate lengths and arithmetic used for memory operations. Avoid assuming an unchecked pointer or integer conversion is safe.
- **Errors:** Define consistent return/status and output-parameter contracts, including what remains valid after failure; do not leave resource ownership implicit on error paths.
- **Validation:** Enable appropriate compiler warnings, test boundary cases, and use supported dynamic analysis where useful. See [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html) and [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html); these supplement review and tests rather than prove memory safety.

### C++

References: [C++ standards information](https://isocpp.org/std/the-standard), the chosen standard library/compiler documentation, and the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) as practical guidance rather than the language specification.

- **Resources:** Prefer RAII and value semantics; use standard containers and ownership-aware types instead of manual lifetime management where practical. See [resource-management guidance](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-resource).
- **Contracts:** Keep ownership, lifetimes, exception guarantees, and thread-safety expectations clear at public boundaries; do not expose raw owning pointers or implementation details accidentally.
- **Builds:** Declare the supported language standard, compiler/ABI constraints, and dependencies; follow the project's build tooling. See [CMake documentation](https://cmake.org/documentation/) when CMake is used.
- **Checks:** Apply compiler warnings, tests, and suitable sanitizers/static analysis for the supported toolchain. Avoid complexity in templates or inheritance unless it solves a real problem.

### Shell

Official references: [Bash Reference Manual](https://www.gnu.org/software/bash/manual/) and [ShellCheck](https://www.shellcheck.net/).

- Declare the intended shell, quote expansions, and handle failures explicitly; do not assume Bash features are portable to `sh`. See [quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html) and [exit status](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html).
- Keep scripts focused and validate them with the project's syntax and static checks; move substantial reusable logic into a suitable package rather than growing an opaque shell framework.

### Ansible

Official references: [Ansible documentation](https://docs.ansible.com/ansible/latest/).

- **Packages:** Use focused roles and group related roles, modules, and plugins in a collection when they form one distribution. See [role layout](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure) and [collection structure](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_structure.html).
- Prefer idempotent modules, explicit host targeting, documented variables and defaults, and handlers for change-triggered actions. See [playbooks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html) and [handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html).
- Validate with the project's linting and safe test targets; support [check and diff modes](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html) where modules allow them, without treating a dry run as proof of runtime behavior.

### Terraform

Official references: [Terraform documentation](https://developer.hashicorp.com/terraform/docs).

- **Packages:** Give modules focused inputs, outputs, and responsibilities; follow the [standard module structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure) where appropriate.
- Declare compatible provider constraints, review plans before applying, and protect state and secrets. See [provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements) and [sensitive data in state](https://developer.hashicorp.com/terraform/language/state/sensitive-data).
- Use formatting, validation, and meaningful module tests where applicable; tests that apply infrastructure need an approved target. See [Terraform tests](https://developer.hashicorp.com/terraform/language/tests).

### Helm

Official references: [Helm documentation](https://helm.sh/docs/).

- **Packages:** Follow the [chart structure](https://helm.sh/docs/topics/charts/#the-chart-file-structure); put configurable defaults in `values.yaml` and reusable named templates in `_helpers.tpl`.
- Keep chart `version` distinct from application `appVersion`, and version chart changes. See [Chart.yaml](https://helm.sh/docs/topics/charts/#the-chartyaml-file).
- Lint and render charts before installation; test against approved clusters when runtime validation is needed. See [chart best practices](https://helm.sh/docs/chart_best_practices/) and [chart tests](https://helm.sh/docs/topics/chart_tests/).

### Docker

Official references: [Docker documentation](https://docs.docker.com/) and [Dockerfile reference](https://docs.docker.com/reference/dockerfile/).

- **Packaging:** Keep the Dockerfile as the build source of truth, use a minimal appropriate base, and use multi-stage builds when they reduce runtime content. See [build best practices](https://docs.docker.com/build/building/best-practices/).
- Run as a non-root user where supported, exclude unnecessary context with `.dockerignore`, and pin base versions or digests with a deliberate update process.
- Pass build credentials through [BuildKit secrets](https://docs.docker.com/build/building/secrets/), never ordinary build arguments or image environment variables.
- Publish immutable release identifiers; do not rely on `latest` for reproducibility. See [image digests](https://docs.docker.com/dhi/core-concepts/digests/).

### Configuration and markup

- **YAML:** Use the owning tool's schema and validation; keep configuration readable and avoid relying on ambiguous implicit types. See the [YAML specification](https://yaml.org/spec/1.2.2/).
- **Markdown:** Keep navigation and links current and document for the reader rather than reproducing theory. See [CommonMark](https://spec.commonmark.org/) and the local [Documentation Guidelines](../../DOCUMENTATION.md).
