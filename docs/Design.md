# Design

TODO: update this with new setup with homelab included and the development hub for me, etc.

DevHub started as a monorepo containing all reusable components—Terraform modules, Ansible roles, and more. However, this approach has a practical limitation: Git does not support cloning only a subdirectory of a repository. Cloning the repo always pulls everything, which is wasteful and inconvenient when a consumer only needs one component type.

To address this, each component type now lives in its own dedicated repository. This is also the industry best practice for distributing reusable components/packages, and offers several benefits:

- Consumers clone only what they need, nothing more.
- Each repository has its own focused scope, versioning and release cycle — consumers can pin to a specific version (tag/ref) and upgrade independently.
- Follows the standard conventions of each ecosystem (e.g. Terraform Registry module naming, Ansible Galaxy, Helm OCI registries), which typically expect one component per repository.
- Each repository can have its own focused CI/CD pipeline, access controls, and issue tracker, etc. without overlap or noise from unrelated components.
- Avoids accidental coupling: a breaking change in one component does not affect others.

DevHub remains the central index—this README links to all the individual repositories so they are easy to discover. In addition, dev-hub centralizes all shared publishing logic: GitHub Actions workflows, helper scripts, and any other CI/CD tooling used to release or validate components. Individual repositories reference or reuse these centrally managed pipelines rather than duplicating them.