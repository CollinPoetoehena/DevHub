# Class & Generics

This document describes the class, inheritance, and generics in Python.

All packages should follow the best practices/conventions from Python itself:

- [Classes](https://docs.python.org/3/tutorial/classes.html) — attributes, inheritance, scope, private conventions.
- [PEP 8 — Class Names](https://peps.python.org/pep-0008/#class-names) and [Designing for Inheritance](https://peps.python.org/pep-0008/#designing-for-inheritance) — naming and public/private surface.
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) — value objects without boilerplate.
- [`abc`](https://docs.python.org/3/library/abc.html) — abstract base classes.
- [`typing`](https://docs.python.org/3/library/typing.html) — [`TypeVar`](https://docs.python.org/3/library/typing.html#typing.TypeVar), [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic), [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol), [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar).
- [Type hints for generics — `typing` HOWTO](https://typing.python.org/en/latest/reference/generics.html) — the reference for the generics rules summarised below.

Only the conventions that need extra attention, or that are specific to this codebase, are documented below.

## Table of Contents

- [General principles](#general-principles)
- [Choosing the right kind of class](#choosing-the-right-kind-of-class)
  - [Why a class instead of a `Dict`](#why-a-class-instead-of-a-dict)
  - [Data classes](#data-classes)
  - [Class-level constants — `ClassVar`](#class-level-constants--classvar)
- [Constructors](#constructors)
  - [`__init__` does the minimum](#__init__-does-the-minimum)
  - [Alternative constructors instead of mode flags](#alternative-constructors-instead-of-mode-flags)
- [Methods](#methods)
  - [Instance vs `classmethod` vs `staticmethod` vs module-level function](#instance-vs-classmethod-vs-staticmethod-vs-module-level-function)
  - [Properties instead of getters and setters](#properties-instead-of-getters-and-setters)
- [Inheritance](#inheritance)
  - [Composition over inheritance](#composition-over-inheritance)
  - [Abstract base classes (`ABC`) — nominal contracts](#abstract-base-classes-abc--nominal-contracts)
  - [`Protocol` — structural contracts](#protocol--structural-contracts)
  - [`ABC` vs `Protocol`](#abc-vs-protocol)
- [Generics](#generics)
  - [When a generic is worth it](#when-a-generic-is-worth-it)
  - [`TypeVar` — one type, used consistently](#typevar--one-type-used-consistently)
  - [Bounded and constrained type variables](#bounded-and-constrained-type-variables)
  - [Generic classes](#generic-classes)
  - [Returning "the same class" — `Self`](#returning-the-same-class--self)
  - [Variance — why `List[Child]` is not a `List[Parent]`](#variance--why-listchild-is-not-a-listparent)
  - [When *not* to use a generic](#when-not-to-use-a-generic)
- [Type aliases](#type-aliases)

---

## General principles

- **One responsibility per class.** A class models one thing: a value, a client, a service. If the docstring needs "and", it is probably two classes.
- **`CapWords` for class names, and the name states what it *is*.** `HTTPClient`, `RetryPolicy`, `UserRecord` — a noun, not a verb ([PEP 8](https://peps.python.org/pep-0008/#class-names)).
- **Type hint every attribute, parameter, and return value.** The annotations are the contract; they are what makes the class checkable by tooling.
- **Class docstring with `Attributes`, method docstrings with `Args` / `Returns` / `Raises`.** Explain *why*, not what the next line already shows.
- **Prefix implementation details with `_`.** The public surface stays small and intentional; helpers and internal state are private.
- **Prefer immutability for data.** A frozen value object cannot be mutated by accident by a caller three layers away.
- **Do not add a class where a function will do.** A class with one method and no state is a function with extra steps.
- **Logging.** Use one logger per class where a class hierarchy needs it; see [Logging](./Logging.md).
- **Exception/error handling.** Error handling is centralised and documented in [Exceptions](./Exceptions.md).
- **Functions.** The rules in [Functions](./Functions.md) apply to methods as well.

---

## Choosing the right kind of class

| You need... | Use | Why |
|---|---|---|
| A value object: fields, equality, no behaviour | `@dataclass(frozen=True)` | Free `__init__`, `__repr__`, `__eq__`, and immutability |
| A value object that must be hashable and tuple-like | `NamedTuple` | Immutable, indexable, cheap; only when tuple semantics are actually wanted |
| A fixed set of named values | `Enum` / `StrEnum` | Type-checked constants instead of magic strings |
| The *shape of an external `Dict`* (e.g. a JSON payload) | `TypedDict` | Annotates a dict you do not own; no runtime object is created |
| Behaviour plus state (clients, services, sessions) | Plain class with `__init__` | Explicit construction and validation |
| A contract that implementations must fulfil | `ABC` or `Protocol` | See [Inheritance](#inheritance) |

### Why a class instead of a `Dict`

Passing raw dictionaries around is the most common way a codebase loses its type safety. A dedicated class is worth the extra file:

- **Centralisation & Maintainability.** Changes are isolated to a single central place. If the upstream payload changes, only the class and its conversion logic (e.g. `to_dict` and `from_dict`) need to be updated, while the rest of the codebase continues to work unchanged. This provides a central location for implementing future changes, validation, normalisation, and enhancements. In contrast, with plain dictionaries, every direct key access (e.g. `payload["some"]["key"]`) throughout the codebase becomes a potential change point, increasing maintenance effort and the risk of inconsistencies.
- **Type safety.** The fields and their types are declared once and checked everywhere. Dictionaries, in contrast, require the developer to remember the expected keys and their types at every usage point, which is error-prone and not checked by static type checkers.
- **Immutability.** `frozen=True` prevents accidental mutation by unrelated code.
- **Documentation**: The class and its attributes can be documented clearly, improving code readability.
- **Discoverability & IDE support**: Autocompletion, go-to-definition, and documentation work on attributes; they do not work on string keys. Furthermore, autocompletion and type checking work better with explicit classes than with generic dictionaries.
- **Consistency.** One representation of the concept across the codebase, instead of "whatever this particular function happened to build".

```python
# ❌ The shape is implicit, unchecked, and duplicated at every call site
def render(item: Dict[str, Any]) -> str:
    return f"{item['name']} ({item['size']})"

# ✅ The shape is declared once and checked everywhere
@dataclass(frozen=True)
class Item:
    name: str
    size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        # NOTE: .get() is used here because it is safer since it handles missing keys gracefully instead of raising 
        # an exception (returns None on empty/not present keys), and it supports default values.
        return cls(
            name=data.get("name", ""),
            size=data.get("size", 0),
        )

def render(item: Item) -> str:
    return f"{item.name} ({item.size})"
```

Keep the conversion in one place — a `classmethod` on the class itself (see [Alternative constructors](#alternative-constructors-instead-of-mode-flags)).

**When to avoid adding a data class on top of a plain dictionary:** In some cases, it may be better to skip creating a dedicated class and use plain dictionaries directly to avoid unnecessary boilerplate and complexity (only these specific situations, the other cases warrant a dedicated data class as explained above):
- **Highly dynamic or rarely used structures.** If the structure is highly dynamic, rarely used, or the overhead of defining a class outweighs the benefits, it may be better to stick with plain dictionaries. For example, a temporary configuration object or a one-off API response that is not central to the application's logic could take some effort to create a data class for little gain (e.g. it is only used once throughout the codebase).
- **Data classes already exist for the structure.** If a suitable data class is already defined and widely used somewhere else, creating another one for the same structure may lead to redundancy and confusion. In such cases, it is better to reuse the existing data class rather than defining a new one. For example, in the `kubernetes` Python package, there is already a data class/type for all objects like `V1Pod` representing a pod, so creating another class for the same purpose would be unnecessary and it could introduce inconsistencies. In these cases, prefer using the existing data class.

### Data classes

```python
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Item:
    """
    A single item in a collection.

    Attributes:
        name: Unique name of the item
        size: Size in bytes
        tags: Labels attached to the item; empty when none are set
        owner: Owner of the item, when the source provides one
    """
    name: str
    size: int
    tags: List[str] = field(default_factory=list)
    owner: Optional[str] = None
```

Conventions:

- **`frozen=True` by default** for data that is read, passed around, and compared. Drop it only when a field genuinely has to change in place, and document why.
- **Never use a mutable default.** `tags: List[str] = []` is a shared-state bug; `field(default_factory=list)` creates a new list per instance ([`dataclasses.field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)).
- **Fields with defaults come last**, otherwise the generated `__init__` is invalid.
- **Validate in `__post_init__`**, not in the caller:

  ```python
  def __post_init__(self) -> None:
      if self.size < 0:
          raise ValueError(f"size must be >= 0, got {self.size}")
  ```

- **Only add a custom `__repr__`/`__eq__` when the generated one is wrong** (e.g. a field holds a secret, or a large payload that should not end up in logs).
- **Avoid behaviour beyond the data.** Conversion (`from_api(...)`, `to_payload()`) and derived values (`@property`) belong on the model; business logic does not.

### Class-level constants — `ClassVar`

An annotated class attribute that is *not* per-instance state must be marked `ClassVar`, otherwise a dataclass turns it into a field:

```python
from typing import ClassVar


@dataclass
class Client:
    DEFAULT_TIMEOUT: ClassVar[int] = 30   # class-level default, not a constructor argument
    host: str
```

Use it for defaults and constants that subclasses may override. Do not use it for shared *mutable* state — that is global state with a class-shaped wrapper.

---

## Constructors

### `__init__` does the minimum

`__init__` assigns state and validates it. It does not do I/O, does not open connections, and does not perform work that can fail for environmental reasons — those belong in an explicit method or an alternative constructor, so a caller can decide when they happen and handle the failure.

```python
class Client:
    def __init__(self, transport: Transport, timeout: int = DEFAULT_TIMEOUT):
        """
        Args:
            transport: Transport used for every request this client makes
            timeout: Per-request timeout in seconds

        Raises:
            ValueError: If no transport is provided
        """
        if transport is None:
            raise ValueError(f"A transport must be provided for {self.__class__.__name__}")
        self.transport = transport
        self.timeout = timeout
```

- **Fail fast and clearly.** An invalid object should not exist; raise at construction rather than at the first method call.
- **Include the class name in constructor errors.** `self.__class__.__name__` gives the *actual* subclass, which is what the reader needs.
- **Keep the parameter list about the object, not about the environment.** Reading configuration files or resolving service discovery is the job of a factory, not of `__init__`.

### Alternative constructors instead of mode flags

The same reasoning as [Functions with multiple return types](./Functions.md#functions-with-multiple-return-types) applies to construction: a flag that changes *how* an object is built forces every reader to look up an unrelated boolean before they know what they have.

❌ **One constructor with a mode flag:**

```python
client = Client(source="config.yaml", from_file=True)   # what does `source` mean here?
```

✅ **Named `classmethod` factories, one per source:**

```python
class Client:
    @classmethod
    def from_url(cls, url: str, **kwargs) -> "Client":
        """Build a client for a service that is reachable at a known URL."""
        return cls(HTTPTransport(url), **kwargs)

    @classmethod
    def from_config_file(cls, path: str, **kwargs) -> "Client":
        """Build a client from a configuration file on disk."""
        return cls(HTTPTransport(_read_url(path)), **kwargs)
```

**Why:**

- **The name carries the meaning.** `Client.from_config_file(path)` needs no explanation.
- **`cls`, not the hard-coded class.** Returning `cls(...)` means a subclass gets an instance of *itself* from the inherited factory.
- **Each factory documents and validates its own inputs**, instead of one docstring describing several mutually exclusive modes.
- **`__init__` stays the single, boring place where state is assigned**, which keeps the invariants in one location.

The same pattern is the right home for `Dict` → model conversion:

```python
@classmethod
def from_api_payload(cls, payload: Dict[str, Any]) -> "Item":
    """Build the model from one entry of the upstream API response."""
    return cls(name=payload["name"], size=int(payload["size"]))
```

---

## Methods

### Instance vs `classmethod` vs `staticmethod` vs module-level function

| The method... | Use | Note |
|---|---|---|
| uses `self` (instance state) | instance method | The default |
| builds or inspects the class itself | `@classmethod` | Alternative constructors, class-level defaults; use `cls`, never the literal class name |
| uses neither `self` nor `cls`, but belongs to the class conceptually | `@staticmethod` | E.g. a pure parser/formatter that is meaningless outside this class |
| uses neither, and is useful on its own | module-level function | Do not attach a general helper to a class just to give it a home |

Logging inside `classmethod`/`staticmethod` has its own pattern — see [Logging](./Logging.md#exception-3--class-methods-and-static-methods).

### Properties instead of getters and setters

Python has no need for `get_x()`/`set_x()` pairs — start with a plain attribute, and promote it to a `@property` only when access needs logic:

```python
class Connection:
    @property
    def is_open(self) -> bool:
        """Whether the underlying socket is currently usable."""
        return self._socket is not None and not self._socket.closed
```

- **A property must be cheap and side-effect free.** If it does I/O, retries, or anything that can fail for environmental reasons, it should be a method — the call parentheses are the reader's only warning that work happens.
- **Do not add a setter just for symmetry.** A read-only property is a deliberate statement that the value is derived.

---

## Inheritance

### Composition over inheritance

Inherit to express *"is a"*, and only when the subclass genuinely fulfils the parent's contract. Everything else — reuse, configuration, decoration — is composition:

```python
# ❌ Inheritance used for reuse: Client is not a Session
class Client(Session):
    ...

# ✅ Composition: Client *has* a session
class Client:
    def __init__(self, session: Session):
        self.session = session
```

**Why:** a base class is a permanent, public coupling — every protected attribute becomes part of the contract, and a change to the base ripples into every subclass. A composed dependency can be swapped, mocked, and reasoned about in isolation.

When a base class *is* the right answer (shared behaviour across genuinely related types):

- **Keep the base class abstract or clearly documented as a base.** Prefix it with `Base` only when there is more than one implementation.
- **Document what subclasses must override**, and enforce it with `@abstractmethod` where possible.
- **Prefer shallow hierarchies.** Two levels is usually plenty; deeper hierarchies hide where behaviour actually comes from.
- **Do not reach into parent internals.** If a subclass needs `self._something` from the base, that member is part of the contract and should be documented as such.

### Abstract base classes (`ABC`) — nominal contracts

Use an `ABC` when this codebase owns both the contract and its implementations, and callers should depend on the contract:

```python
from abc import ABC, abstractmethod
from typing import List


class Repository(ABC):
    """Read-only access to stored items, independent of where they are stored."""

    @abstractmethod
    def get(self, name: str) -> Item:
        """
        Return one item by name.

        Raises:
            ItemNotFoundError: If no item with that name exists
        """

    @abstractmethod
    def list_all(self) -> List[Item]:
        """Return every item in the store."""
```

- **The interface declares only what every implementation can honestly provide.** Anything one backend alone supports stays on that implementation's own class, not on the interface.
- **The interface owns the docstrings**, including which exceptions callers must handle. Implementations describe *how*, not *what*.
- **Instantiating an incomplete subclass fails at construction**, which is exactly the early failure that is wanted.

### `Protocol` — structural contracts

Use a `Protocol` when the implementer cannot (or should not) inherit from your class — third-party types, callables, or "anything that has these methods":

```python
from typing import Protocol


class SupportsClose(Protocol):
    def close(self) -> None: ...


def shutdown(resource: SupportsClose) -> None:
    resource.close()
```

Any object with a matching `close()` satisfies this — no inheritance, no import of your package. This is duck typing made checkable.

### `ABC` vs `Protocol`

| | `ABC` | `Protocol` |
|---|---|---|
| Relationship | Nominal — must subclass | Structural — must match the shape |
| Implementers | Types you own | Any type, including third-party |
| Enforcement | At runtime (instantiation fails) | At type-check time only |
| Shared code | Can provide concrete methods | Should not (keep it a shape) |
| Use for | The main abstractions of a package | Narrow capability requirements on inputs |

Default to `ABC` for the package's own abstractions; use `Protocol` for parameter types where you only care about a capability.

---

## Generics

A generic is a class or function that is **parameterised by a type**, so the same implementation works for many types *without* losing type information. The alternative — `Any` — works at runtime and tells the reader and the type checker nothing.

### When a generic is worth it

Use a generic when **the same code operates on a type it does not care about, and the caller's type must survive the round trip**:

```python
# ❌ The type is lost: every call site needs a cast or a comment
def first(items: List[Any]) -> Any: ...

value = first(users)   # what is `value`? Any. So: no checking, no autocompletion.

# ✅ The type flows through
T = TypeVar("T")

def first(items: List[T]) -> T: ...

value = first(users)   # `User` — inferred, checked, autocompleted
```

If the caller's type does not need to come back out, you do not need a generic.

### `TypeVar` — one type, used consistently

A `TypeVar` means "some type, decided at the call site, and the *same* type everywhere it appears in this signature":

```python
from typing import Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def first_or_none(items: List[T]) -> Optional[T]:
    """Return the first item, or None when the collection is empty."""
    return items[0] if items else None


def group_by_key(items: List[V], key: Callable[[V], K]) -> Dict[K, List[V]]:
    """Group items by the key returned for each of them."""
    ...
```

Conventions:

- **Name it for what it stands for.** `T` for a single unconstrained type is idiomatic; use meaningful names (`ModelT`, `KeyT`) when several appear in one signature.
- **Declare it at module level**, once, next to the code that uses it.
- **A `TypeVar` used only once in a signature is a code smell** — it is usually just `Any` in disguise, or a sign that a bound is missing.

### Bounded and constrained type variables

```python
# bound=: any subclass of Model
ModelT = TypeVar("ModelT", bound="Model")

# constraints: exactly one of these types
NumberT = TypeVar("NumberT", int, float)
```

- **`bound=`** — "T is a `Model` or a subclass of it". Inside the function you may use everything `Model` offers, and the caller still gets their exact subclass back. This is the common case.
- **Constraints** — "T is exactly `int`, or exactly `float`, and nothing else". Use sparingly; a union parameter is usually clearer unless the return type must match the argument.

```python
def parse_all(payloads: List[Dict[str, Any]], model: Type[ModelT]) -> List[ModelT]:
    """Convert raw payloads into instances of the requested model type."""
    return [model.from_payload(payload) for payload in payloads]

items = parse_all(raw, Item)   # List[Item] — not List[Model], not List[Any]
```

### Generic classes

A class becomes generic by inheriting `Generic[T]`; the type parameter is then usable across all of its methods:

```python
from typing import Dict, Generic, Iterable, Optional, TypeVar

T = TypeVar("T")


class Cache(Generic[T]):
    """
    In-memory cache of values of a single type.

    Attributes:
        max_size: Maximum number of entries kept before the oldest is evicted
    """

    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._entries: Dict[str, T] = {}

    def get(self, key: str) -> Optional[T]:
        """Return the cached value, or None when the key is not cached."""
        return self._entries.get(key)

    def put(self, key: str, value: T) -> None:
        """Cache a value under the given key."""
        self._entries[key] = value
```

```python
cache: Cache[Item] = Cache()
cache.put("a", item)
cache.get("a")        # Optional[Item]
cache.put("b", 42)    # ❌ type error, caught before it ships
```

Notes:

- **Python 3.12+ has the shorter [PEP 695](https://peps.python.org/pep-0695/) syntax** (`class Cache[T]:`). Use it only if every consumer of the package is on 3.12+; otherwise stay with `Generic[T]`, which works on all supported versions (see `requires-python` in the package's [`pyproject.toml`](./README.md#pyprojecttoml)).
- **A generic base class can pin its parameter for a concrete subclass**: `class ItemCache(Cache[Item]):` — the subclass is no longer generic, and all inherited methods are typed to `Item`.
- **Type parameters are erased at runtime.** `Cache[Item]` performs no checking when the program runs; generics are a static contract, so keep runtime validation where the data enters the system.

### Returning "the same class" — `Self`

Methods that return an instance of their own class (builders, fluent APIs, alternative constructors) should say so, otherwise a subclass loses its type:

```python
# Python 3.11+
from typing import Self

class Query:
    def where(self, condition: str) -> Self:
        ...
        return self
```

```python
# Older versions: a bound TypeVar achieves the same
QueryT = TypeVar("QueryT", bound="Query")

class Query:
    def where(self: QueryT, condition: str) -> QueryT:
        ...
        return self
```

Returning the hard-coded `"Query"` instead would type `SubQuery().where(...)` as `Query`, silently dropping the subclass's own methods.

### Variance — why `List[Child]` is not a `List[Parent]`

This is the rule that surprises people most often:

```python
def add_default(items: List[Parent]) -> None:
    items.append(Parent())     # legal for List[Parent]...

children: List[Child] = [...]
add_default(children)          # ❌ rejected — and rightly so: it would insert a Parent into a List[Child]
```

Mutable containers are **invariant**: `List[Child]` is not compatible with `List[Parent]`, because writing through the wider type would corrupt the narrower one.

**The practical rule:** type parameters *accepted* by a function should be as general as the function actually needs.

- Accept `Iterable[T]` or `Sequence[T]` (read-only, covariant) when you only read.
- Accept `List[T]` only when you genuinely mutate the caller's list.

```python
# ✅ accepts List[Child], Tuple[Child, ...], a generator, ...
def summarise(items: Iterable[Parent]) -> str: ...
```

The same applies to return types: return the concrete type (`List[Item]`), accept the abstract one (`Iterable[Item]`).

### When *not* to use a generic

- **One implementation, one type.** If only `Cache[Item]` will ever exist, write `ItemCache` — KISS wins.
- **The type parameter appears once.** It carries no information; the parameter is just `object`/`Any` with ceremony.
- **The behaviour differs per type.** If the class needs `isinstance` branches on `T`, the types are not interchangeable and you want separate classes or an [interface](#abstract-base-classes-abc--nominal-contracts).
- **Runtime validation is the real requirement.** Generics are erased at runtime; they will not validate a payload for you.

---

## Type aliases

Give a name to any type that is long, repeated, or meaningful in the domain:

```python
from typing import Any, Dict, List, Union

JSON = Union[Dict[str, Any], List[Any]]
Headers = Dict[str, str]
```

- **Alias for meaning, not for brevity alone.** `Headers` explains something; `D = Dict[str, str]` does not.
- **Define aliases next to the types they describe** and export them with the module's `__all__`, so callers can annotate their own code with the same names (see [`__init__.py` — Package Initialisation](./README.md#__init__py--package-initialisation)).
- **An alias is not a new type.** For values that must not be mixed up (e.g. two different kinds of ID), use [`NewType`](https://docs.python.org/3/library/typing.html#newtype) instead.
