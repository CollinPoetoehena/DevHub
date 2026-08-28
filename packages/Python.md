# Python

Reusable [Ansible](https://docs.ansible.com/) roles and playbooks, used for configuration management and application deployment.

Each role lives in its own dedicated repository. This file serves as the index and reference for all Ansible roles, and documents conventions shared across them.

## Dev-Hub

This repository ([dev-hub](https://github.com/CollinPoetoehena/dev-hub)) is the central reference for all Python packages, see [README.md](README.md) for the full design and index of all component types.

## Structure

All packages use the [src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout) required by setuptools:

```
<package_root>/           # e.g. devhub_<name>/
├── pyproject.toml
├── README.md
└── src/
    └── devhub_<name>/
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
name = "devhub_<name>"       # underscore — publishes as devhub-<name>
version = "1.0.0"
description = "Short description of the package."
requires-python = ">=3.8"
dependencies = ["requests>=1.0.0", ...]  # dependencies
readme = "README.md"

[project.urls]
Homepage = "https://github.com/CollinPoetoehena/<package_root>"

[tool.setuptools.packages.find]
where = ["src"]
include = ["devhub_<name>*"]   # matches package + all sub-packages
```

> **Naming:** Use underscores (e.g. `devhub_<name>`) in `pyproject.toml`. Artifactory automatically normalises to hyphens (e.g. `devhub-<name>`) on publish. Consumers install with either form via `pip`.

### Dependencies

- Declare dependencies in `pyproject.toml` under `[project] dependencies`.
- Use **broad version ranges** (`>=x.y`) rather than pinned versions. The consuming project pins its own versions.
- Internal packages (e.g. `dev_hub_<name>`) are listed as dependencies using their underscore name and a minimum version: `"dev_hub_<name>>=1.0.0"`.
- Do **not** pin transitive dependencies inside the package itself to avoid conflicts and versioning issues (e.g. a package requiring a specific version of another internal package that is already pinned by the consuming project which could lead to version conflicts).


## `__init__.py` — Package Initialisation

### What it does

A directory with an `__init__.py` file is a **Python package**. When Python imports a package (e.g. `from dev_hub_<name>.clients.k8s import K8sPodClient`), it runs `__init__.py` in that directory first. Whatever names exist in that module after it runs become the package's public API — callers can import them directly from the package instead of from the individual module files.

A directory **without** `__init__.py` is a namespace package (PEP 420): importable, but it exposes nothing by default and behaves differently from a regular package. Always add `__init__.py` to every directory that should be importable as a package.

### The two patterns

The confusion between the two patterns is that both look the same when you write an import statement, because **importing a package and accessing its contents are two separate things**. When you write `import dev_hub_<name>.clients.k8s`, Python loads and runs `__init__.py` in every directory along the path — that always succeeds. But what you can *do afterwards* depends entirely on whether `__init__.py` re-exported anything.
#### Pattern 1 — Marker only
The marker only pattern is used for internal grouping directories that are not part of the public import surface:
```python
# dev_hub_<name>/clients/__init__.py is empty
import dev_hub_<name>.clients           # ✅ works — Python sees a package
dev_hub_<name>.clients.K8sPodClient    # ❌ AttributeError — nothing was exposed
```
The directory is a package container. Nothing inside it is accessible as an attribute; callers must go deeper themselves:
```python
from dev_hub_<name>.clients.k8s import K8sPodClient  # must spell out the full path
```
#### Pattern 2 — Re-export facade
> A *facade* is a design pattern where one interface hides the complexity behind it. Here, `__init__.py` acts as the facade: it presents a clean, stable set of names to callers while the actual implementation can live in any number of internal files. Callers never need to know which file a class comes from — they only see the package surface.

The Re-export facade pattern is used for public API directories:
```python
# dev_hub_<name>/clients/k8s/__init__.py
from dev_hub_<name>.clients.k8s.exceptions import *
from dev_hub_<name>.clients.k8s.k8s_pod_client import *
```
```python
import dev_hub_<name>.clients.k8s
dev_hub_<name>.clients.k8s.K8sPodClient  # ✅ works — __init__ created this attribute
from dev_hub_<name>.clients.k8s import K8sPodClient  # ✅ clean, stable import
```
#### Comparison
| Behaviour | Marker only | Re-export facade |
|---|---|---|
| `import dev_hub_<name>.clients.k8s` | ✅ | ✅ |
| `dev_hub_<name>.clients.k8s.K8sPodClient` | ❌ `AttributeError` | ✅ |
| Callers need to know internal file layout | ✅ yes | ❌ no |
| Stable API survives internal refactoring | ❌ | ✅ |

Think of the two patterns as:
- **Empty `__init__.py`** → "this is a package container"
- **Re-exporting `__init__.py`** → "this is the public interface"

The practical consequence for a team: without re-exports, callers must know the internal file structure (`from dev_hub_<name>.clients.k8s.k8s_pod_client import K8sPodClient`). If you later rename or reorganise that file, every caller breaks. With a re-export facade, callers only know the package name (`from dev_hub_<name>.clients.k8s import K8sPodClient`), and internal refactoring is safe as long as `__init__.py` keeps exporting the same names.

### `*` imports and `__all__`

`from module import *` imports every name that does not start with `_`, **unless** the module defines `__all__`. Always define `__all__` in any module that is re-exported via `*`, to make the public API explicit and prevent internal helpers from leaking into the package namespace:

```python
# k8s_pod_client.py
__all__ = ["K8sPodClient"]
```

## Naming Convention

| Context | Convention | Example |
|---|---|---|
| Python package name (import) | `devhub_<name>` | `devhub_<name>` |
| Published package name (pip/Artifactory) | `devhub-<name>` | `devhub-<name>` |
| Repository folder | `devhub_<name>/` | `devhub_<name>/` |

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
# <package-name>

> Part of [dev-hub/Python](https://github.com/CollinPoetoehena/dev-hub/blob/main/packages/Python.md) — see that file for conventions, structure guidelines, and the full package index.

<Short description of what this package provides.>

## Requirements

List any dependencies or prerequisites here.

## Usage

Installation and usage instructions for the Python package:
```bash
pip install devhub-<name>
```

Then import and use it in your Python code:
```python
import devhub_<name>

# Example usage
devhub_<name>.<function_or_class>()
```
