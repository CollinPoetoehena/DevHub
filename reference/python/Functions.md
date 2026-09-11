# Function Design

This document describes the function and method design used in Python.

All packages should follow the best practices/conventions from Python itself:

- [Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) and [More on Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions) — arguments, defaults, keyword arguments, `*args`/`**kwargs`.
- [PEP 8 — Function and Variable Names](https://peps.python.org/pep-0008/#function-and-variable-names) and [Function Annotations](https://peps.python.org/pep-0008/#function-annotations) — naming and type hints.
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — what a docstring must state.
- [`typing`](https://docs.python.org/3/library/typing.html) — type hints, including [`typing.overload`](https://docs.python.org/3/library/typing.html#typing.overload) used below.

**Only the conventions that need extra attention, or that are specific to this codebase, are documented below.**

## Table of Contents

- [General principles](#general-principles)
- [Functions with multiple return types](#functions-with-multiple-return-types)
  - [Rule of thumb](#rule-of-thumb)
  - [Why a return-shape flag is a problem](#why-a-return-shape-flag-is-a-problem)
  - [Option 1 — split into two functions (preferred)](#option-1--split-into-two-functions-preferred)
  - [Option 2 — `typing.overload`](#option-2--typingoverload)
  - [Unions that are fine](#unions-that-are-fine)

---

## General principles

- **One responsibility per function.** A function does one thing; if the docstring needs "and", it is probably two functions.
- **The name states the result.** `get_pods()`, `build_base_url()`, `classify_auth_pods()` — a reader should know what comes back without reading the body.
- **Type hint every public parameter and return value.** The type hint is part of the contract and is what makes the API checkable by tooling ([PEP 8](https://peps.python.org/pep-0008/#function-annotations)).
- **Docstring with `Args` / `Returns` / `Raises`.** Explain *why*, not what the next line already shows.
- **No mutable default arguments.** Use `None` and build the value inside the function (see [Default Argument Values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)).
- **Pass booleans and optional flags by keyword at the call site** (`persistent=False`, not a bare `False`), so the meaning is visible where it is used.
- **Prefix implementation details with `_`.** Public API stays small and intentional; shared internals are private helpers.
- **Logging.** Logging is centralised and documented in [Logging](./Logging.md).
- **Exception/error handling.** Error handling is centralised and documented in [Exceptions](./Exceptions.md).
- **Classes & Generics.** These rules apply to methods too; class-specific conventions are documented in [Classes & Generics](./Classes_Generics.md).

---

## Functions with multiple return types

A function that can return more than one type (`Union[...]`) is not automatically wrong — it depends on *what decides* the type. The problem case is a parameter that changes the **shape of the return value**, because the caller then has to know the semantics of an unrelated flag to know what they are holding.

### Rule of thumb

| A parameter changes... | Do this | Examples |
|---|---|---|
| only **behaviour** — the return type stays the same | ✅ keep it as a flag/parameter | `verbose=True`, `verify_ssl=False`, `persistent=False`, `follow_redirects=True` |
| the **shape or type of the return value** | ✅ split into separate functions (or use overloads) | `stream=True` → `Response` vs parsed JSON, `as_typed_dict=True` → `Dict` vs `List` |

Good, self-describing names:

```python
# Good examples of function signatures with clear return types
# Pods:
get_pods() -> List[Pod]
get_pods_by_type() -> Dict[Type, List[Pod]]
# Loading content
load_json() -> JSON
load_yaml() -> YAML
# Making a request:
make_request() -> requests.Response
make_stream_request() -> requests.Response # NOTE: Here it is returned streaming.
```

Less ideal, because one call site has multiple behaviours hidden behind a boolean:

```python
get_pods(as_typed_dict=True)
load(file, yaml=True)
make_request(stream=True)
```

### Why a return-shape flag is a problem

```python
pods = get_pods(client, AUTH)   # What is `pods`? A list? A dict?
```

The only way to answer that is to look up an unrelated boolean argument elsewhere in the call:

1. **Unreadable at the call site.** `pods = get_pods(client, AUTH, as_typed_dict=True)` requires the reader to remember what the flag does before they know what the variable holds.
2. **Unusable for type checkers.** The inferred type is the full union, so every call site needs narrowing or a `cast()` even though the shape is statically known from the literal argument.
3. **Two functions in one docstring.** `Returns` has to describe both modes, and the body grows branches (`return x if flag else y`) that have nothing to do with the actual work.

### Option 1 — split into two functions (preferred)

Two public functions, one shared private implementation. Use this whenever the variants differ **only in internal processing** while the call itself stays the same — the shared work lives in the private helper, and each public function only shapes the result:

```python
def _fetch_document(source: str, timeout: int, stream: bool) -> Response:
    """Shared implementation: connect, validate the status, translate errors — identical for both variants."""
    ...

def fetch_document(source: str, timeout: int = 5) -> Dict[str, Any]:
    """Return the fully parsed document."""
    return _fetch_document(source, timeout, stream=False).json()

def fetch_document_stream(source: str, timeout: int = 5) -> Response:
    """Return the open response so the body can be read incrementally."""
    return _fetch_document(source, timeout, stream=True)
```

**Why this is preferred:**
- **Simplicity (KISS).** Keep it simple, stupid (KISS) — each function does one thing, making the code easier to reason about.
- **Clear separation of concerns.** Each function has a single responsibility, making the code easier to understand and maintain.
- **The name carries the meaning.** `fetch_document_stream(...)` says what comes back; no flag has to be remembered or looked up.
- **One return type per function**, so type checkers, editors, and readers all agree without narrowing.
- **No duplication.** Everything the variants share stays in the private helper, so the split costs a signature, not a second implementation.
- **Each variant documents and evolves on its own terms** (e.g. streaming can document that the caller must close the response, without that note polluting the parsed-JSON case).

#### Accepted Trade-off: duplicated signatures vs duplicated implementations
The split-function approach may duplicate the public signature:
```python
def fetch_document(source: str, timeout: int = 5) -> Dict[str, Any]:
    ...

def fetch_document_stream(source: str, timeout: int = 5) -> Response:
    ...
```
**This is usually acceptable because only the interface is duplicated, not the implementation.** This is generally considered acceptable because it duplicates only the **interface**, not the **implementation**. You should generally follow *DRY (Don't Repeat Yourself)*, but it should not come at the cost of making the public API less clear or harder to use. So, for the interface/parameter list, a small amount of duplication is acceptable. Furthermore, clear function names and predictable return types are usually more valuable than avoiding a duplicated signature.

❌ **Avoid implementation duplication:**
```python
def fetch_document(...):
    response = requests.get(...)
    validate_status(...)
    handle_errors(...)

def fetch_document_stream(...):
    response = requests.get(...)
    validate_status(...)
    handle_errors(...)
```

✅ **Prefer interface duplication with shared implementation:**
```python
def fetch_document(...):
    return _fetch_document(..., stream=False).json()

def fetch_document_stream(...):
    return _fetch_document(..., stream=True)
```

**The shared logic still exists in exactly one place**, so there is no maintenance overhead from duplicated behaviour.

### Option 2 — `typing.overload`

Keeps the existing signature (useful when it cannot be changed without breaking callers) and restores type inference:

```python
from typing import Literal, overload

@overload
def get_pods(client: Client, types: Types, as_typed_dict: Literal[False] = False) -> List[Pod]: ...

@overload
def get_pods(client: Client, types: Types, as_typed_dict: Literal[True]) -> Dict[Type, List[Pod]]: ...

def get_pods(client: Client, types: Types, as_typed_dict: bool = False):
    ...
```

The type checker now infers `List[Pod]` for `get_pods(client, types)` and `Dict[Type, List[Pod]]` for `get_pods(client, types, as_typed_dict=True)`. This is a large improvement, but the runtime function still does two things and the call site still reads as a flag.

### Unions that are fine

- **Input convenience unions.** A parameter accepting "one or many" is a normal, idiomatic pattern, provided the function normalises it immediately and the rest of the body deals with one type only:

  ```python
  ComponentTypes = Union[ComponentType, Iterable[ComponentType]]   # caller may pass one value or a list

  def get_pods(client: Client, types: ComponentTypes) -> List[Pod]:
      requested_types = _normalize_component_types(types)          # everything below works on List[ComponentType]
  ```

  The union is a convenience at the boundary, not a second mode: the return type is unaffected.

- **Return unions the caller cannot choose.** When the variation comes from the data rather than from an argument (e.g. a JSON body that is an object, an array, or absent → `Optional[Union[Dict[str, Any], List[Any]]]`), splitting the function would not help: the same call can legitimately produce either, and no flag is hiding it.
