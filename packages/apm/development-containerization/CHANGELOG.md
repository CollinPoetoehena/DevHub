# Changelog

## Unreleased

### Documentation

- Document the package as `development-containerization`, its `development-core` dependency, and independent adoption of shared `guidelines-core`.

## [0.1.0] - 2026-11-06

### Added

- Docker instruction with the DevHub Dockerfile defaults previously in `devhub-common`, plus image, Compose, and validation rules.
- Kubernetes and Helm instructions with mandatory rules and validation commands on top of the common instructions.
- `docker` and `kubernetes` skills with references adapted from ECC and awesome-copilot.
- `helm` skill with patterns and testing references authored from the official Helm documentation, requiring a values schema generated from `@schema` annotations with helm-schema and helm-unittest tests for every chart.
- Dependency on `devhub-common`, so installing this package always installs the common agents and standards.
