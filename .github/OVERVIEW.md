# Shared GitHub Customizations

> This file is named `OVERVIEW.md` rather than `README.md` because GitHub gives a `.github/README.md` precedence over the repository-root `README.md` on the repository home page. Using a different filename keeps the root README as the repository's landing page while this file provides an overview of the shared GitHub customizations.

This folder contains generic automation and AI workflows that can be reused across DevHub projects and other repositories. Keep project-specific implementation and settings in the project that owns them; keep reusable guidance and workflows here.

- [Reusable GitHub Actions workflows](./workflows/README.md) describes how to call workflows from other repositories and the current workflow's status.
- [Reusable Agent Skills](./skills/README.md) explains how to use the generic skills and adapt them to a repository.
- The [DevHub README](../README.md#what-belongs-in-devhub) explains why these shared resources live in DevHub while larger project implementations, such as the homelab, live in separate repositories.

These files are examples and shared starting points, not a requirement that every project use the same workflow. Review inputs, permissions, secrets, and security implications in the consuming repository before adopting them.