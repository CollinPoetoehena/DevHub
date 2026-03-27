# DevHub
DevHub: A central hub referencing reusable development resources, libraries, modules, and tools across multiple languages and technologies.

While DevHub primarily serves as a hub for my personal development projects, it is publicly available to benefit others who may find these resources useful and wish to access them easily without necessary credentials.

## Table of Contents
1. [Documentation](#documentation)
2. [Design](#design)
3. [Versioning](#versioning)
4. [Repositories](#repositories)

## Documentation
The documentation is intentionally kept minimal, with the main documentation limited to this README.md file and the individual repository .md files linked below in the [Repositories](#repositories) section.

## Design
DevHub started as a monorepo containing all reusable components—Terraform modules, Ansible roles, and more. However, this approach has a practical limitation: Git does not support cloning only a subdirectory of a repository. Cloning the repo always pulls everything, which is wasteful and inconvenient when a consumer only needs one component type.

To address this, each component type now lives in its own dedicated repository. This is also the industry best practice for distributing reusable components/packages, and offers several benefits:

- Consumers clone only what they need, nothing more.
- Each repository has its own focused scope, versioning and release cycle — consumers can pin to a specific version (tag/ref) and upgrade independently.
- Follows the standard conventions of each ecosystem (e.g. Terraform Registry module naming, Ansible Galaxy, Helm OCI registries), which typically expect one component per repository.
- Each repository can have its own focused CI/CD pipeline, access controls, and issue tracker, etc. without overlap or noise from unrelated components.
- Avoids accidental coupling: a breaking change in one component does not affect others.

DevHub remains the central index—this README links to all the individual repositories so they are easy to discover. In addition, dev-hub centralizes all shared publishing logic: GitHub Actions workflows, helper scripts, and any other CI/CD tooling used to release or validate components. Individual repositories reference or reuse these centrally managed pipelines rather than duplicating them.

## Versioning

Each repository follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`) and is released via Git tags (e.g. `v1.0.0`). Versions are independent per repository — a breaking change in the Terraform modules does not force a version bump on Helm charts or Ansible roles.

### Creating a release

```bash
git tag v1.0.0
git push origin v1.0.0
```

Pin to a tag to get a stable, reproducible reference. Each ecosystem uses the Git tag slightly differently, see the specific instructions for each type below.

### Version bump guidelines

| Change | Version bump |
|--------|--------------|
| Breaking change to inputs/outputs/interface | `MAJOR` |
| New backwards-compatible feature or resource | `MINOR` |
| Bug fix, doc update, internal refactor, etc. | `PATCH` |

## Repositories

| Component | Index | Description |
|-----------|-------|-------------|
| Terraform | [Terraform.md](Terraform.md) | Reusable Terraform modules (IaC) |
| Ansible | [Ansible.md](Ansible.md) | Reusable Ansible roles and playbooks |
| Helm | [Helm.md](Helm.md) | Reusable Helm charts |
| _(future)_ | | Add more here as needed |