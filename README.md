# DevHub
DevHub: My central development hub — a personal lab and reference repository for home lab documentation, reusable packages, and shared tooling across my projects.

DevHub brings together my home lab (a hands-on learning environment for DevOps, Kubernetes, networking, and infrastructure automation) and my reusable packages (Terraform modules, Ansible roles, Helm charts, etc.) under one roof. It serves as both the central index and the documentation/code repository for everything I build, learn, and experiment with. While primarily a personal hub, it is publicly available for anyone who finds these resources useful.

---

## Table of Contents
1. [Documentation](#documentation)
2. [DevHub Design](#devhub-design)
3. [Home Lab](./homelab/README.md)
4. [Packages](./packages/README.md)

--- 

## Documentation
The documentation in `DevHub` is intentionally kept minimal, with the main documentation for `DevHub` in general limited to this README.md file and further documentation provided by each part of the project (e.g. `homelab`, `packages` all have their own documentation (see [DevHub Design](#devhub-design) below)).

---

## DevHub Design
DevHub is my central development hub — bringing together my personal home lab, reusable packages, and shared CI/CD tooling under one roof. It serves as both an index and a documentation/code repository for everything I build, learn, and experiment with. The design is split into two main areas: the home lab and the packages:
1. **Home Lab:** A hands-on learning environment for DevOps, Kubernetes, networking, and infrastructure automation. The home lab is where I experiment with new tools, learn new concepts, and build out my skills in a practical way. It includes detailed documentation on the setup and architecture decisions. See the [Home Lab Design](./homelab/README.md#home-lab-design) section for more details.
2. **Packages:** A collection of reusable components, including Terraform modules, Ansible roles, Helm charts, and more. Each component type lives in its own dedicated repository for better modularity and versioning. The packages section also centralizes all shared publishing logic (e.g. GitHub Actions workflows) that individual repositories can reference. See the [Packages Design](./packages/README.md#packages-design) section for more details.

TODO: project structure is separate parts have their own folder, such as `packages` and `homelab`, etc., and they contain their own documentation and code, etc. This is because they are really separate parts but still part of the larger DevHub project, so they should be organized in a way that reflects that separation but still makes it easy to navigate and find the relevant information.

--- 