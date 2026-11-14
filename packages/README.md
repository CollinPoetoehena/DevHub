# DevHub Packages

Reusable packages for my personal projects. Each package owns its native metadata, supported interface, dependencies, and validation; sharing this repository does not require one version or runtime.

Related packages stay together for coordinated maintenance, not a shared runtime or mandatory lockstep release. The [release-boundary ADR](../docs/adrs/RELEASE-BOUNDARIES-BY-MANAGED-CONTRACT.md) records the release rationale; [package guidelines](../docs/GUIDELINES.md#placing-packages-and-components) cover placement.

---

## Package index

| Area | Purpose and current state |
|---|---|
| [Python](python/README.md) | Design and setup guidance for future Python packages; no implemented packages yet. |
| [Go](go/README.md) | Design and setup guidance for future Go modules and packages; no implemented modules yet. |
| [Helm](helm/README.md) | Placeholder for future charts; no chart implementation yet. |
| [APM](apm/README.md) | Eight source packages: independent shared `guidelines-core`, local `development-core`, and six opt-in `development-*` stacks. [ADRs](apm/docs/adrs/README.md) own decisions and [concepts](apm/docs/CONCEPTS.md) explain terminology; source readiness does not establish installation, synchronization, or host discovery. |

Each area README is the entry point for its ecosystem. As implementations are added, keep each independently consumed package's native manifest, dependencies, tests, and usage/release documentation with its source. Use small, cohesive packages with narrow public contracts; introduce shared dependencies only for demonstrated reuse.
