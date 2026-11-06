# DevHub Packages

Reusable packages for my personal projects. Each package owns its native metadata, supported interface, dependencies, and validation; sharing this repository does not require one version or runtime.

Related packages stay together for coordinated maintenance, not a shared runtime or mandatory lockstep release. [DevHub architecture](../docs/ARCHITECTURE.md#release-and-versioning-units) owns the repository and release rationale; [package guidelines](../docs/GUIDELINES.md#placing-packages-and-components) cover placement.

---

## Package index

| Area | Purpose and current state |
|---|---|
| [Python](python/README.md) | Design and setup guidance for future Python packages; no implemented packages yet. |
| [Go](go/README.md) | Design and setup guidance for future Go modules and packages; no implemented modules yet. |
| [Helm](helm/README.md) | Placeholder for future charts; no chart implementation yet. |
| [APM](apm/README.md) | Shared AI customization design and setup, with the active [common package](apm/common/README.md), placeholder stack packages for [Python](apm/python/README.md), [Java](apm/java/README.md), [Go](apm/go/README.md), and [Rust](apm/rust/README.md), and a [homelab placeholder](apm/homelab/README.md). |

Each area README is the entry point for its ecosystem. As implementations are added, keep each independently consumed package's native manifest, dependencies, tests, and usage/release documentation with its source. Use small, cohesive packages with narrow public contracts; introduce shared dependencies only for demonstrated reuse.
