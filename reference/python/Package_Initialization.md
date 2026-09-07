# `__init__.py` — Package Initialisation

This document describes how package initialisation (`__init__.py`) is designed in Python. The `__init__.py` file determines what a package exposes when it is imported, and is what turns a directory of modules into a clean and stable public API.

All packages should follow the best practices/conventions from Python itself:

- [Modules — Packages](https://docs.python.org/3/tutorial/modules.html#packages) and [Importing \* From a Package](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package) — what a package is and how `__all__` controls `import *`.
- [PEP 420 — Implicit Namespace Packages](https://peps.python.org/pep-0420/) — what a directory *without* `__init__.py` becomes.
- [PEP 8 — Imports](https://peps.python.org/pep-0008/#imports) and [Public and Internal Interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces) — import style and what belongs to the public surface.
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — every `__init__.py` starts with a module docstring.

Only the conventions that need extra attention, or that are specific to this codebase, are documented below.

## Table of Contents

- [General principles](#general-principles)
- [What `__init__.py` does](#what-__init__py-does)
- [The two patterns](#the-two-patterns)
  - [Pattern 1 — Marker only](#pattern-1--marker-only)
  - [Pattern 2 — Re-export facade](#pattern-2--re-export-facade)
  - [Comparison](#comparison)
- [`*` imports and `__all__`](#-imports-and-__all__)
- [Which pattern to use where](#which-pattern-to-use-where)
  - [Top-level package](#top-level-package)
  - [Domain sub-package](#domain-sub-package)
  - [Internal grouping / nested sub-package](#internal-grouping--nested-sub-package)

---

## General principles

- **Every importable directory has an `__init__.py`.** A directory without one is a namespace package ([PEP 420](https://peps.python.org/pep-0420/)): importable, but it exposes nothing by default and behaves differently from a regular package.
- **Every `__init__.py` starts with a docstring** stating which of the two patterns it uses, why, and linking back to this document. In a marker-only file the docstring *is* the file, so it is the only thing telling the next reader why nothing is exported here.
- **`__init__.py` contains no logic.** It imports, it declares `__all__`, and nothing else. Behaviour belongs in a module, not in the file that runs on every import.
- **Declare `__all__` explicitly** in every module or package that is re-exported with `*`, so imported helpers (`dataclass`, `Optional`, `requests`, …) cannot leak into a caller's namespace.
- **Avoid circular imports.** `__init__.py` is the *leaf importer* — it imports from the modules below it, never the other way around. If module `a` imports from `b` and `b` imports from `a` (directly or via `__init__`), Python fails mid-execution with a partially-initialised module.
- **Document skipped imports.** If a module is intentionally excluded from `__init__.py` (e.g. because it requires an optional binary such as `git`), explain why in the docstring so the next reader does not add it by mistake.
- **Logging.** The top-level package is the only `__init__.py` that runs code, to attach a `NullHandler`; see [Logging](./Logging.md).
- **Functions, Classes & Generics.** What is exported here is defined elsewhere; see [Functions](./Functions.md) and [Classes & Generics](./Classes_Generics.md).

---

## What `__init__.py` does

A directory with an `__init__.py` file is a **Python package**. When Python imports a package (e.g. `from example_package.clients import ServiceClient`), it runs `__init__.py` in that directory first. Whatever names exist in that module after it runs become the package's public API — callers can import them directly from the package instead of from the individual module files.

The confusion between the two patterns below is that both look the same when you write an import statement, because **importing a package and accessing its contents are two separate things**. When you write `import example_package.clients`, Python loads and runs `__init__.py` in every directory along the path — that always succeeds. But what you can *do afterwards* depends entirely on whether `__init__.py` re-exported anything.

---

## The two patterns

### Pattern 1 — Marker only

The marker only pattern says: *this directory is a package container, nothing more*. The `__init__.py` holds a docstring and no imports, so nothing inside the directory is reachable as an attribute of the package:

```python
# example_package/services/interfaces/__init__.py contains only a docstring
import example_package.services.interfaces            # ✅ works — Python sees a package
example_package.services.interfaces.ServiceInterface  # ❌ AttributeError — nothing was exposed
```

Callers must go deeper themselves:

```python
from example_package.services.interfaces.primary import PrimaryService  # must spell out the full path
```

That is precisely why this pattern is reserved for *internal* structure: the directory groups related files for the maintainers of the package, while callers reach its contents through a facade one level up (see [Internal grouping / nested sub-package](#internal-grouping--nested-sub-package)).

Because the docstring carries the whole file, it must state which pattern is used, where the contents *are* exported, and what the grouping is for:

```python
"""
Marker only `__init__.py` for the `example_package.services.interfaces` package. Re-exported via the
`example_package.services` package.

See <link to this document> for the pattern and rules.

The interfaces in this package define the roles and behaviours of service components independently of
their implementations, so application code can talk to a service component generically and providers
can be added, replaced, or swapped without the application code changing.
"""
```

### Pattern 2 — Re-export facade

> A *facade* is a design pattern where one interface hides the complexity behind it. Here, `__init__.py` acts as the facade: it presents a clean, stable set of names to callers while the actual implementation can live in any number of internal files. Callers never need to know which file a class comes from — they only see the package surface.

The facade imports the package's public names out of its modules and declares them in `__all__`. The docstring states what the package is for, what belongs in it, and what does not:

```python
"""
Re-export facade for example_package.models.

All shared model types are re-exported here so callers can import directly from the package and
stay unaffected by which file a model lives in:
    from example_package.models import Environment, ResourceCollection

See <link to this document> for the pattern and rules.

What belongs here:
    Models that are not owned by one domain — a deployment stage applies regardless of what is
    deployed, and the generic containers group *any* kind of object regardless of where it came
    from. Keeping them here means no domain module has to import another domain just to reuse a
    concept that is common to all of them.

What does not belong here:
    Anything a single domain owns. Service records and backends live in the services package, and
    supplier-specific vocabulary in that provider's own package. A model that only makes sense
    inside one domain belongs to that domain, not here.
"""
from example_package.models.environment import Environment
from example_package.models.resources import ResourceCollection, ResourceInventory

# Explicit public API, so an `import *` of this package cannot leak imported helpers (dataclass,
# Enum, TypeVar, ...) from the model modules into the caller's namespace.
__all__ = [
    "Environment",
    "ResourceCollection",
    "ResourceInventory",
]
```

Both access styles now work, and neither mentions a file name:

```python
import example_package.models
example_package.models.Environment              # ✅ works — __init__ created this attribute
from example_package.models import Environment  # ✅ clean, stable import
```

### Comparison

| Behaviour | Marker only | Re-export facade |
|---|---|---|
| `import example_package.models` | ✅ | ✅ |
| `example_package.models.Environment` | ❌ `AttributeError` | ✅ |
| Callers need to know internal file layout | ✅ yes | ❌ no |
| Stable API survives internal refactoring | ❌ | ✅ |

Think of the two patterns as:

- **Marker only `__init__.py`** → "this is a package container"
- **Re-exporting `__init__.py`** → "this is the public interface"

The practical consequence for a team: without re-exports, callers must know the internal file structure (`from example_package.models.environment import Environment`). If you later rename or reorganise that file, every caller breaks. With a re-export facade, callers only know the package name (`from example_package.models import Environment`), and internal refactoring is safe as long as `__init__.py` keeps exporting the same names. That is also what makes splitting one growing `models.py` into a `models/` package free of cost: the file layout changes, the imports elsewhere do not.

---

## `*` imports and `__all__`

`from module import *` imports every name that does not start with `_`, **unless** the module defines `__all__` (in that case it imports only the names listed in `__all__`). Always define `__all__` in any module that is re-exported via `*`, to make the public API explicit and prevent internal helpers from leaking into the package namespace:

```python
# exceptions.py
__all__ = ["SomeException"]
```

A facade may re-export either by name (`from ... import A, B`) or with `*`. Use explicit names when the list is short and stable, and `*` when the sub-package already declares its own `__all__` — the sub-package then owns its surface, and the parent does not have to be updated whenever it changes. 

**NEVER duplicate the `__all__` list from the sub-package in the parent module (DRY), write it once:** Always try to import the sub-package with `*` and rely on its own `__all__`, ensuring you only define `__all__` once (e.g. in the sub-package itself).

---

## Which pattern to use where

### Top-level package

**Pattern: [re-export facade](#pattern-2--re-export-facade).** Example: `example_package/`.

The top-level package is the entry point of the distribution, so everything public must be reachable in one import: `from example_package import BaseHTTPClient`. It re-exports its own modules and then each domain sub-package with `*`, relying on the `__all__` those declare (ensuring only the intended public API is exposed and the `__all__` is not duplicated). It is also the one `__init__.py` allowed to run code, to attach a `NullHandler` to the package logger (see [Logging](./Logging.md)), and the place where deliberately skipped imports are documented.

```python
"""
Top-level re-export facade for example_package.

All public symbols are re-exported here so callers can import directly from the package:
    from example_package import BaseHTTPClient
instead of reaching into sub-modules:
    from example_package.utils.client_utils import BaseHTTPClient

See <link to this document> for the pattern and rules.
"""
import logging

# NullHandler: satisfies Python's requirement that at least one handler exists on the top-level
# package logger, so no "No handlers could be found" warning is emitted when an application has not
# configured logging yet. See ./Logging.md#libraries.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Top-level re-exports:
from example_package.exceptions import * # exports example_package/exceptions.py.__all__

# Domain module re-exports — each sub-package defines its own __all__:
from example_package.models import * # exports example_package/models/__init__.py.__all__
from example_package.services import * # exports example_package/services/__init__.py.__all__
from example_package.clients import * # exports example_package/clients/__init__.py.__all__

...
```

### Domain sub-package

**Pattern: [re-export facade](#pattern-2--re-export-facade).** Examples: `example_package/services/`, `example_package/clients/`, `example_package/models/`, `example_package/utils/`.

A domain sub-package is a public import surface of its own: `from example_package.clients import ServiceClient`. Its facade imports the public names out of its modules and nested sub-packages and declares them in `__all__`, which is what lets the top level re-export the entire domain with a single `*`.

The docstring is where the domain explains its own layout and — just as importantly — what it deliberately does **not** export:

```python
"""
Re-export facade for example_package.services.

The services package is organised by responsibility rather than by supplier:
    interfaces/   the service roles callers depend on
    models/       the provider-neutral records and backends
    transports.py how a server is reached: HTTP, local endpoints, or a provider protocol
    providers/    one package per supplier, adapting its API to the interfaces and models

Roles, models, and transports are re-exported here so callers can import them in one line:
    from example_package.services import PrimaryService, ServiceRecordSet

Provider packages are deliberately *not* re-exported, so importing this package does not pull in
every supplier's dependencies and it stays obvious at the call site which supplier is being used:
    from example_package.services.providers.example_provider import ExampleServiceClient

See <link to this document> for the pattern and rules.
"""
from example_package.services.interfaces import PrimaryService, SecondaryService
from example_package.services.models import ServiceBackend, ServiceRecordSet
from example_package.services.transports import HTTPTransport

# Explicit public API, so an `import *` of this package cannot leak imported helpers (dataclass, Optional, requests, ...) from the sub-modules into the caller's namespace.
__all__ = [
    "PrimaryService",
    "ServiceBackend",
    "ServiceRecordSet",
    "HTTPTransport",
    "SecondaryService",
]
```

### Internal grouping / nested sub-package

**Pattern: [marker only](#pattern-1--marker-only).** Examples: `example_package/services/interfaces/`, `example_package/services/models/`.

A directory that exists to group files for the maintainers is not part of the public import surface. Its contents are exported by the domain facade one or more levels up, so callers write `from example_package.services import PrimaryService` and never `from example_package.services.interfaces import PrimaryService`. Adding a facade here as well would give the same class two supported import paths, and every caller would have to guess which one is intended.

Its `__init__.py` therefore holds only a docstring: which pattern it uses, where its contents are re-exported, and what the grouping is for (see the example under [Pattern 1 — Marker only](#pattern-1--marker-only)).

> **Exception — a nested package with its own dependencies.** A nested package that callers must name explicitly, such as a provider package (`example_package/services/providers/example_provider/`), is a public surface in its own right and uses the facade pattern instead (e.g. `from example_package.services.providers.example_provider import ExampleServiceClient`). It is not re-exported upwards precisely so that its supplier-specific dependencies are only imported when that provider is actually used.
> **Exception — other good reasons to re-export.** If you have any other reason to re-export a nested package, document it clearly in the `__init__.py` so that maintainers and callers understand why it is necessary and how it should be used. For example, you might want a separate `models` package within the nested package to group related data structures, and you choose to re-export it for convenience (e.g. `from kpn_dns.dns.models import DNSModel`).