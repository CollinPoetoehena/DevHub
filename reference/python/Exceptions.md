# Exception Design

This document describes the exception design used across all `devhub_*` packages.

All packages should follow the best practices/conventions from Python, see [Python Errors and Exception Documentation](https://docs.python.org/3/tutorial/errors.html) for best practices and documentation.

Patterns that need extra attention or specific information to this codebase are documented below:

## Table of Contents

- [Pattern: built-in Python exception chaining](#pattern-built-in-python-exception-chaining)
  - [Why BaseChainedException was removed](#why-basechainedexception-was-removed)
- [Pattern: per-package exceptions](#pattern-per-package-exceptions)
  - [Note on catching HTTP client exceptions](#note-on-catching-http-client-exceptions)
- [Pattern: define exceptions simply (KISS)](#pattern-define-exceptions-simply-kiss)
  - [When to add parameters](#when-to-add-parameters)
  - [Use subclasses to express specificity](#use-subclasses-to-express-specificity)

---

## Pattern: built-in Python exception chaining

This follows the [Python Best Practice for Exception Chaining](https://docs.python.org/3/tutorial/errors.html#exception-chaining).

All exceptions use standard Python exception chaining via `raise X from Y` at the raise site:

```python
except SomeError as e:
    raise K8sPodError(f"Unexpected error listing pods in namespace '{ns}'") from e
```

Python then automatically:
- sets `__cause__` on the new exception
- prints the full chain in tracebacks ("The above exception was the direct cause of...")
- preserves the original traceback for `logger.exception()` / `exc_info=True`

### Why `BaseChainedException` was removed:

An earlier version of this codebase had a custom `BaseChainedException` base class for exception chaining:
- accepted `original_exception` as a constructor argument
- manually set `self.__cause__ = original_exception`
- overrode `__str__` to embed `"(caused by ExcType: message)"` in the string representation

This was abandoned because:

1. **Does not follow Python best practice/conventions.** Python has built-in syntax for exception chaining that is widely understood and supported by tooling. A custom base class with different semantics is non-idiomatic and can confuse Python developers.
2. **Don't override what Python already does.** `raise X from Y` is the correct, idiomatic mechanism for exception chaining. Python's built-in behaviour covers tracebacks, `__cause__`, and tooling support. Reimplementing it in a base class adds complexity and extra maintenance and potential points of failure with no benefit.
3. **`__str__` embedding the cause is the wrong layer.** Structured logging with `exc_info=True` (or `logger.exception(...)`) already surfaces the full chain. Embedding cause text in `str(exc)` duplicates information and can confuse log aggregators that parse structured fields.
4. **Chaining belongs at the raise site, not the constructor (Python best practice).** `raise X from Y` makes the relationship explicit and readable in the code where it happens. Passing the original exception as a constructor argument hides it and separates cause from effect across lines.

---

## Pattern: per-package exceptions

Each package defines its own exception type in its own `exceptions.py`. Callers only need to import from the package they use — no transitive dependency on `devhub_<name>.exceptions` required. This follows the same convention as Python's standard library and popular third-party packages (e.g. `requests` raises `requests.exceptions.RequestException`, not `urllib.error.URLError`): each library owns its exception surface and does not expose its dependency's types. This ensures loose coupling between packages and allows each package to evolve its exceptions independently without risk of breaking dependent packages, and also clarifies which exception occurs in which package (e.g. a `K8sPodError` is clearly from a K8s-related component), etc.

All specific exception types can be seen in the `exceptions.py` files in each package. One file per package keeps things organized and discoverable, and avoids scattering exception definitions across the codebase. This follows the same convention as Python's standard library and popular third-party packages such as `requests` (`requests.exceptions`), `kubernetes` (`kubernetes.client.exceptions`), etc.

See [Python Documentation for User-defined Exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions) for more best practices on defining custom exceptions.

### Note on catching HTTP client exceptions

`BaseHTTPClient._make_request()` raises `APIError` and `ClientTimeoutError` from `devhub_<name>`. In the rare case where a subclass method needs to catch those specifically before wrapping in its own exception type, it may still import from `devhub_<name>.exceptions` for the `except` clause only. Example in `authoritative_dns_client.py`:

```python
from devhub_<name>.exceptions import APIError           # caught, not raised
from devhub_<name>.clients.powerdns.exceptions import DNSError, DNSClientError

except (DNSError, APIError):
    raise  # re-raise already-formatted exceptions unchanged
except Exception as e:
    raise DNSClientError("...") from e
```

---

## Pattern: define exceptions simply (KISS)

Exception classes should be as simple as possible. The error message string is the primary carrier of context — the exception class name conveys the *category*, the message conveys the *detail*.

```python
# Correct — simple, no custom params needed
class K8sPodError(K8sError):
    pass
```

Do not add `__init__` parameters or `__str__` overrides unless they serve a genuine purpose beyond what is already in the message string.

### When to add parameters

Only add a custom parameter when a caller **needs to inspect the value programmatically** (i.e. in code, not just in a log message). Ask: "will a `except` block or a unit test actually read this field?" If not, put it in the message string instead.

✅ `APIError.status_code` — callers branch on the HTTP status code to decide retry logic  
✅ `APIError.response_text` — callers surface raw API error bodies to operators  
❌ `GitError.repo_name` — already embedded in the message string; no caller reads it from the field  
❌ `ClientError.client_name` — already in the message string and in the exception class name itself  

### Use subclasses to express specificity

When you need to distinguish *kinds* of errors (e.g. pod vs. service), use a subclass rather than a parameter. Callers can then catch exactly what they care about:

```python
# devhub_<name>/clients/k8s/exceptions.py
class K8sError(Exception): pass        # catch-all for the whole package
class K8sPodError(K8sError): pass      # pod list/delete failures
class K8sServiceError(K8sError): pass  # service/endpoint failures
class K8sConfigError(K8sError): pass   # secret/configmap failures
class K8sConnectionError(K8sError): pass  # cluster connect/config load

# devhub_<name>/clients/powerdns/exceptions.py
class DNSError(Exception): pass            # catch-all; named after the domain, not the supplier
class DNSResolutionError(DNSError): pass   # dnspython resolver failures
class DNSClientError(DNSError): pass       # DNS API client failures
```

While defining empty classes with `pass` may seem ambiguous or boilerplate-heavy, this is a Python best practice with real advantages that you should embrace:

- **Selective catching** — callers can `except K8sPodError` to handle pod failures specifically, or `except K8sError` to catch all K8s errors, without coupling to message strings or error codes.
- **Type-safe error handling** — IDEs and type checkers understand the hierarchy and can warn on unreachable or missing `except` branches.
- **Stable API surface** — adding detail to an exception (e.g. a new field) later does not break existing `except` clauses; the class identity remains the contract.
- **Self-documenting hierarchy** — the subclass tree is the authoritative list of error categories; no need to grep for string patterns or error codes to understand what can go wrong.
- **No overhead** — an empty `pass` class costs nothing at runtime; Python's exception machinery only requires the type, not any body.

> **Naming convention:** Note that for example `DNSError` is used and not `PowerDNSError` (which would tie the exception to a specific supplier) — named after the **domain** (DNS) rather than a specific **supplier** (PowerDNS). If the software is replaced in the future, the exception surface stays stable.