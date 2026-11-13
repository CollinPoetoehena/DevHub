# DevHub Shared Repository Guidelines

`devhub-guidelines-core` distributes shared repository standards through [APM](https://microsoft.github.io/apm/). Its `.apm/instructions/` directory is the authoring source; [`apm.yml`](apm.yml) declares the pinned instruction dependencies.

Repositories adopt this package independently of any local development workflow. It contains no agents, skills, or stack-specific maps. The [`development-core`](../development-core/README.md) package is a separate choice for local agents and skills; opt-in `development-*` stack packages own their scoped instruction maps.

## Guidelines

The package contains common coding, security, testing, documentation, Git, GitHub Actions, and AI-customization guidance. These are host-facing instruction files using the native filenames and frontmatter required by Copilot.

Guidelines are shared defaults. Repository configuration, owning documentation, and `AGENTS.md` refine or override them; stack-specific guidance adds scoped technology defaults. Copilot calls these files instructions and Claude calls them rules; the package retains the host-required filenames and frontmatter. Surface unresolved conflicts rather than assuming a universal host precedence.

## Consumption

Declare `CollinPoetoehena/DevHub/packages/apm/guidelines-core` in a participating repository's APM manifest independently of the local development setup. The consumer owns installation scope, updates, local instructions, and collision review. The [APM guide](../README.md#repository-setup) explains the separate package families and host verification.

## Validation

Validate this source with `apm compile --validate --local-only` from this package directory. Static source validation confirms package structure and references; it does not install the package or establish host discovery or runtime behavior.

Changes are recorded in the [changelog](CHANGELOG.md).
