# `__init__.py` — Package Initialisation

This document describes how package initialisation (`__init__.py`) is designed in Python. The `__init__.py` file determines what a package exposes when it is imported, and is what turns a directory of modules into a clean and stable public API.

All packages should follow the best practices/conventions from Python itself:

- [Modules — Packages](https://docs.python.org/3/tutorial/modules.html#packages) and [Importing \* From a Package](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package) — what a package is and how `__all__` controls `import *`.
- [PEP 420 — Implicit Namespace Packages](https://peps.python.org/pep-0420/) — what a directory *without* `__init__.py` becomes.
- [PEP 8 — Imports](https://peps.python.org/pep-0008/#imports) and [Public and Internal Interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces) — import style and what belongs to the public surface.
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — every `__init__.py` starts with a module docstring.

Only the conventions that need extra attention, or that are specific to this codebase, are documented below.

> Throughout this document, `example_package` stands for the distribution's top-level package. The other names are placeholders too: `domain_a`/`domain_b` are domain sub-packages, `provider_x` a supplier package, and `SomeClient`/`SomeRecord`/`SomeInterface` the objects they export.

## Table of Contents

- [General principles](#general-principles)
- [What `__init__.py` does](#what-__init__py-does)
- [The two patterns](#the-two-patterns)
  - [Pattern 1 — Marker only](#pattern-1--marker-only)
  - [Pattern 2 — Re-export facade](#pattern-2--re-export-facade)
  - [Comparison](#comparison)
- [`*` imports and `__all__`](#-imports-and-__all__)
- [Importing the package from the outside](#importing-the-package-from-the-outside)
  - [The layout at a glance](#the-layout-at-a-glance)
  - [Which pattern to use where](#which-pattern-to-use-where)
  - [Top-level package](#top-level-package)
  - [Domain sub-package](#domain-sub-package)
  - [Internal grouping / nested sub-package](#internal-grouping--nested-sub-package)
- [Importing from within the package itself](#importing-from-within-the-package-itself)
  - [The facade chain above a module](#the-facade-chain-above-a-module)
  - [Rule 1 — inside your own facade chain, import from the defining module](#rule-1--inside-your-own-facade-chain-import-from-the-defining-module)
  - [Rule 2 — everywhere else, import from the facade](#rule-2--everywhere-else-import-from-the-facade)
  - [Why apply this even when Python does not fail](#why-apply-this-even-when-python-does-not-fail)
  - [Circular imports](#circular-imports)
  - [Breaking a cycle](#breaking-a-cycle)

---

## General principles

- **Every importable directory has an `__init__.py`.** A directory without one is a namespace package ([PEP 420](https://peps.python.org/pep-0420/)): importable, but it exposes nothing by default and behaves differently from a regular package.
- **Every `__init__.py` starts with a docstring** stating which of the two patterns it uses, why, and linking back to this document. In a marker-only file the docstring *is* the file, so it is the only thing telling the next reader why nothing is exported here.
- **`__init__.py` contains no logic.** It imports, it declares `__all__`, and nothing else. Behaviour belongs in a module, not in the file that runs on every import.
- **Declare `__all__` explicitly** in every module or package that is re-exported with `*`, so imported helpers (`dataclass`, `Optional`, `requests`, …) cannot leak into a caller's namespace.
- **Import from the defining module when you sit below the facade that exports you, from the facade everywhere else.** A module that imports a facade which imports it back imports itself; a facade that does not (another domain, a shared package) is the preferred path. See [Importing from within the package itself](#importing-from-within-the-package-itself).
- **Document skipped imports.** If a module is intentionally excluded from `__init__.py` (e.g. because it requires an optional binary such as `git`), explain why in the docstring so the next reader does not add it by mistake.
- **Logging.** The top-level package is the only `__init__.py` that runs code, to attach a `NullHandler`; see [Logging](./Logging.md).
- **Functions, Classes & Generics.** What is exported here is defined elsewhere; see [Functions](./Functions.md) and [Classes & Generics](./Classes_Generics.md).

---

## What `__init__.py` does

A directory with an `__init__.py` file is a **Python package**. When Python imports a package (e.g. `from example_package.domain_a import SomeClient`), it runs `__init__.py` in that directory first. Whatever names exist in that module after it runs become the package's public API — callers can import them directly from the package instead of from the individual module files.

The confusion between the two patterns below is that both look the same when you write an import statement, because **importing a package and accessing its contents are two separate things**. When you write `import example_package.domain_a`, Python loads and runs `__init__.py` in every directory along the path — that always succeeds. But what you can *do afterwards* depends entirely on whether `__init__.py` re-exported anything.

---

## The two patterns

### Pattern 1 — Marker only

The marker only pattern says: *this directory is a package container, nothing more*. The `__init__.py` holds a docstring and no imports, so nothing inside the directory is reachable as an attribute of the package:

```python
# example_package/domain_b/interfaces/__init__.py contains only a docstring
import example_package.domain_b.interfaces         # ✅ works — Python sees a package
example_package.domain_b.interfaces.SomeInterface  # ❌ AttributeError — nothing was exposed
```

Callers must go deeper themselves:

```python
from example_package.domain_b.interfaces.some_interface import SomeInterface  # must spell out the full path
```

That is precisely why this pattern is reserved for *internal* structure: the directory groups related files for the maintainers of the package, while callers reach its contents through a facade one level up (see [Internal grouping / nested sub-package](#internal-grouping--nested-sub-package)).

Because the docstring carries the whole file, it must state which pattern is used, where the contents *are* exported, and what the grouping is for:

```python
"""
Marker only `__init__.py` for the `example_package.domain_b.interfaces` package. Re-exported via
the `example_package.domain_b` package.

See <link to this document> for the pattern and rules.

The interfaces in this package define the roles and behaviours of the domain's components
independently of their implementations, so application code can talk to a component generically and
implementations can be added, replaced, or swapped without the application code changing.
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
    from example_package.models import SharedModel, OtherModel

See <link to this document> for the pattern and rules.

What belongs here:
    Models that are not owned by one domain — a deployment stage applies regardless of what is
    deployed, and a generic container groups *any* kind of object regardless of where it came
    from. Keeping them here means no domain module has to import another domain just to reuse a
    concept that is common to all of them.

What does not belong here:
    Anything a single domain owns. A domain's own records and clients live in that domain's
    package, and supplier-specific vocabulary in that provider's own package. A model that only
    makes sense inside one domain belongs to that domain, not here.
"""
from example_package.models.shared_model import SharedModel
from example_package.models.other_model import OtherModel

# Explicit public API, so an `import *` of this package cannot leak imported helpers (dataclass, Enum, TypeVar, ...) from the model modules into the caller's namespace.
__all__ = [
    "OtherModel",
    "SharedModel",
]
```

Both access styles now work, and neither mentions a file name:

```python
import example_package.models
example_package.models.SharedModel              # ✅ works — __init__ created this attribute
from example_package.models import SharedModel  # ✅ clean, stable import
```

### Comparison

| Behaviour | Marker only | Re-export facade |
|---|---|---|
| `import example_package.models` | ✅ | ✅ |
| `example_package.models.SharedModel` | ❌ `AttributeError` | ✅ |
| Callers need to know internal file layout | ✅ yes | ❌ no |
| Stable API survives internal refactoring | ❌ | ✅ |

Think of the two patterns as:

- **Marker only `__init__.py`** → "this is a package container"
- **Re-exporting `__init__.py`** → "this is the public interface"

The practical consequence for a team: without re-exports, callers must know the internal file structure (`from example_package.models.shared_model import SharedModel`). If you later rename or reorganise that file, every caller breaks. With a re-export facade, callers only know the package name (`from example_package.models import SharedModel`), and internal refactoring is safe as long as `__init__.py` keeps exporting the same names. That is also what makes splitting one growing `models.py` into a `models/` package free of cost: the file layout changes, the imports elsewhere do not.

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

## Importing the package from the outside

This is the *caller's perspective* (i.e. *outside* the package): application code, another distribution, or a test that consumes the published API. A caller never reaches into a file — it imports from whichever facade is the supported surface for that name, and which surfaces exist is decided by the pattern each `__init__.py` uses.

### The layout at a glance

A distribution is a tree of `__init__.py` files, each one either a facade or a marker. The annotations show what the file does and what it re-exports:

```
example_package/                  the distribution (import root)
├── __init__.py                   top-level facade   from example_package.domain_a import *
├── exceptions.py                 defining module    class ExamplePackageError(Exception): ...
├── models/                       shared models, owned by no single domain
│   ├── __init__.py               domain facade      from example_package.models.shared_model import SharedModel
│   └── shared_model.py           defining module    class SharedModel: ...
├── domain_a/                     a flat domain
│   ├── __init__.py               domain facade      from example_package.domain_a.some_client import SomeClient
│   └── some_client.py            defining module    class SomeClient: ...
└── domain_b/                     a deeper domain, several levels of nesting
    ├── __init__.py               domain facade      from example_package.domain_b.models.some_record import SomeRecord
    ├── some_module.py            defining module    class SomeHelper: ...
    ├── interfaces/               internal grouping
    │   ├── __init__.py           marker only        docstring only — exported by example_package.domain_b
    │   └── some_interface.py     defining module    class SomeInterface(ABC): ...
    ├── models/                   internal grouping, one module per concern
    │   ├── __init__.py           marker only        docstring only — exported by example_package.domain_b
    │   └── some_record.py        defining module    class SomeRecord: ...
    └── providers/                nested sub-packages with their own dependencies
        ├── __init__.py           marker only        docstring only — providers are named explicitly
        └── provider_x/           one supplier
            ├── __init__.py       nested facade      not re-exported upwards — the caller names it
            └── some_client.py    defining module    class ProviderXClient(SomeInterface): ...
```

Which gives callers exactly these paths, and no others:

```python
from example_package import SomeClient, SomeRecord                 # everything public, in one import
from example_package.domain_b import SomeInterface, SomeRecord     # one domain, when that is clearer at the call site
from example_package.domain_b.providers.provider_x import ProviderXClient  # opt-in: supplier named explicitly

from example_package.domain_b.models.some_record import SomeRecord  # ⚠️ works, but reaches into internal wiring — breaks when the file moves; avoid if possible by using above paths
from example_package.domain_b.interfaces import SomeInterface       # ❌ ImportError — marker only, nothing is exported here
from example_package.domain_b.models import SomeRecord              # ❌ ImportError — marker only, nothing is exported here
```

### Which pattern to use where

| Level | Example | Pattern | What a caller writes |
|---|---|---|---|
| [Top-level package](#top-level-package) | `example_package/` | re-export facade | `from example_package import X` |
| [Domain sub-package](#domain-sub-package) | `domain_a/`, `domain_b/`, `models/` | re-export facade | `from example_package.domain_b import X` |
| [Internal grouping](#internal-grouping--nested-sub-package) | `domain_b/interfaces/`, `domain_b/models/` | marker only | nothing — reached through the domain facade |
| [Nested, own dependencies](#internal-grouping--nested-sub-package) | `domain_b/providers/provider_x/` | facade, *not* re-exported upwards | `from example_package.domain_b.providers.provider_x import X` |

Depth says nothing about the pattern: `domain_b/models/` and `domain_b/providers/provider_x/` are both nested, yet the first is a grouping for maintainers (marker only, reached through the domain facade) and the second an opt-in surface with dependencies of its own (facade, named explicitly by the caller). A nested package only gets a facade when callers are meant to name it — giving one to a grouping that is already re-exported upwards would create two supported paths for the same class.

### Top-level package

**Pattern: [re-export facade](#pattern-2--re-export-facade).** Example: `example_package/`.

The top-level package is the entry point of the distribution, so everything public must be reachable in one import: `from example_package import SomeClient`. It re-exports its own modules and then each domain sub-package with `*`, relying on the `__all__` those declare (ensuring only the intended public API is exposed and the `__all__` is not duplicated). It is also the one `__init__.py` allowed to run code, to attach a `NullHandler` to the package logger (see [Logging](./Logging.md)), and the place where deliberately skipped imports are documented.

```python
"""
Top-level re-export facade for example_package.

All public symbols are re-exported here so callers can import directly from the package:
    from example_package import SomeClient
instead of reaching into sub-modules:
    from example_package.domain_a.some_client import SomeClient

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
from example_package.domain_a import * # exports example_package/domain_a/__init__.py.__all__
from example_package.domain_b import * # exports example_package/domain_b/__init__.py.__all__

# NOTE: The top-level package re-exports all domain sub-packages using `*`, relying on their `__all__` declarations to control the public API. It does not re-export private modules or symbols that are not included in the sub-packages' `__all__`.
```

### Domain sub-package

**Pattern: [re-export facade](#pattern-2--re-export-facade).** Examples: `example_package/domain_a/`, `example_package/domain_b/`, `example_package/models/`.

A domain sub-package is a public import surface of its own: `from example_package.domain_a import SomeClient`. Its facade imports the public names out of the modules that define them — including the ones inside marker-only groupings — and declares them in `__all__`, which is what lets the top level re-export the entire domain with a single `*`.

The docstring is where the domain explains its own layout and — just as importantly — what it deliberately does **not** export:

```python
"""
Re-export facade for example_package.domain_b.

The package is organised by responsibility rather than by supplier:
    interfaces/     the roles callers depend on, independent of any implementation
    models/         the supplier-neutral data types
    some_module.py  the helpers shared by every implementation
    providers/      one package per supplier, adapting its API to the interfaces and models

Roles, models, and helpers are re-exported here so callers can import them in one line:
    from example_package.domain_b import SomeInterface, SomeRecord

Provider packages are deliberately *not* re-exported, so importing this package does not pull in
every supplier's dependencies and it stays obvious at the call site which supplier is being used:
    from example_package.domain_b.providers.provider_x import ProviderXClient

See <link to this document> for the pattern and rules.
"""
# interfaces/ and models/ are marker only packages, so their contents come from their own modules:
from example_package.domain_b.interfaces.some_interface import OtherInterface, SomeInterface
from example_package.domain_b.models.some_record import SomeRecord
from example_package.domain_b.some_module import SomeHelper

# Explicit public API, so an `import *` of this package cannot leak imported helpers (dataclass, Enum, TypeVar, ...) from the model modules into the caller's namespace.
__all__ = [
    "OtherInterface",
    "SomeHelper",
    "SomeInterface",
    "SomeRecord",
]
```

### Internal grouping / nested sub-package

**Pattern: [marker only](#pattern-1--marker-only).** Examples: `example_package/domain_b/interfaces/`, `example_package/domain_b/models/`, `example_package/domain_b/providers/`.

A directory that exists to group files for the maintainers is not part of the public import surface, however deep it sits. Its contents are exported by the domain facade one or more levels up, so callers write `from example_package.domain_b import SomeInterface` and never `from example_package.domain_b.interfaces import SomeInterface`. Adding a facade here as well would give the same class two supported import paths, and every caller would have to guess which one is intended.

Its `__init__.py` therefore holds only a docstring: which pattern it uses, where its contents are re-exported, and what the grouping is for (see the example under [Pattern 1 — Marker only](#pattern-1--marker-only)).

> **Exception — a nested package with its own dependencies.** A nested package that callers must name explicitly, such as a provider package (`example_package/domain_b/providers/provider_x/`), is a public surface in its own right and uses the facade pattern instead (e.g. `from example_package.domain_b.providers.provider_x import ProviderXClient`). It is not re-exported upwards precisely so that its supplier-specific dependencies are only imported when that provider is actually used.

---

## Importing from within the package itself

This is the *maintainer's perspective*: code that lives *inside* the distribution. The goal of the facade pattern is to make the public API as easy, usable, and maintainable as possible: one obvious import path per name, short enough to write from memory (`from example_package.domain_b import SomeRecord`), and stable when the file layout behind it changes.

That goal only holds if a facade is never consumed by the code it exports. A facade that is also used from below stops being a thin, freely re-organisable layer and becomes a load-bearing part of the implementation — at which point moving a class between files can break the package itself, not just its callers.

Which import path is correct therefore depends on one thing only: **WHETHER THE FACADE YOU WANT TO IMPORT FROM ALREADY IMPORTS YOU.**

### The facade chain above a module

Every name is defined in exactly one module, and each `__init__.py` above that module that re-exports it — the domain facade, then the top-level facade (see for details [Importing the package from the outside](#importing-the-package-from-the-outside)) — already depends on it. Those files are the module's **own facade chain**:

```
example_package/__init__.py                                   top-level facade   from example_package.domain_b import *
└── example_package/domain_b/__init__.py                      domain facade      from example_package.domain_b.models.some_record import SomeRecord
    └── example_package/domain_b/models/__init__.py           marker only        docstring only — exports nothing
        └── example_package/domain_b/models/some_record.py    defining module    class SomeRecord: ...
```

For `some_record.py` the chain is `example_package.domain_b` and `example_package`; the marker-only `models` package imports nothing, so nothing depends on it (see [Which pattern to use where](#which-pattern-to-use-where) for what each level is). Anything *not* in the chain — `example_package.domain_a`, `example_package.models`, another distribution — does not depend on the module and is free to import.

### Rule 1 — inside your own facade chain, import from the defining module

When the name you need is exported by a facade that also sits above **you**, bypass that facade and import from the module that defines the name:

```python
# example_package/domain_b/providers/provider_x/some_client.py
from example_package.domain_b.models.some_record import SomeRecord  # ✅ the defining module
from example_package.domain_b import SomeRecord                     # ❌ a facade that imports this module
from example_package import SomeRecord                              # ❌ the top-level facade, same problem
```

Below a facade, import direction therefore always points **downwards**, from the facade towards the modules, never back up or sideways through it.

### Rule 2 — everywhere else, import from the facade

Every other position is that of an ordinary caller, and callers use the public path:

- **Application/client code** consuming the distribution.
- **Tests** for the package, which should exercise the same surface a consumer gets.
- **Another domain or sub-package** in the same distribution, whose facade chain is separate from yours.

```python
# example_package/domain_b/providers/provider_x/helpers.py — lives below the example_package.domain_b chain
from example_package.domain_a import SomeClient  # ✅ different domain — its facade does not import us
from example_package.models import SharedModel   # ✅ shared models — same reasoning
from example_package.domain_b.providers.provider_x.models import ProviderXType  # ✅ own chain — defining module
```

So `from example_package.domain_a import ...` inside `example_package.domain_b` is not an exception to Rule 1 — it is Rule 2 — and it is the *preferred* form: short, stable, and identical to the line an external caller writes, so there is no second import style for code that happens to ship in the same distribution.

It works because the dependency runs one way only: `domain_a` knows nothing about `domain_b` and never imports it. Keep that direction deliberate — two domains importing each other's facades is a real cycle, and usually means a shared model is in the wrong place (see [Breaking a cycle](#breaking-a-cycle)).

### Why apply this even when Python does not fail

Breaking Rule 1 often *appears* to work. A package being imported is registered in `sys.modules` while it is still initialising, so a facade import from below is frequently satisfied from that half-finished module without raising anything. It fails only when the name is read before the facade has assigned it — which depends on *which module the process imports first*, something a library cannot control.

Apply the rules regardless of whether the current import order happens to succeed:

- The failure mode is an `ImportError`/`AttributeError` at import time in an unrelated part of the codebase, triggered by a change that touched neither module.
- Whether it fails differs per entry point, so an application, a script, and the test suite can disagree about whether the package imports at all.
- The facade stops being safe to reorganise, which is the entire reason it exists.

Treat the rules as structural rather than as a fix for an error you have already seen, and verify them with the static check below instead of with a passing import.

### Circular imports

A circular import is two or more modules that import each other, directly or through an `__init__.py`. `__init__.py` is the *leaf importer* — it imports from the modules below it, never the other way around — so importing a package facade from one of its own modules closes a loop:

```
example_package/domain_b/__init__.py       imports  interfaces/some_interface.py
interfaces/some_interface.py               imports  example_package.domain_b    ← back to the facade
```

For the reasons above, such a cycle can sit in the codebase unnoticed until an unrelated change alters the import order. Verify statically instead of trusting that imports currently succeed — see [Checking circular imports](./StaticCodeAnalysis.md#checking-circular-imports).

### Breaking a cycle

In order of preference:

1. **Import from the defining module** instead of from the facade. This is the fix for nearly every cycle Pylint reports, and it costs nothing.
2. **Move the shared type up** into a package both sides may import, when two domains genuinely need the same model — that is what `example_package/models/` is for. A cycle between two domains is usually a misplaced model, not an import problem.
3. **Import only for type checking** with `if typing.TYPE_CHECKING:` and a string annotation, when the import exists purely for annotations. This removes the import at runtime and with it the cycle, but it hides the design problem instead of fixing it, so use it last.