# DevHub Tools

Automation shared across my personal projects. Each tool's README owns its design, configuration, commands, and operational safeguards; the [tool ADR index](adrs/README.md) links to durable decisions kept with their owning tools.

- [`repo/`](repo/README.md): repository fleet management. Terraform owns repository settings and protection from one inventory; the central workflow applies guarded settings plans and uses `repo-fleet` for combined template/APM pull requests.

Project-specific operational tooling stays in its owning project. Add further tools here only for concrete recurring needs.
