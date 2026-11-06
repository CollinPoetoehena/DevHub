# Changelog

## [0.1.0] - 2026-11-06

### Added

- Ansible instruction with the DevHub Ansible rules previously in `devhub-common`, plus lint, naming, privilege, and validation rules, and matching of `ansible/` directories.
- Terraform and Bicep instructions with mandatory rules and validation commands on top of the common instructions.
- `ansible`, `terraform`, and `bicep` skills with patterns references adapted from awesome-copilot.
- Dependency on `devhub-common`, so installing this package always installs the common agents and standards.
