# Changelog

## Unreleased

### Documentation

- Document the package as `development-python`, its `development-core` dependency, and independent adoption of shared `guidelines-core`.

## [0.1.0] - 2026-11-06

### Added

- Python instruction with toolchain defaults, mandatory rules, and validation commands on top of the common instructions, including the Python rules previously in `devhub-common`.
- `python` skill with patterns and testing references adapted from ECC, and an authored tooling reference for uv, ruff, mypy, pytest, and pip-audit.
- `fastapi` and `django` framework skills with patterns references adapted from ECC.
- Dependency on `devhub-common`, so installing this package always installs the common agents and standards.
