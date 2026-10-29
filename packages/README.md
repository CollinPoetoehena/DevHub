# DevHub Packages

Reusable packages for my personal projects. Each package owns its native metadata, supported interface, dependencies, and validation; sharing this repository does not require one version or runtime.

The Python and Go SDKs are foundations without vendor integrations. Shared AI customizations live in the common APM package; the homelab package is a placeholder. [DevHub architecture](../docs/ARCHITECTURE.md) records repository and release boundaries; technical background belongs in official ecosystem documentation.

---

## Table of Contents

- [Packages](#packages)
- [Decisions and boundaries](#decisions-and-boundaries)
- [Development and releases](#development-and-releases)

---

## Packages

| Package | Contract |
|---|---|
| [Common APM](apm/common/README.md) | Shared engineering agents, instructions, and skills; local dependency of the [root manifest](../apm.yml) |
| [Homelab APM](apm/homelab/README.md) | Placeholder for homelab-specific AI guidance |
| [Python SDK](python/sdk/README.md) | Distribution `devhub-python-sdk`, import `devhub_python_sdk`; Python 3.12+ |
| [Go SDK](go/sdk/README.md) | Module `github.com/CollinPoetoehena/devhub-sdks/go`; Go 1.25+ |
| [Python repository manager](python/tools/repo_manager.py) | Placeholder script; repository-management automation is not implemented |

The SDK identifiers above match their current manifests, including the older `devhub-sdks` Go module path. Their presence does not imply publication or a completed migration of installation and release instructions into DevHub.

---

## Decisions and boundaries

- **One maintainer, related work:** Keeping packages together avoids duplicated settings and coordinated changes across repositories. Split only for a real ownership, access, consumer, or release boundary.
- **Depth before language coverage:** Python fits my existing automation experience; Go broadens my infrastructure-tooling experience. Add another language only for a demonstrated consumer need, not a language checklist.
- **Native SDKs, independent contracts:** Keep focused domains within one Python distribution and one Go module for now. Do not mechanically translate APIs or promise equivalent features and versions. Use the [Python tutorial](https://docs.python.org/3/tutorial/) and [Effective Go](https://go.dev/doc/effective_go) for language idioms.
- **Reuse before abstraction:** Prefer supported vendor clients; extract recurring domain behavior and reliability contracts, not a shadow vendor API. Add integrations from real consumer needs, without speculative interfaces or cross-language frameworks.
- **Applications own operations:** Provisioning, deployment, credentials, environment configuration, business decisions, and adoption of package updates stay with consuming projects. Private homelab configuration does not belong here.

---

## Development and releases

Follow the owning package README and manifest for local commands. The [Python metadata](python/sdk/pyproject.toml) configures Hatchling, Ruff, mypy, and pytest; [Go metadata](go/sdk/go.mod) declares its native module.

For packaging mechanics, use the [Python Packaging User Guide](https://packaging.python.org/en/latest/overview/) and [Go module documentation](https://go.dev/doc/modules/developing). Add domain tests with each integration, including failure paths and resource ownership; live homelab tests require explicit opt-in and an approved target.

The repository's [publishing workflow](../.github/workflows/publish.yml) is a placeholder, not working package CI or publication. Before releasing, reconcile each SDK's older installation/release guidance with its actual location, select a license and artifact destination, and define validation and tag ownership. Independent Go releases must follow the [module tag rules](https://go.dev/ref/mod#vcs-version); do not infer a tag prefix from this directory index.
