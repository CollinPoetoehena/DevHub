# DevHub Architecture Decision Records

These records capture significant repository-wide decisions and their trade-offs. Current structure and placement guidance remains in [Project Structure](../ARCHITECTURE.md) and [Guidelines](../GUIDELINES.md).

## Decisions

| ADR | Decision |
|---|---|
| [Keep DevHub as a bounded monorepo](DEVHUB-MONOREPO.md) | Keep related shared development resources together while placing independently operated projects in their own repositories. |
| [Separate the homelab repositories from DevHub](SEPARATE-HOMELAB-REPOSITORIES.md) | Keep the homelab's public and private project material within its own repository boundary. |
| [Set release boundaries by managed contract](RELEASE-BOUNDARIES-BY-MANAGED-CONTRACT.md) | Version and release the artifacts consumers use together, independently of repository and directory boundaries. |
