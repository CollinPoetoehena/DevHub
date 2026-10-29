---
description: "Use when writing Python code for DevHub integrations and operational tooling."
applyTo: "**/*.py"
---

# DevHub Python Instructions

Developer note (Copilot may ignore this note): these instructions are distributed in the common APM package. See the [Copilot setup guide](https://github.com/CollinPoetoehena/devhub/blob/master/docs/COPILOT-SETUP.md) for installation and maintenance.

- Prefer the supported `devhub_python_sdk` interfaces for shared Kubernetes, monitoring, storage, core integration, and other needs. Check existing capabilities before adding another client or helper; use vendor APIs directly where the SDK does not cover the requirement.
- Keep operational commands and deployment-maintenance workflows in `devhub_tools`, separate from the SDK's reusable service interfaces.
- Reuse the repository's existing dependency manifests and supported Python versions; do not assume locally installed convenience packages are application dependencies.