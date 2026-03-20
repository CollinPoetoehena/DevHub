# DevHub
DevHub: A central repository for storing and sharing reusable development resources, libraries, modules, and tools across multiple languages and technologies.

While DevHub primarily serves as a hub for my personal development projects, it is publicly available to benefit others who may find these resources useful and wish to access them easily without necessary credentials.

## Table of Contents
1. [Documentation](#documentation)
2. [Design](#design)
3. [Project Structure](#project-structure)

## Documentation
The documentation is intentionally kept minimal, with the main documentation limited to this README.md file, and specific files per type in this repository (e.g. Terraform modules README.md, Ansible roles README.md, etc.). 

## Design
DevHub is a central repository (monorepo) for all reusable components I use in my projects—including Terraform modules, Ansible roles, and more. This approach is especially handy for my personal projects, and offers several benefits:

- Centralized management of all reusable code.
- Easier maintenance and updates for solo development.
- Simplified structure—just one repository to track.
- Keeps other project repositories clean, without mixing in reusable logic or modules.
- Allows all logic for publishing packages (such as scripts, CI/CD, etc.) to be managed centrally, avoiding repetition (DRY) and keeping things simple (KISS).

In enterprise environments, it is common to split reusable components into separate repositories per type (e.g., Ansible roles, Terraform modules) or even individual repositories per package/component. However, since this is mainly for my personal projects, I keep everything together in this repository for convenience.

If any component grows too large or needs to be separated for other reasons, it can always be split into its own dedicated repository.

## Project Structure
The project structure is organized by component type, with each type having its own directory:

TODO: make this here later, also add separate for /scripts wich has reusable scripts for publishing packages, CI/CD, etc., and the GitHub Actions folder for publishing workflows, etc. 