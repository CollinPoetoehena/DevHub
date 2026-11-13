# ADR TODO: Synchronization of Customization Packages

## Status

Proposed: TODO only. The user requested the direction below, not an implemented or fully designed synchronization mechanism.

---

## TODO

- **Development setup**: Design an install script and `.bashrc` integration to keep the team members' selected local setup directories continuously synchronized with the development-setup source repository/package, without copying generic agents and skills into every repository. Reuse [APM distribution](DISTRIBUTION.md) to keep package content up to date rather than write another package manager. Define the recurring trigger: [`.bashrc` runs at interactive non-login shell startup](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html), not continuously by itself.
- **Repository instructions**: Design [GitHub Actions](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows) automation that updates the instruction package in participating repositories using APM and opens a pull request for review, rather than silently changing repository guidance.

Keep this as a TODO until triggers, ownership, update policy, permissions, collision handling, and discovery checks are agreed. [Package design](PACKAGE-DESIGN.md) owns the destinations and boundaries. Do not create scripts, shell configuration changes, workflows, or background services as part of this documentation task.

---

## Date

2026-11-13
