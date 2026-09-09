# `__init__.py` — Package Initialization and Importing

This document covers the two halves of one design: what a package **exposes** through its `__init__.py`, and which import path is then **written** for a name — by callers outside the distribution and by the modules inside it.

The first half is a design decision, and the question it answers is never *"how deep does this package sit?"* but **"which import path do we want callers to write for this name?"** The package that answers *"mine"* **owns** that name: it declares it in `__all__`, and that is the name's canonical import path. Every other level either forwards to the owner or exposes nothing at all. Ownership — not depth — decides which pattern an `__init__.py` uses.

The second half follows from it: given those surfaces, which one a module *inside* the distribution may import from without turning a facade into a load-bearing part of the implementation.

**All packages should follow the best practices/conventions from Python itself, such as:**

- [The Import System](https://docs.python.org/3/reference/import.html) — how Python finds and loads modules.
- [Modules — Packages](https://docs.python.org/3/tutorial/modules.html#packages) and [Importing \* From a Package](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package) — what a package is and how `__all__` controls `import *`.
- [PEP 420 — Implicit Namespace Packages](https://peps.python.org/pep-0420/) — what a directory *without* `__init__.py` becomes.
- [PEP 8 — Imports](https://peps.python.org/pep-0008/#imports) and [Public and Internal Interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces) — import style and what belongs to the public surface.
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — every `__init__.py` starts with a module docstring.

See for more details the [General Official Python Documentation](https://docs.python.org/3/).

**Only the conventions that need extra attention, or that are specific to this codebase, are documented below.**

> Throughout this document, `example_package` stands for the distribution's top-level package. The other names are placeholders too: `domain_a`/`domain_b` are sub-packages, `provider_x` a supplier package, and `SomeClient`/`SomeRecord`/`SomeInterface` the objects they export.

## Table of Contents

- [General principles](#general-principles)
- [Background](#background)
  - [What `__init__.py` does & how importing works](#what-__init__py-does--how-importing-works)
  - [`*` imports and `__all__`](#-imports-and-__all__)
  - [The three patterns](#the-three-patterns)
    - [Marker](#marker)
    - [Local facade](#local-facade)
    - [Aggregation facade](#aggregation-facade)
- [Deciding what a package exposes](#deciding-what-a-package-exposes)
  - [The ownership question](#the-ownership-question)
  - [The `__init__.py` docstring template](#the-__init__py-docstring-template)
  - [Forwarding with `import *` and `__all__`](#forwarding-with-import--and-__all__)
    - [A facade that owns names](#a-facade-that-owns-names)
    - [A facade that forwards](#a-facade-that-forwards)
    - [A facade that owns *and* forwards](#a-facade-that-owns-and-forwards)
    - [The distribution root](#the-distribution-root)
  - [The layout at a glance](#the-layout-at-a-glance)
  - [Top-level package](#top-level-package)
  - [Nested sub-packages](#nested-sub-packages)
    - [Outcome 1 — marker](#outcome-1--marker)
    - [Outcome 2 — local facade, forwarded upwards](#outcome-2--local-facade-forwarded-upwards)
      - [Outcome 2.1 — a domain directly under the root](#outcome-21--a-domain-directly-under-the-root)
      - [Outcome 2.2 — a package nested inside a domain](#outcome-22--a-package-nested-inside-a-domain)
    - [Outcome 3 — local facade, not forwarded](#outcome-3--local-facade-not-forwarded)
- [Importing from within the package itself](#importing-from-within-the-package-itself)
  - [Which path to use](#which-path-to-use)
  - [Why apply this even when Python does not fail](#why-apply-this-even-when-python-does-not-fail)
  - [Circular imports and how to break them](#circular-imports-and-how-to-break-them)
    - [Fix 1 — import from the defining module](#fix-1--import-from-the-defining-module)
    - [Fix 2 — give the shared concept a proper owner](#fix-2--give-the-shared-concept-a-proper-owner)
    - [Fix 3 — import only for type checking](#fix-3--import-only-for-type-checking)

---

## General principles

- **Every importable directory has an `__init__.py`.** A directory without one is a namespace package ([PEP 420](https://peps.python.org/pep-0420/)): importable, but it exposes nothing by default and behaves differently from a regular package.
- **One owner per name.** Exactly one place declares a public name in `__all__`: the `__init__.py` of the package callers are meant to import it from, or — for a top-level module — the module itself. That place is the name's canonical import path.
- **Never declare the same name in two `__all__` lists.** A name that is already owned somewhere is *forwarded* with `*`, never re-listed by hand; two lists mean two things to keep in sync and two competing answers to "where does this come from?".
- **Depth decides nothing.** A package three levels down can be a fully supported import surface, and a package directly under the root can be pure file organisation. Only the import path you want to support decides the pattern.
- **Every `__init__.py` starts with a docstring** that follows [the docstring template](#the-__init__py-docstring-template): which of the three patterns it uses, why, how to import from it, and what the package is for. In a marker file the docstring *is* the file, so it is the only thing telling the next reader why nothing is exported here.
- **`__init__.py` contains no logic.** It imports, it declares `__all__`, and nothing else. Behaviour belongs in a module, not in the file that runs on every import.
- **Import from the defining module when you sit below the facade that exports you, from the owning facade everywhere else.** A module that imports a facade which imports it back imports itself. See [Importing from within the package itself](#importing-from-within-the-package-itself).
- **Document skipped imports.** If a module is intentionally excluded from `__init__.py` (e.g. because it requires an optional binary such as `git`), explain why in the docstring so the next reader does not add it by mistake.
- **Logging.** The top-level package is the only `__init__.py` that runs code, to attach a `NullHandler`; see [Logging](./Logging.md).
- **Functions, Classes & Generics.** What is exported here is defined elsewhere; see [Functions](./Functions.md) and [Classes & Generics](./Classes_Generics.md).

---

## Background

### What `__init__.py` does & how importing works

Python resolves an import in three steps ([The import system](https://docs.python.org/3/reference/import.html) describes them in full):

1. **Finding.** For `import example_package.domain_a.some_client`, Python walks the dotted name from left to right and looks each part up on `sys.path` (for the root) or in the parent package's directory (for every part after it).
2. **Loading and executing.** Each part not already in `sys.modules` is executed **once**, top to bottom, as a module object: for a directory that means running its `__init__.py`, for a file the file itself. The result is cached in `sys.modules`, so importing the same module again anywhere in the process is a dictionary lookup, not a re-execution.
3. **Binding.** The names produced by that execution become attributes of the module object, and importing a sub-module also binds it as an attribute of its parent package. `import x.y` then binds `x` in the local namespace, while `from x import y` binds `y` — after `x` has been fully executed.

A directory with an `__init__.py` file is a **Python package**, and step 2 is where it earns its keep: whatever names exist in that module after it runs become the package's public API, so callers can import them from the package instead of from the individual module files. Step 2 also explains why an `__init__.py` must stay free of logic — it runs on every first import of anything below it — and why cycles are a real risk: a module that is still halfway through step 2 is already in `sys.modules`, so an import of it succeeds while it is still incomplete (see [Why apply this even when Python does not fail](#why-apply-this-even-when-python-does-not-fail)).

**Importing a package and accessing its contents are two separate things.** When you write `import example_package.domain_a`, Python loads and runs `__init__.py` in every directory along the path — that always succeeds. But what you can *do afterwards* depends entirely on whether that `__init__.py` bound any names:

```python
import example_package.domain_b.interfaces         # ✅ always works — Python sees a package (assuming the file exists: example_package/domain_b/interfaces.py)
example_package.domain_b.interfaces.SomeInterface  # ✅ or ❌ AttributeError — depends on the __init__.py
```

Every import path a caller can write is therefore a deliberate choice, made in exactly one `__init__.py`.

### `*` imports and `__all__`

> See for full details the [official Python docs on `*` and `__all__`](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package)

`from module import *` imports every name that does not start with `_`, **unless** the module defines `__all__` — then it imports only the names listed there. `__all__` is what makes a public API explicit and keeps imported helpers (`dataclass`, `Optional`, `requests`, …) from leaking into the caller's namespace:

```python
# exceptions.py
__all__ = ["SomeException"]
```

`__all__` is also the mechanism behind ownership: **the file that declares a name in `__all__` owns it.** A package that wants to expose a name it does not own forwards it with `*` and inherits the owner's list, so the name is written down once and only once (DRY). Listing the same name by hand in a second `__all__` is never correct — see [A facade that forwards](#a-facade-that-forwards).

### The three patterns

Every `__init__.py` is one of three things (a facade may be both of the last two at once):

| Pattern | The `__init__.py` contains | Owns names | Declares `__all__` | Supported caller import |
|---|---|---|---|---|
| [**Marker**](#marker) | a docstring, nothing else | no | no | none — the package exposes nothing |
| [**Local facade**](#local-facade) | imports of the names defined in *its own* modules | yes | yes | `from example_package.domain_a import SomeClient` |
| [**Aggregation facade**](#aggregation-facade) | `*` imports of the packages/modules below it | no | inherits, see [A facade that forwards](#a-facade-that-forwards) | `from example_package import SomeClient` |

> A *facade* is a design pattern where one interface hides the complexity behind it. Here `__init__.py` is the facade: it presents a stable set of names while the implementation can live in any number of files, so callers never need to know which file a class comes from and internal refactoring costs nothing.

#### Marker

The directory is structure for maintainers, not an import surface. Its contents are reached through whichever facade owns them, so nothing here is importable:

```python
# example_package/domain_b/models/__init__.py holds a docstring and nothing else
from example_package.domain_b.models import SomeRecord  # ❌ ImportError — nothing is exported here
from example_package.domain_b import SomeRecord         # ✅ the facade that owns the name
```

The docstring therefore carries the whole file; see [the docstring template](#the-__init__py-docstring-template) for what it must state.

#### Local facade

The package *is* the supported import path for the names its own modules define, and declares them in `__all__`, such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Local facade for `example_package.models`.

The shared models are a surface callers depend on by name, so this package owns them and is the one
supported path to each of them.

See <link to this document> for the patterns and rules.

How to use it: import the models from this package, so a caller stays unaffected by which file each
model lives in:
    from example_package.models import OtherModel, SharedModel

What this package is for: models that are not owned by one domain, so no domain has to import
another domain just to reuse a concept common to all of them. Anything a single domain owns does not
belong here — that lives in the domain's own package.
"""
from example_package.models.other_model import OtherModel
from example_package.models.shared_model import SharedModel

# Explicit public API, so an `import *` of this package cannot leak imported helpers (e.g. a private function) from the model modules.
__all__ = [
    "OtherModel",
    "SharedModel",
]
```

#### Aggregation facade

The package owns nothing itself; it forwards the surfaces below it with `*` so that everything public is reachable in one shorter import:

```python
from example_package.models import *     # forwards example_package/models/__init__.py.__all__
from example_package.domain_a import *   # forwards example_package/domain_a/__init__.py.__all__
```

---

## Deciding what a package exposes

This is the *caller's perspective* (i.e. *outside* the package): application code, another distribution, or a test that consumes the published API. Which import paths exist for a name is not a property of the file layout — it is a decision, taken once per package.

### The ownership question

For every package, one question decides the pattern:

> **Do I want callers to write `from <this package> import X`?**

| Answer | Pattern | Consequence |
|---|---|---|
| Yes, and `X` is defined in this package's own modules | [local facade](#local-facade) | This package **owns** `X` and declares it in `__all__` |
| Yes, but `X` is owned by a package below | [aggregation facade](#aggregation-facade) | Forward with `*`; never re-declare `X` |
| No | [marker](#marker) | The directory is file organisation; a facade above owns its contents and imports them from their defining modules |

Two consequences are worth spelling out, because both are easy to get wrong:

- **Depth is irrelevant.** Two packages at the same depth can differ: `domain_b/interfaces/` may be a supported surface callers name explicitly, while its sibling `domain_b/models/` is a marker whose contents are exported one level up. "Nested" never implies "internal", and "directly under the root" never implies "public".
- **Forwarding upwards does not create a second owner.** Aggregating a name to the root gives it a shorter path as well (`from example_package import SomeInterface`) — a deliberate convenience entry point, while the owner remains the one place the name is declared and documented. What must never exist is two *unrelated* packages exporting the same name, so callers have to guess which path is intended.

**When in doubt, start with a marker. Not exposing something is reversible; every supported import path is a promise you have to keep to the caller.**

### The `__init__.py` docstring template

> See for docstring convention in Python: [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/).

Once the decision is made, it has to be written down in the file that implements it — the docstring is the only place a reader can see *why* a package exposes what it exposes. Every `__init__.py` uses the same four blocks, in this order:

```python
"""
<Pattern> for `<full.dotted.package>`.

<One sentence on why that pattern was chosen for this package.>

See <link to this document> for the patterns and rules.

How to use it: <How callers import from here — the supported path(s), or, for a marker, where the contents are
exported instead:>
    from <full.dotted.package> import SomeName

What this package is for: <what belongs in it, what does not, and any import deliberately skipped.>
"""
```

**Example:** Filled in for a [marker](#marker), where the docstring *is* the whole file:

```python
"""
Marker for `example_package.domain_b.models`.

The records are owned one level up, so there is exactly one supported path to each of them.

See <link to this document> for the patterns and rules.

How to use it: nothing is exported here; the records are imported from the facade that owns them:
    from example_package.domain_b import SomeRecord

What this package is for: one module per model concern instead of one growing models.py. A new
record gets its own module here and is exported by `example_package.domain_b`; nothing is added to
this file.
"""
```

[Local facade](#local-facade), [Aggregation facade](#aggregation-facade), and [Nested sub-packages](#nested-sub-packages) show the same template filled in for the other patterns, followed by the imports and `__all__` that implement them.

### Forwarding with `import *` and `__all__`

A name is declared in `__all__` exactly once — in its owner; every level above the owner *forwards* it. Forwarding uses two mechanisms that are easy to confuse, because they usually sit on adjacent lines and only one of them is visible at the call site:

- **`from <owner> import *` binds.** It copies the names listed in the owner's `__all__` into this package's namespace, which is what makes `from <this package> import SomeName` work at runtime. It does **not** copy the owner's `__all__`; that stays an ordinary variable in the owner's module.
- **`__all__` declares.** It decides which of the names bound here are taken by a *further* `import *` one level up, and it is what linters, type checkers, and API documentation read as "the public surface of this package". It has no effect on a direct `from <this package> import SomeName`.

The two therefore answer different questions — *"can this name be reached from here?"* versus *"does this name travel any further up?"* — which is why a facade that is itself star-imported needs both, and why a facade that nothing star-imports needs only the first.

| Case | What it does with `import *` | What it does with `__all__` |
|---|---|---|
| [A facade that owns names](#a-facade-that-owns-names) | not used — it imports its own names explicitly | declares exactly the names it owns |
| [A facade that forwards](#a-facade-that-forwards) | one per forwarded package or module | none of its own, unless something star-imports it in turn |
| [A facade that owns *and* forwards](#a-facade-that-owns-and-forwards) | one per forwarded package, plus explicit imports for its own names | extends the forwarded `__all__` with the names it owns |
| [The distribution root](#the-distribution-root) | one per sub-package and top-level module | omitted — nothing star-imports the root |

#### A facade that owns names

It imports its names explicitly (never with `*`) and lists exactly those names in `__all__`, it is the *owner* of those names:

```python
from example_package.models.shared_model import SharedModel

__all__ = [
    "SharedModel",
]
```

Explicit imports keep the choice of what becomes public in the facade rather than in the defining module, so a module can import `dataclass`, `Enum`, or `requests` without those helpers ever reaching a caller. This `__all__` is the single declaration of those names: everything above this package inherits it and must never repeat it.

#### A facade that forwards

It star-imports the *owner* (`from <owner> import *`) and relies on the owner's `__all__` for the boundary:

```python
from example_package.models import *  # forwards example_package/models/__init__.py.__all__
```

The owner's `__all__` bounds what arrives, so a name the owner adds later shows up here automatically and one added to a private helper never does — that is exactly why copying the owner's list into a second `__all__` is wrong: it silently rots the moment the owner changes.

Two things to keep in mind:

- **A star-import also binds the sub-package itself.** `from example_package.models import *` makes `models` an attribute of this package as a side effect of step 3 in [how importing works](#what-__init__py-does--how-importing-works). Without an `__all__` here, a further `import *` would pick that up too.
- **Later star-imports shadow earlier ones.** If two forwarded packages export the same name, the last import silently wins — one more reason for [one owner per name](#the-ownership-question).

If something *does* star-import this facade in turn, it must declare what it forwards, without retyping it:

```python
from example_package.models import *
from example_package.models import __all__ as _models_all

__all__ = list(_models_all)
```

#### A facade that owns *and* forwards

> **NOTE: this is the complex case — avoid it where a simpler split will do.**

The package owns names from its own modules *and* forwards a package below it, and is itself forwarded further up. It is the only case where one `__init__.py` has to do both jobs at once, which is exactly what makes it the one to avoid: the file has two reasons to change, and the `__all__` line stops being a plain list.

**Reach for one of these two instead — both leave every file doing a single job:**

| Instead | What you do | What this file becomes |
|---|---|---|
| **Make the child a [marker](#outcome-1--marker)** | The child (e.g. `example_package.domain_b.interfaces`) exposes nothing; this package imports its contents from their *defining modules* and owns them (e.g. `example_package.domain_b`) | [A facade that owns names](#a-facade-that-owns-names) — one plain `__all__`, no `*` at all |
| **Move this level's own modules down** | Everything this package defines itself moves into a sub-package that owns it, so nothing is left to own here | [A facade that forwards](#a-facade-that-forwards) — only `*` imports |

The *first option* is the usual answer, and it is why a package inside a domain [defaults to a marker](#nested-sub-packages): you rarely need the deeper directory to be nameable, and making it one buys a second import path at the cost of complicating the level above. The *second option* is worth it when this level has grown a mixed bag of loose modules next to sub-packages — that is a layout problem showing up as an `__init__.py` problem.

**See for more details about nested sub-packages and what pattern to choose where: [Nested sub-packages](#nested-sub-packages).**

**If you do want it anyway** — the child really is a surface callers name, *and* this package really does own names of its own — then write it like this. Extend instead of repeating, so the child package stays the single source of truth for its own API:

```python
# Bind: copies the names listed in interfaces.__all__ into this package's namespace,
# so `from example_package.domain_b import SomeInterface` works.
from example_package.domain_b.interfaces import *
# Declare: the child's public API list, reused so it is never retyped here.
# NOTE: This is also required on top of the * import, see explanation below in the table!
from example_package.domain_b.interfaces import __all__ as _interfaces_all
# A name this package owns itself.
from example_package.domain_b.some_module import SomeHelper

# This package's public API: everything interfaces already exports, plus what it owns itself.
__all__ = _interfaces_all + [
    "SomeHelper",
]
```

Both imports of the child are needed, and dropping either one fails in its own way:

| What is written | Effect |
|---|---|
| `import *` **and** `__all__ as _interfaces_all` | ✅ names are reachable here *and* travel further up |
| only `import *` | names are reachable here, but this file's own `__all__` lists only what it owns, so the forwarded ones are dropped by any `import *` one level up |
| only `__all__ as _interfaces_all` | `__all__` promises names that were never bound: `from example_package.domain_b import SomeInterface` raises `ImportError`, and a star-import one level up raises `AttributeError` |
| the child's names retyped by hand | works today, drifts tomorrow — two lists for one API, which is what [one owner per name](#general-principles) forbids |

#### The distribution root

Nothing star-imports the root (`example_package/__init__.py`), so binding is all it has to do and there is nothing left to declare:

```python
from example_package.exceptions import *  # forwards example_package/exceptions.py.__all__
from example_package.models import *      # forwards example_package/models/__init__.py.__all__

# No __all__ here: nothing forwards this package further, so there is nothing to declare.
```

The `__all__` of everything it star-imports already bounds what it exposes, so adding a list here would only be one more place to keep in sync.

### The layout at a glance

A distribution is a tree of `__init__.py` files, each one a [marker](#marker), a [local facade](#local-facade), or an [aggregation facade](#aggregation-facade). The annotations show what each file does, such as (*NOTE: this is just an example, your actual project may vary on the decisions you make regarding which files are facades, markers, or aggregations*):

```
example_package/                  the distribution (import root)
├── __init__.py                   aggregation facade  * of the modules and sub-packages below
├── exceptions.py                 owning module       declares its own __all__ — no __init__.py exists here
├── models/                       shared models, owned by no single domain
│   ├── __init__.py               local facade        owns SharedModel
│   └── shared_model.py           defining module     class SharedModel: ...
├── domain_a/                     a flat domain
│   ├── __init__.py               local facade        owns SomeClient
│   └── some_client.py            defining module     class SomeClient: ...
└── domain_b/                     a deeper domain, several levels of nesting
    ├── __init__.py               local + aggregation owns SomeHelper/SomeRecord, forwards interfaces/
    ├── some_module.py            defining module     class SomeHelper: ...
    ├── interfaces/               a surface callers may name explicitly
    │   ├── __init__.py           local facade        owns SomeInterface
    │   └── some_interface.py     defining module     class SomeInterface(ABC): ...
    ├── models/                   grouping, one module per concern
    │   ├── __init__.py           marker              exposes nothing — owned by example_package.domain_b
    │   └── some_record.py        defining module     class SomeRecord: ...
    └── providers/                nested sub-packages with their own dependencies
        ├── __init__.py           marker              providers are named explicitly, never forwarded
        └── provider_x/           one supplier
            ├── __init__.py       local facade        owns ProviderXClient, not forwarded upwards
            └── some_client.py    defining module     class ProviderXClient(SomeInterface): ...
```

Which gives callers exactly these paths, and no others:

```python
from example_package import SomeClient, SomeInterface, SomeRecord          # convenience entry point: everything forwarded to the root
from example_package.domain_a import SomeClient                            # owner
from example_package.domain_b import SomeHelper, SomeRecord                # owner
from example_package.domain_b import SomeInterface                         # forwarded from interfaces/, which owns it
from example_package.domain_b.interfaces import SomeInterface              # owner
from example_package.domain_b.providers.provider_x import ProviderXClient  # owner, opt-in: supplier named explicitly

from example_package.domain_b.models.some_record import SomeRecord  # ⚠️ works, but reaches into internal wiring — breaks when the file moves
from example_package.domain_b.models import SomeRecord              # ❌ ImportError — marker, nothing is exported here
```

### Top-level package

**The one place where the decision is already made.** The distribution root is the entry point, so everything public must be reachable in one import: `from example_package import SomeClient`. It is always an [aggregation facade](#aggregation-facade) — it star-imports each sub-package and each of its own top-level modules and owns nothing itself. It is also the one `__init__.py` allowed to run code, to attach a `NullHandler` to the package logger (see [Logging](./Logging.md)), and the place where deliberately skipped imports are documented.

**Exception — top-level modules.** A file that sits directly at the root (e.g. `exceptions.py`) has no `__init__.py` of its own, so there is no facade to put its `__all__` in. The owner is then the module itself: it declares `__all__` next to the definitions, and the root forwards it with the same `*` used for sub-packages. The pattern does not change, only the location of the owner:

```python
# example_package/exceptions.py — a top-level module owns its own surface
__all__ = [
    "ExamplePackageError",
]


class ExamplePackageError(Exception):
    """Base exception for everything raised by example_package."""


class _RetryState:  # private and not in __all__: internal helper, never forwarded
    ...
```

The root then forwards that module together with every sub-package, such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Aggregation facade for `example_package`.

It is the distribution root, so everything public has to be reachable from it in a single import.

See <link to this document> for the patterns and rules.

How to use it: callers import from the distribution root instead of reaching into sub-modules:
    from example_package import SomeClient
    from example_package.domain_a.some_client import SomeClient  # not this

What this package is for: forwarding the public surface of every sub-package and top-level module,
and attaching the logging NullHandler. It owns no names and declares no `__all__` of its own, so it
cannot expose anything its owners did not. `example_package.domain_b.providers.*` is deliberately
not forwarded — provider packages pull in supplier-specific dependencies and are named explicitly by
the caller.
"""
import logging

# NullHandler: satisfies Python's requirement that at least one handler exists on the top-level
# package logger, so no "No handlers could be found" warning is emitted when an application has not
# configured logging yet. See docs/design/python/Logging.md#libraries.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Top-level modules — the module itself declares __all__:
from example_package.exceptions import *  # forwards example_package/exceptions.py.__all__

# Sub-packages — each facade declares its own __all__:
from example_package.models import *    # forwards example_package/models/__init__.py.__all__
from example_package.domain_a import *  # forwards example_package/domain_a/__init__.py.__all__
from example_package.domain_b import *  # forwards example_package/domain_b/__init__.py.__all__

# NOTE: example_package.domain_b.providers.* is deliberately not forwarded, see the docstring above.
```

### Nested sub-packages

Everything that is not the root — an internal grouping, a domain sub-package such as `dns/`, an `interfaces/` package, a supplier package — is decided by [the ownership question](#the-ownership-question), and only by that. There is no rule that says "deeper means private": the same directory name can warrant a different pattern in a different distribution, because the supported import path is different.

**Decide one level at a time, top down.** A nested tree is not one decision but one decision per directory, and the answer at one level says nothing about the level below it, such as the below example (*NOTE: this is just an example, your actual project may vary on the decisions you make regarding which files are facades, markers, or aggregations*):

```
example_package/domain_b/                       facade, forwarded      callers name the domain: from example_package.domain_b import ...
example_package/domain_b/models/                marker                 file-per-concern grouping; the records are owned by domain_b
example_package/domain_b/interfaces/            facade, forwarded      "interfaces" is a concept callers depend on by name
example_package/domain_b/providers/             marker                 holds supplier packages only; nothing to forward
example_package/domain_b/providers/provider_x/  facade, NOT forwarded  opt-in: naming the supplier is the point
```

`models/` and `interfaces/` sit at the same depth and get opposite answers, which is the whole point: depth is not the input, the import path you want to support is.

**In practice the levels fall into three shapes:**

| Level | Typical examples | Default | The question that overrides the default |
|---|---|---|---|
| A domain directly under the root | `example_package/dns/`, `example_package/k8s/`, `example_package/utils/` | [facade, forwarded to the root](#outcome-2--local-facade-forwarded-upwards) | Does this domain have a public API at all? If not, it should not be a package of its own. |
| A grouping inside a domain | `example_package/dns/models/`, `example_package/dns/interfaces/`, `example_package/tooling/ops/` | [marker](#outcome-1--marker) | Would I ever tell a caller to name this directory? If yes, promote it to a facade — it is then forwarded *and* nameable, and both paths are supported on purpose. |
| A package with dependencies of its own | `example_package/dns/providers/powerdns/` | [facade, not forwarded](#outcome-3--local-facade-not-forwarded) | Should importing the domain pull these dependencies in? If yes, forward it like any other facade. |

**Two rules of thumb make the choice cheap:**

1. **Start at marker and promote later.** Adding a facade to a package that had none only adds an import path, so no caller breaks. Removing one takes a path away, which does break callers — that asymmetry is why the default for anything below a domain is a marker.
2. **Promote when the directory name is part of how you describe the API.** If the documentation, the examples, or the call site would naturally say "the interfaces of the DNS domain" or "the PowerDNS provider", that directory is a concept callers depend on and deserves its own facade. If it only answers "where did we put this file?", it stays a marker.

The three outcomes, with what each `__init__.py` looks like:

#### Outcome 1 — marker

**The directory is only file organisation.** Its contents are owned by a facade above (can be one or more levels above), which imports them from their *defining modules* (a marker exposes nothing to forward). Giving this package a facade as well would create a second path to the same name, so do not. The file is the docstring shown in [the docstring template](#the-__init__py-docstring-template).

#### Outcome 2 — local facade, forwarded upwards

**The package is a supported surface *and* part of a shorter one.** Callers may use either the owner or the facade above it; the name is still declared once. The file you write is the same [local facade](#local-facade) in both cases below — what differs is **what sits above it**, and therefore what that level has to do to keep forwarding:

| | The package | The level above | What the level above writes |
|---|---|---|---|
| [2.1](#outcome-21--a-domain-directly-under-the-root) | a domain directly under the root (`domain_a/`) | the [distribution root](#the-distribution-root) | a single `import *` — the root declares no `__all__`, so nothing else is needed |
| [2.2](#outcome-22--a-package-nested-inside-a-domain) | a package nested inside a domain (`domain_b/interfaces/`) | a domain facade that owns names *and* is forwarded further up | `import *` **and** `__all__ as _x_all`, see [A facade that owns *and* forwards](#a-facade-that-owns-and-forwards) |

##### Outcome 2.1 — a domain directly under the root

The parent is the root, which owns nothing and declares no `__all__`, so forwarding costs one line and stops there, such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Local facade for `example_package.domain_a`.

The domain is a surface callers name directly, so it owns the clients its own modules define.

See <link to this document> for the patterns and rules.

How to use it: import from this package, or from the distribution root, which forwards it:
    from example_package.domain_a import SomeClient
    from example_package import SomeClient

What this package is for: everything the domain publishes, defined in one module per client. The
modules stay free to move, because this file is the only thing a caller sees.
"""
from example_package.domain_a.some_client import SomeClient

__all__ = [
    "SomeClient",
]
```

```python
# example_package/__init__.py — the whole forward is one line
from example_package.domain_a import *
```

##### Outcome 2.2 — a package nested inside a domain

The package itself looks exactly like 2.1 — it owns what its modules define and declares it, such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Local facade for `example_package.domain_b.interfaces`.

"interfaces" is a concept callers depend on by name, so this package is promoted from a marker to a
surface of its own.

See <link to this document> for the patterns and rules.

How to use it: import from this package, or from the domain facade one level up, which forwards it:
    from example_package.domain_b.interfaces import SomeInterface
    from example_package.domain_b import SomeInterface

What this package is for: the interfaces define the roles of the domain's components independently
of their implementations, so application code can talk to a component generically and
implementations can be swapped. The implementations themselves belong in `providers/`, never here.
"""
from example_package.domain_b.interfaces.some_interface import OtherInterface, SomeInterface

__all__ = [
    "OtherInterface",
    "SomeInterface",
]
```

**The difference is the level above.** `domain_b` is not the root: it owns names of its own *and* is forwarded to the root, so a bare `import *` would leave the interfaces stranded at that level. It has to bind *and* re-declare — see [A facade that owns *and* forwards](#a-facade-that-owns-and-forwards), such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Local *and* aggregation facade for `example_package.domain_b`.

It owns the models and helpers its own modules define, and forwards `interfaces`, which is a surface
callers name in its own right.

See <link to this document> for the patterns and rules.

How to use it: roles, models, and helpers are all reachable from this package in one line:
    from example_package.domain_b import SomeInterface, SomeRecord

What this package is for: the domain, organised by responsibility rather than by supplier:
    interfaces/     the roles callers depend on, forwarded from their own facade
    models/         a marker grouping; the records are owned here
    some_module.py  the helpers shared by every implementation
    providers/      one package per supplier, named explicitly by the caller
Provider packages are deliberately *not* forwarded, so importing this package does not pull in every
supplier's dependencies and it stays obvious at the call site which supplier is used:
    from example_package.domain_b.providers.provider_x import ProviderXClient
"""
# Forwarded surface — the `*` binds the names here, the `__all__` import declares them further
# up; both are needed, see link above for detailed explanation (section: #a-facade-that-owns-and-forwards).
from example_package.domain_b.interfaces import *
from example_package.domain_b.interfaces import __all__ as _interfaces_all

# Owned surface — models/ is a marker, so its contents come from their defining modules:
from example_package.domain_b.models.some_record import SomeRecord
from example_package.domain_b.some_module import SomeHelper

# Only the names this package owns; the forwarded ones stay declared in interfaces/__init__.py.
__all__ = _interfaces_all + [
    "SomeHelper",
    "SomeRecord",
]
```

**Why the default is a `marker` in the [Nested sub-packages top section of this subsection](#nested-sub-packages):** That extra work in the parent is the real price of [2.2](#outcome-22--a-package-nested-inside-a-domain), and the reason the default for a package inside a domain is a [marker](#outcome-1--marker): a marker costs the parent one plain import from a defining module, while a nested facade turns the parent into the [owns-*and*-forwards](#a-facade-that-owns-and-forwards) case for as long as it exists.

#### Outcome 3 — local facade, not forwarded

**An opt-in surface.** A package with dependencies of its own, such as a supplier adapter, is a public surface but is left out of the aggregation above it, so its dependencies are only imported when that supplier is actually used and the call site names it. It is an ordinary [local facade](#local-facade) — the only difference is the absence of a forward one level up, which the docstring has to state so the next reader does not "fix" it, such as (see [template](#the-__init__py-docstring-template)):

```python
"""
Local facade for `example_package.domain_b.providers.provider_x`.

The supplier is an opt-in surface: this package owns its clients but is deliberately NOT forwarded
upwards, so its dependencies are only imported when the supplier is actually used.

See <link to this document> for the patterns and rules.

How to use it: callers name the supplier explicitly, because no facade above forwards this package:
    from example_package.domain_b.providers.provider_x import ProviderXClient

What this package is for: everything supplier-specific — endpoints, payload shapes, authentication.
The clients implement the roles in `example_package.domain_b.interfaces` and return the
provider-neutral models in `example_package.domain_b.models`, so a supplier can be replaced without
a call site changing.
"""
from example_package.domain_b.providers.provider_x.some_client import ProviderXClient

# The only place these names are published: no facade above forwards this package.
__all__ = [
    "ProviderXClient",
]
```

The other half of the pattern is what the parent does *not* write: `example_package/domain_b/__init__.py` has no `from example_package.domain_b.providers... import *` line, and `providers/__init__.py` is a [marker](#outcome-1--marker) that forwards nothing either. So `from example_package.domain_b import ProviderXClient` raises `ImportError` by design, and a consumer who never touches this supplier never imports its dependencies.

---

## Importing from within the package itself

This is the *maintainer's perspective*: code that lives *inside* the distribution. A facade is only free to be reorganised as long as it is never consumed by the code it exports — otherwise it becomes a load-bearing part of the implementation, and moving a class between files breaks the package itself, not just its callers.

### Which path to use

One question decides it: **does the facade I want to import from already import me, directly or through another facade?**

- **Yes** → import from the **defining module**. Everything from a facade down to the modules it exports is one chain; inside that chain imports point downwards only, never back up or sideways through the facade.
- **No** → import from the **owning facade**, exactly the line an external caller would write. This is the position of application code, of tests (which should exercise the surface a consumer gets), and of any sub-package whose chain is separate from yours.

```python
# example_package/domain_b/providers/provider_x/some_client.py
from example_package.domain_b.models.some_record import SomeRecord  # ✅ own chain — the defining module
from example_package.domain_b import SomeRecord                     # ❌ a facade that imports this package
from example_package import SomeRecord                              # ❌ the root facade, same problem

from example_package.domain_a import SomeClient  # ✅ different chain — its facade does not import us
from example_package.models import SharedModel   # ✅ shared models — same reasoning
```

Importing another sub-package through its facade is the *preferred* form: short, stable, and identical to the line an external caller writes, so there is no second import style for code that happens to ship in the same distribution. It works because the dependency runs one way only — keep that direction deliberate, as two sub-packages importing each other's facades is a real cycle and usually means a shared type is in the wrong place.

### Why apply this even when Python does not fail

Importing your own facade from below often *appears* to work: a package being imported is registered in `sys.modules` while it is still initialising, so the import is frequently satisfied from that half-finished module. It fails only when the name is read before the facade has assigned it — which depends on which module the process imports first, something a library cannot control. Apply the rule structurally, not as a fix for an error you have already seen:

- The failure mode is an `ImportError`/`AttributeError` at import time in an unrelated part of the codebase, triggered by a change that touched neither module.
- Whether it fails differs per entry point, so an application, a script, and the test suite can disagree about whether the package imports at all.
- The facade stops being safe to reorganise, which is the entire reason it exists.

### Circular imports and how to break them

A circular import is two or more modules that import each other, directly or through an `__init__.py`. Since `__init__.py` is the *leaf importer* — it imports from the modules below it, never the other way around — importing a facade from one of its own modules closes a loop:

```
example_package/domain_b/__init__.py       imports  interfaces/some_interface.py
interfaces/some_interface.py               imports  example_package.domain_b    ← back to the facade
```

Such a cycle can sit unnoticed until an unrelated change alters the import order, so verify it statically instead of trusting that imports currently succeed — see [Checking circular imports](./StaticCodeAnalysis.md#checking-circular-imports).

**Three fixes exist, and they are tried in this order — the first one resolves nearly every cycle a linter reports:**

| # | Fix | Use it when | Cost |
|---|---|---|---|
| 1 | [Import from the defining module](#fix-1--import-from-the-defining-module) | A module imports a facade that sits above it in its own chain — the default case | None; it is the import the module should have written anyway |
| 2 | [Give the shared concept a proper owner](#fix-2--give-the-shared-concept-a-proper-owner) | The cycle spans several modules or packages, so no single import is "the wrong one" | A layout change, but it removes the whole class of cycles |
| 3 | [Import only for type checking](#fix-3--import-only-for-type-checking) | The import exists purely for annotations, and 1 and 2 do not apply | Hides the design problem instead of fixing it — last resort |

#### Fix 1 — import from the defining module

**Replace the facade import with an import of the module where the name is actually defined**, see [Which path to use](#which-path-to-use).

Why this works: the facade is the *leaf importer* of its own chain, so it is always loaded *after* the modules it exports. A module that imports its own facade therefore waits on a module that is waiting on it, while the defining module sits below it in the same chain and has no import of its own that points back up. Replacing the path removes the edge that closes the loop, and nothing about the public API changes — external callers keep importing from the facade.

```python
# example_package/domain_b/interfaces/some_interface.py
from example_package.domain_b import SomeRecord                     # ❌ the facade imports this module — cycle
from example_package.domain_b.models.some_record import SomeRecord  # ✅ the defining module, one level down
```

#### Fix 2 — give the shared concept a proper owner

**Reconsider the package design when the cycle spans multiple modules or packages.** A cycle that long is rarely one bad import; it is a symptom that a type, an abstraction, or a responsibility is owned by the wrong package, so packages depend on each other instead of following one clear direction. Example:

```text
example_package.metrics
    ↓
example_package.models.result
    ↓
example_package.models
    ↓
example_package.models.check
    ↓
example_package.models.test
    ↓
example_package.models.service_context
    ↓
example_package.metrics
```

Here several runtime abstractions (`Check`, `Test`, `ServiceContext`) were put in `models/` even though they carry framework *behaviour* rather than data, so `models/` ended up depending on `metrics/` — which depends on `models/`. Moving them into a package that owns runtime behaviour restores a one-way dependency:

```text
example_package/
├── models/     shared data structures
├── runtime/    runtime abstractions and execution logic
└── utils/      shared utility helpers
```

Data, runtime behaviour, and utilities become distinct layers, each depending only on the layer below it, which removes this class of cycle by design rather than per import. Now each layer has one job and the dependency direction stays one-way (e.g. `bootstrap` → `runtime` → `models`/`utils`). 

**This illustrates that redesigning into a proper package ownership and clear layering can prevent import cycles and maintain a clean, one-way dependency structure.**

#### Fix 3 — import only for type checking

**Use `if typing.TYPE_CHECKING:` with a string annotation when the import exists purely for annotations** (see the [official Python docs on `TYPE_CHECKING`](https://typing.python.org/en/latest/spec/directives.html#type-checking) and on [`__future__`](https://docs.python.org/3/library/__future__.html)). The import disappears at runtime and the cycle with it, but the design problem stays — so reach for this only after 1 and 2 are ruled out (prefer [option 2: Design for proper package ownership and layering](#fix-2--give-the-shared-concept-a-proper-owner)).

```python
# Store annotations as strings instead of resolving them immediately.
from __future__ import annotations

from typing import TYPE_CHECKING

# Only imported by type checkers; skipped at runtime.
if TYPE_CHECKING:
    from example_package.a import A
```