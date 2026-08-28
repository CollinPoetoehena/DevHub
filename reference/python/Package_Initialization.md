# `__init__.py` — Package Initialisation

Package initialisation in Python is handled through the `__init__.py` file. This file determines what is exposed when a package is imported and can be used to re-export selected names from submodules, providing a clean and stable public API.

---

## What it does

A directory with an `__init__.py` file is a **Python package**. When Python imports a package (e.g. `from devhub_<name>.clients.k8s import K8sPodClient`), it runs `__init__.py` in that directory first. Whatever names exist in that module after it runs become the package's public API — callers can import them directly from the package instead of from the individual module files.

A directory **without** `__init__.py` is a namespace package (PEP 420): importable, but it exposes nothing by default and behaves differently from a regular package. Always add `__init__.py` to every directory that should be importable as a package.

---

## The two patterns

The confusion between the two patterns is that both look the same when you write an import statement, because **importing a package and accessing its contents are two separate things**. When you write `import devhub_<name>.clients.k8s`, Python loads and runs `__init__.py` in every directory along the path — that always succeeds. But what you can *do afterwards* depends entirely on whether `__init__.py` re-exported anything.

### Pattern 1 — Marker only
The marker only pattern is used for internal grouping directories that are not part of the public import surface:
```python
# devhub_<name>/clients/__init__.py is empty
import devhub_<name>.clients           # ✅ works — Python sees a package
devhub_<name>.clients.K8sPodClient    # ❌ AttributeError — nothing was exposed
```
The directory is a package container. Nothing inside it is accessible as an attribute; callers must go deeper themselves:
```python
from devhub_<name>.clients.k8s import K8sPodClient  # must spell out the full path
```

### Pattern 2 — Re-export facade
> A *facade* is a design pattern where one interface hides the complexity behind it. Here, `__init__.py` acts as the facade: it presents a clean, stable set of names to callers while the actual implementation can live in any number of internal files. Callers never need to know which file a class comes from — they only see the package surface.

The Re-export facade pattern is used for public API directories:
```python
# devhub_<name>/clients/k8s/__init__.py
from devhub_<name>.clients.k8s.exceptions import *
from devhub_<name>.clients.k8s.k8s_pod_client import *
```
```python
import devhub_<name>.clients.k8s
devhub_<name>.clients.k8s.K8sPodClient  # ✅ works — __init__ created this attribute
from devhub_<name>.clients.k8s import K8sPodClient  # ✅ clean, stable import
```

### Comparison
| Behaviour | Marker only | Re-export facade |
|---|---|---|
| `import devhub_<name>.clients.k8s` | ✅ | ✅ |
| `devhub_<name>.clients.k8s.K8sPodClient` | ❌ `AttributeError` | ✅ |
| Callers need to know internal file layout | ✅ yes | ❌ no |
| Stable API survives internal refactoring | ❌ | ✅ |

Think of the two patterns as:
- **Empty `__init__.py`** → "this is a package container"
- **Re-exporting `__init__.py`** → "this is the public interface"

The practical consequence for a team: without re-exports, callers must know the internal file structure (`from devhub_<name>.clients.k8s.k8s_pod_client import K8sPodClient`). If you later rename or reorganise that file, every caller breaks. With a re-export facade, callers only know the package name (`from devhub_<name>.clients.k8s import K8sPodClient`), and internal refactoring is safe as long as `__init__.py` keeps exporting the same names.

---

## `*` imports and `__all__`

`from module import *` imports every name that does not start with `_`, **unless** the module defines `__all__`. Always define `__all__` in any module that is re-exported via `*`, to make the public API explicit and prevent internal helpers from leaking into the package namespace:

```python
# k8s_pod_client.py
__all__ = ["K8sPodClient"]
```