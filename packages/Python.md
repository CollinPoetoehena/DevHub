# Python

Reusable [Ansible](https://docs.ansible.com/) roles and playbooks, used for configuration management and application deployment.

Each role lives in its own dedicated repository. This file serves as the index and reference for all Ansible roles, and documents conventions shared across them.

For the official Python packaging reference, see [Python Packaging Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## DevHub

This repository ([DevHub](https://github.com/CollinPoetoehena/DevHub)) is the central reference for all Python packages, see [README.md](README.md) for the full design and index of all component types.

## Structure

All packages use the [src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout) required by setuptools:

```
<package_root>/           # e.g. devhub_python_<name>/
├── pyproject.toml
├── README.md
└── src/
    └── devhub_python_<name>/
        ├── __init__.py   # re-exports public API
        ├── module_a.py
        ├── module_b.py
        └── models/
            ├── __init__.py
            └── some_model.py
```

- The `src/` directory prevents accidental imports of the local source when the installed package is expected.
- Each package must define its `__init__.py` files, see [Package Initialisation](#__init__py--package-initialisation) for details on how to structure `__init__.py` and the two patterns for package initialisation.

### pyproject.toml

Every package contains a `pyproject.toml` at its root. The minimal required sections are:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "devhub_python_<name>"       # underscore — publishes as devhub-<name>
version = "1.0.0"
description = "Short description of the package."
requires-python = ">=3.8"
dependencies = ["requests>=1.0.0", ...]  # dependencies
readme = "README.md"

[project.urls]
Homepage = "https://github.com/CollinPoetoehena/<package_root>"

[tool.setuptools.packages.find]
where = ["src"]
include = ["devhub_python_<name>*"]   # matches package + all sub-packages
```

> **Naming:** See [Naming Convention](#naming-convention)

### Dependencies

- Declare dependencies in `pyproject.toml` under `[project] dependencies`.
- Use **broad version ranges** (`>=x.y`) rather than pinned versions. The consuming project pins its own versions.
- Internal packages (e.g. `devhub_python_<name>`) are listed as dependencies using their underscore name and a minimum version: `"devhub_python_<name>>=1.0.0"`.
- Do **not** pin transitive dependencies inside the package itself to avoid conflicts and versioning issues (e.g. a package requiring a specific version of another internal package that is already pinned by the consuming project which could lead to version conflicts).

## Python Reference & Best Practices

See [Python Reference & Best Practices](../reference/python/README.md).

## Naming Convention

See [DevHub Global Naming Convention](./README.md#repositories--naming-conventions) for the overall naming rules applied across all DevHub components. Specifically for Python packages, should use underscores in the package name (e.g. `devhub_python_<name>`) rather than hyphens (this is the convention for Python package names).

## Usage

Each package repository contains its own README with usage instructions. The general pattern for referencing a package via `pip`:

TODO: later add here how to publish (e.g. via twine, etc.)!

## Python Packages

| Package | Repository | Description |
|---------|------------|-------------|
| _(none yet)_ | | Python Packages will be listed here as they are added |

## README Template

When creating a new package repository, use the following template as the starting point for its `README.md`:

```markdown
# <package-name following the naming convention>

> Part of [DevHub/Python](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/Python.md) — see that file for conventions, structure guidelines, and the full package index.

<Short description of what this package provides.>

## Requirements

List any dependencies or prerequisites here.

## Usage

Installation and usage instructions for the Python package:
```bash
pip install <name>
```

Then import and use it in your Python code:
```python
import devhub_python_<name>

# Example usage
devhub_python_<name>.<function_or_class>()
```
