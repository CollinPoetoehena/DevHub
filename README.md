# DevHub
DevHub: My central development hub — a personal lab and reference repository for home lab documentation, reusable packages, and shared tooling across my projects.

DevHub brings together my home lab (a hands-on learning environment for DevOps, Kubernetes, networking, and infrastructure automation) and my reusable packages (Terraform modules, Ansible roles, Helm charts, etc.) under one roof. It serves as both the central index and the documentation/code repository for everything I build, learn, and experiment with. While primarily a personal hub, it is publicly available for anyone who finds these resources useful.

The name reflects what the project is:
- **Dev** — short for *development* and *DevOps*: the main focus areas of this repository. Everything here is about building, automating, and learning through hands-on development work.
- **Hub** — a central point that connects everything together. Like a hub in a wheel, all parts of my personal development work (home lab, reusable packages, shared tooling, etc.) connect back to this one place. It's the single source of truth and starting point for navigating all of it.

---

## Table of Contents
1. [DevHub Design & Documentation](#devhub-design--documentation)
2. [Home Lab](./homelab/README.md)
3. [Packages](./packages/README.md)
4. [Scripts](#scripts)

--- 

## DevHub Design & Documentation
DevHub is my central development hub — bringing together my personal home lab, reusable packages, and shared CI/CD tooling under one roof. It serves as both an index and a documentation/code repository for everything I build, learn, and experiment with. The design is split into two main areas: the home lab and the packages:
1. **Home Lab:** A hands-on learning environment for DevOps, Kubernetes, networking, and infrastructure automation. The home lab is where I experiment with new tools, learn new concepts, and build out my skills in a practical way. It includes detailed documentation on the setup and architecture decisions. See the [Home Lab Design](./homelab/README.md#home-lab-design) section for more details.
2. **Packages:** A collection of reusable components, including Terraform modules, Ansible roles, Helm charts, and more. Each component type lives in its own dedicated repository for better modularity and versioning. The packages section also centralizes all shared publishing logic (e.g. GitHub Actions workflows) that individual repositories can reference. See the [Packages Design](./packages/README.md#packages-design) section for more details.

Each part of DevHub lives in its own top-level folder (e.g. `homelab/`, `packages/`) and is treated as a self-contained unit with its own documentation and code. This keeps concerns separated — the home lab setup has nothing to do with the Terraform module publishing logic, for example — while still being part of the larger DevHub project. The root `README.md` (this file) acts as the single entry point and index, making it easy to navigate to the right part without everything being mixed together.

The documentation in `DevHub` is intentionally kept minimal, with the main documentation for `DevHub` in general limited to this README.md file and further documentation provided by each part of the project (e.g. `homelab`, `packages` all have their own documentation, as explained above).

---

## Scripts
The `scripts/` folder contains shared utility scripts used across the project. These are standalone tools that don't belong to a specific sub-project.

| Script | Description |
|--------|-------------|
| `load_config.sh` | Shared configuration loader — sources project-wide variables and utility functions. Other scripts source this file to get the project root path and common settings. |
| `convert_md_to_docx.py` | Converts a Markdown file to a Word (.docx) document. Handles headings, tables, code blocks, inline formatting, lists, and blockquotes. Requires `python-docx` (`pip install python-docx`). Usage: `python3 scripts/convert_md_to_docx.py <input.md> [output.docx]`. |
| `terraform/` | Terraform scripts — contains various Terraform configurations and helper scripts for managing infrastructure. |

---