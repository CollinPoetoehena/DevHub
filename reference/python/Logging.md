# Logging

Python's built-in `logging` module uses a **hierarchical logger tree** rooted at the root logger. Logger names like `"myapp.db.client"` automatically become children of `"myapp.db"`, which is a child of `"myapp"`, which is a child of the `root` logger. Log records propagate up this tree by default, so a handler attached to `"myapp"` will receive records from all its children.

This hierarchy is the core mechanism that separates **library code** (which should never configure logging) from **application code** (which owns the logging configuration).

See for more details on logging best practices in Python: [Logging HowTo](https://docs.python.org/3/howto/logging.html) and [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html).

---

## Table of Contents

- [Libraries](#libraries)
- [Applications](#applications)
- [Discovering logger names in third-party packages](#discovering-logger-names-in-third-party-packages)
- [Exceptions to the standard pattern](#exceptions-to-the-standard-pattern)
  - [When to make an exception](#when-to-make-an-exception)
  - [Exception 1 — Dual-mode output (CLI terminal + library logger)](#exception-1--dual-mode-output-cli-terminal--library-logger)
  - [Exception 2 — Base class logging when subclasses live in other modules](#exception-2--base-class-logging-when-subclasses-live-in-other-modules)
  - [Exception 3 — Class methods and static methods](#exception-3--class-methods-and-static-methods)
- [Logging configuration — philosophy and setup](#logging-configuration--philosophy-and-setup)
    - [Optional: Building a reusable logging configuration — `<some central package>.logging_utils`](#optional-building-a-reusable-logging-configuration--some-central-packagelogging_utils)
- [Summary](#summary)

---

## Libraries

A library should follow the [standard Python library logging pattern](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library):

1. **Always use `logging.getLogger(__name__)`** at module level. `__name__` resolves to the dotted import path (e.g. `devhub_python_<name>_<name>.tooling.git`), which places the logger correctly in the hierarchy.
2. **Never configure handlers, formatters, or levels** (no `basicConfig`, no `addHandler`, no `setLevel`). That is the application's responsibility — interfering would cause duplicate log entries, incorrect levels, or output going to unexpected destinations.
3. **Add a `NullHandler` to the top-level package logger.** This prevents a `No handlers could be found` warning if the application has not configured logging at all. It is a single line in the package's top-level `__init__.py` and has no other effect. You also see this pattern in popular libraries such as `requests` and `urllib3` where they have this in the top-level package `__init__.py`.

**What `NullHandler` does:** it is a do-nothing handler — it accepts log records and discards them silently. Without it, if a library emits a log record and the application has not set up any handlers, Python falls back to `logging.lastResort` (a `WARNING`-level `StreamHandler` that prints to `stderr`) and also emits a `No handlers could be found for logger "..."` warning to `stderr`. Adding `NullHandler` satisfies Python's requirement that at least one handler exists, so neither the warning nor the fallback output appears. The application can still attach its own handlers and receive the library's log records normally — `NullHandler` never interferes with that.

```python
# devhub_python_<name>_<name>/__init__.py  (top-level package only — not in every sub-module)
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

```python
# devhub_python_<name>_<name>/git.py  (sub-modules: just getLogger, no NullHandler needed (already covered by the top-level packagedevhub_devhub_python_<name>_<name> logger)))
import logging

logger = logging.getLogger(__name__)  # "devhub_python_<name>_<name>.tooling.git"

def get(url: str) -> ...:
    logger.debug("debug log")
    ...
```

---

## Applications

An application (anything with an entry point) is responsible for configuring logging **once**, **early**, before any library code runs. This is typically done in `main()` or at the top of the entry-point script.

See for more details the [Python Logging Configuration Documentation](https://docs.python.org/3/howto/logging.html#configuring-logging).

**Option 1 — `dictConfig` (recommended best practice):**

`dictConfig` is preferred over `basicConfig` for almost all real applications because it is declarative, complete, and explicit. `basicConfig` is a convenience shortcut that only works if no handlers have been attached to the root logger yet — calling it after any library has already triggered logging setup silently does nothing. `dictConfig` always applies regardless of call order, supports multiple handlers, per-logger overrides, and formatters in a single atomic configuration, and its structure maps directly to the Python logging documentation, making it easy to read, copy, and extend. `basicConfig` is fine for throwaway scripts; `dictConfig` is the right choice for any application that runs in production.

```python
# main.py
import logging
import logging.config

def main():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,  # keeps library loggers alive
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "app.log",
                "maxBytes": 10_000_000,
                "backupCount": 3,
            },
        },
        # Root logger: catches everything not matched by a specific logger below.
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        # Per-logger overrides: tune specific packages without affecting others.
        "loggers": {
            # Your own application tree — DEBUG to file, INFO to console.
            "myapp": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,  # don't also send to root (otherwise it would create duplicate records according to the root config (e.g. console handler with INFO level))
            },
            # Silence chatty third-party libraries.
            "urllib3":    {"level": "WARNING"},
            "kubernetes": {"level": "WARNING"},
        },
    })
    ...
```

> Always set `disable_existing_loggers: False`. The default (`True`) silences any logger that was created before `dictConfig` runs, which catches library loggers initialised at import time.

Sub-modules of the application follow the same pattern as libraries — `getLogger(__name__)` and no configuration. The configuration cascades automatically through the hierarchy.

```python
# myapp/db/client.py
import logging

logger = logging.getLogger(__name__)  # "myapp.db.client"

class DBClient:
    def query(self, sql: str) -> ...:
        logger.info("Running query: %s", sql)
        ...
```

**Option 2 — `basicConfig` (simple, good for scripts and CLIs):**

```python
# main.py
import logging

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )
    ...
```

---

## Discovering logger names in third-party packages

To silence or tune a dependency you need to know the exact logger name(s) it uses. The most reliable ways:

1. **Check the documentation** — well-maintained packages document their logger names.
2. **Grep the installed source** — logger names are almost always string literals passed to `getLogger`:

```bash
# find the site-packages directory for your venv, then grep for logger calls, such as:
grep -RIn "getLogger" ./venv/lib/python3.14/site-packages/urllib3/
grep -RIn "logger" ./venv/lib/python3.14/site-packages/urllib3/
grep -RIn "logging" ./venv/lib/python3.14/site-packages/urllib3/
...
```

Example outputs using the `devhub_python_<name>_<name>` and `urllib3` packages as an example:
```
# devhub_python_<name>_<name> loggers:
./CHANGELOG.md:17:  - **`logger` constructor parameter removed from all modules.** Every module now declares `logger = logging.getLogger(__name__)` at module level. Callers that previously passed a logger instance must configure the logger hierarchy externally via `logging.basicConfig` or `logging.config.dictConfig`. See the [Python Logging Design](../docs/design/python/Logging.md#logging-configuration--philosophy-and-devhub-setup) for full documentation.
./test/test_get_class_logger.py:141:        """Python's logging.getLogger caches by name — same inputs → same object."""
./src/devhub_python_<name>_<name>/utils/logging_utils.py:205:    ``logging.getLogger(name)`` to retrieve the actual object.
./src/devhub_python_<name>/utils/proxy_utils.py:7:logger = logging.getLogger(__name__)
./src/devhub_python_<name>/tooling/git.py:64:logger = logging.getLogger(__name__)
./src/devhub_python_<name>_<name>/__init__.py:24:logging.getLogger(__name__).addHandler(logging.NullHandler())
./src/devhub_python_<name>/clients/client_utils.py:27:    return logging.getLogger(f"{cls.__module__}.{name}")
./src/devhub_python_<name>_<name>/clients/metrics_alerting/email_client.py:7:logger = logging.getLogger(__name__)
./src/devhub_python_<name>/clients/metrics_alerting/parser.py:6:logger = logging.getLogger(__name__)

# urllib3 client loggers:
(venv) poetoec@<client>:~/projects/devhub_python_<name>$ grep -RIn "getLogger" ./venv/lib/python3.14/site-packages/urllib3
./venv/lib/python3.14/site-packages/urllib3/util/retry.py:29:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/http2/connection.py:23:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/poolmanager.py:35:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/__init__.py:71:logging.getLogger(__name__).addHandler(NullHandler())
./venv/lib/python3.14/site-packages/urllib3/__init__.py:85:    logger = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/response.py:51:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/connection.py:71:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/contrib/emscripten/response.py:19:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/contrib/pyopenssl.py:135:log = logging.getLogger(__name__)
./venv/lib/python3.14/site-packages/urllib3/connectionpool.py:61:log = logging.getLogger(__name__)
```

The value of `__name__` in each file is its dotted import path, so `urllib3/connectionpool.py` → logger name `"urllib3.connectionpool"`. The top-level name `"urllib3"` covers the entire package.

3. **Inspect at runtime** — after importing a library, list all registered loggers:

```bash
python -c "import logging; import <package>; [print(name) for name in sorted(logging.Logger.manager.loggerDict)]"
```

Example outputs to illustrate what loggers live in each package (can be used to configure your logging more precisely), uses the `devhub_python_<name>` and `urllib3` packages as an example:
```
# (devhub_python_<name>) loggers:
(venv) poetoec@<client>:~/projects/devhub_python_<name>$ python -c "import logging; import devhub_python_<name>; [print(name) for name in sorted(logging.Logger.manager.loggerDict)]"
charset_normalizer
devhub_python_<name>
devhub_python_<name>.utils
devhub_python_<name>.utils.proxy_utils
requests
urllib3
urllib3.connection
urllib3.connectionpool
urllib3.poolmanager
urllib3.response
urllib3.util
urllib3.util.retry

# urllib3 loggers:
(venv) poetoec@<client>:~/projects/devhub_python_<name>$ python -c "import logging; import urllib3; [print(name) for name in sorted(logging.Logger.manager.loggerDict)]"
urllib3
urllib3.connection
urllib3.connectionpool
urllib3.poolmanager
urllib3.response
urllib3.util
urllib3.util.retry
```

---

## Exceptions to the standard pattern

The module-level `logger = logging.getLogger(__name__)` rule covers the vast majority of cases. There are a small number of situations where the pattern looks different — but in each case the module-level logger is still present; only additional structure is layered on top.

---

### When to make an exception

| Situation | What changes | What stays the same |
|---|---|---|
| Function that must produce output in two modes (e.g. colored terminal vs. logger) | Declare module-level logger; expose a `use_logger: bool = False` flag to control an output adapter | All output is routed through the adapter — no direct `logger.X()` calls at call sites |
| Base class whose methods are called from subclasses in other packages | Import and call shared `get_class_logger(cls)` from `devhub_python_<name>.clients.client_utils`; `__init__` calls `get_class_logger(self.__class__)` | Subclasses need no logger setup at all |
| `@classmethod` on a class hierarchy | Call `get_class_logger(cls)` — reuses the shared function | Module-level logger still available for non-classmethod code in the same module |
| `@staticmethod` | Must use the module-level logger — no `cls` or `self` available | Module-level `logger = logging.getLogger(__name__)` |
| Module that is also a utility for the logging system itself (e.g. configures loggers) | May import `Logger` type for its own API | Still declares its own module-level logger |

The rule of thumb: **only declare the module-level logger if the module actually calls it**. Declaring an unused logger is noise.

---

### Exception 1 — Dual-mode output (CLI terminal + library logger)

Some functions need to produce human-readable colored output when run from the command line, but route all output through the logging system when called programmatically from library code. These two requirements are incompatible with a single fixed approach.

The solution is an **output adapter** controlled by a `use_logger` flag. The module declares a standard module-level logger and passes it to `OutputAdapter` only when the flag is set:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)  # standard module-level logger

def do_work(
    input_path: str,
    *,
    use_logger: bool = False,  # False → CLI coloured output, True → route through module logger
) -> None:
    out = OutputAdapter(logger if use_logger else None)  # bridges the two modes
    out.info("Starting work...")

# Example OutputAdapter implementation:
class OutputAdapter:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger

    def debug(self, msg: str) -> None:
        if self._logger:
            self._logger.debug(msg)
        else:
            print_debug(msg)
    ....
```

`False` is the correct default because these functions are primarily CLI tools; library use is the opt-in. The caller enables library mode by passing `use_logger=True` and then for example configures the `devhub_python_<name>.scripts.*` logger namespace via the standard logging hierarchy — no logger instance needs to be constructed or threaded through the call.

**Why a flag rather than passing a `Logger` instance:**

| Alternative | Problem |
|---|---|
| `logger: Optional[logging.Logger] = None` | The caller must construct a `Logger` object and pass it in; every call site in library code must either obtain a logger reference or forward one through the call chain — unnecessary boilerplate |
| Flag + module-level logger | The module already owns its logger via `getLogger(__name__)` (the standard setup as explained in the rest of this document); the caller only flips a `bool` and configures routing externally via `dictConfig` — no object passing required |

---

### Exception 2 — Base class logging when subclasses live in other modules

When a base class defines methods that are called through subclasses, the standard `logging.getLogger(__name__)` would place all log records under the base class module name — losing the subclass identity in the logger name.

The better pattern: **define a shared `get_class_logger(cls, name)` function** (e.g. in a shared utilities module) that uses `cls.__module__` rather than a fixed base-class `__name__`. Both instance setup and classmethods call this one function, so the naming convention is enforced in exactly one place:

```python
# mylib/shared_utils.py
import logging
from typing import Type

def get_class_logger(cls: Type) -> logging.Logger:
    # Uses cls.__module__ so the logger is rooted in the subclass module, not the base class.
    return logging.getLogger(cls.__module__)


# mylib/base_client.py
from mylib.shared_utils import get_class_logger

class BaseClient:
    def __init__(self):
        # Logger name is the subclass module: "mylib.users_client", etc.
        self.logger = get_class_logger(self.__class__)

    def connect(self):
        self.logger.info("Connecting...")  # appears under the subclass logger name

# mylib/users_client.py
class UsersClient(BaseClient):
    def get_user(self, user_id):
        self.logger.info(f"Fetching user {user_id}")  # no logger setup needed here
```

Log records now appear as `mylib.users_client`, `mylib.orders_client`, etc. — avoiding boilerplate (e.g. repeated `logger = logging.getLogger(__name__)` or passing `logger` as a parameter in every subclass, etc.) and making them individually configurable:

```python
logging.getLogger("mylib.users_client").setLevel(logging.WARNING)   # silence all users client logs
logging.getLogger("mylib.orders_client").setLevel(logging.DEBUG)    # tune orders client independently
```

The logger is still set up once in one place (the base class `__init__`) and subclasses just call `self.logger` — no `super().__init__(logger)` wiring, no repeated boilerplate.

**Why not the alternatives:**

| Alternative | Problem |
|---|---|
| Module-level `logger = logging.getLogger(__name__)` | All subclass logs appear under the base class module — no way to tune or filter by subclass |
| Pass `logger` as a constructor parameter | Every caller must construct and pass a logger; every subclass must thread it through `super().__init__(logger)` — pure boilerplate |
| `logging.getLogger(type(self).__qualname__)` | Creates loggers named e.g. `UsersClient` — outside the module hierarchy, impossible to control with a namespace prefix like `mylib.users_client` |
| Each subclass declares its own module-level logger | Duplicated setup in every subclass; base class methods can't use it |
| Inline `logging.getLogger(cls.__module__)` in every `__init__` and classmethod directly | Naming convention is not centralised — any future change must be found and updated everywhere |

---

### Exception 3 — Class methods and static methods

`@classmethod` and `@staticmethod` cannot use `self.logger` from Exception 2 — there is no instance. Each requires a different approach.

**`@classmethod`** — receives `cls` as its first argument, which is the actual class the method is called on (including subclasses). Because `get_class_logger` is defined once in a shared utilities module (Exception 2), classmethods simply call `get_class_logger(cls, cls.__name__)` from `devhub_python_<name>.clients.client_utils` — no separate logger setup needed, and the naming convention stays in one place:

```python
# mylib/users_client.py
from mylib.shared_utils import get_class_logger

class UsersClient(BaseClient):
    ...
    @classmethod
    def test_operation(cls, name: str) -> None:
        get_class_logger(cls).debug("Testing operation %s", name)  # appears under the subclass module logger
        ...
```

Because Python caches loggers by name internally, `logging.getLogger(...)` always returns the same cached `Logger` object — calling `get_class_logger()` on every invocation is cheap.

**`@staticmethod`** — receives neither `self` nor `cls`. The only option is the module-level logger. If the log record needs to identify the class for context, include the class name in the message string:

```python
# mylib/config_loader.py
import logging

logger = logging.getLogger(__name__)  # required — only option for static methods

class ConfigLoader:
    @staticmethod
    def load(path: str) -> dict:
        logger.debug("ConfigLoader: loading from %s", path)
        ...
```

If a static method is growing to the point where it needs per-class logger differentiation, that is a signal to convert it to a `@classmethod` instead.

**Why not the alternatives:**

| Alternative | Problem |
|---|---|
| Inline `logging.getLogger(...)` in every `@classmethod` | Duplicates the naming logic across methods — any future naming change must be updated in every callsite |
| Module-level `logger` for `@classmethod` | Loses the subclass name when the method is called on a subclass — all records appear under the base class |
| `cls.__name__` (without `cls.__module__` prefix) in `@classmethod` | Creates a logger named e.g. `UsersClient` — outside the module hierarchy, impossible to control with a namespace prefix |

---

## Logging configuration — philosophy and setup

Python's `logging` module is itself the centralisation layer — hierarchy, handler inheritance, level propagation, `dictConfig` / `basicConfig`, etc. are all built in. A custom central module that attaches handlers and returns configured `Logger` instances just duplicates that machinery without adding value and makes it harder to understand what is actually happening. In earlier projects (e.g. at my work) I previously made that mistake with a `<package example name>.logger` module; it was removed for exactly that reason.

The correct pattern is:
- Every library module declares `logger = logging.getLogger(__name__)` — one line, no configuration.
- Every application entry point calls `logging.config.dictConfig({...})` once, early, before any library code runs.

Writing the `dictConfig` dict inline keeps the entire logging setup visible in one place. There is nothing left for a centralised module to do.

### Optional: Building a reusable logging configuration — `<some central package>.logging_utils`

For some applications it may be handy to provide a utility function in a module (e.g. `logging_utils`) of some central package (ensures only one util is managed centrally, avoiding duplication and inconsistencies). Using them is not required — applications can always write their own `dictConfig` dict directly.

For example, this logging utility can have:
- `build_logging_config`: returns a ready-to-use `dictConfig` dict pre-wired for all internal packages. The only reason it exists as a function rather than a static dict is that the calling application's own logger namespace cannot be known ahead of time — it accepts that as a parameter. Everything it returns is plain data: inspect it, extend it, or override any key before passing to `logging.config.dictConfig`. It is just a utility that helps build the `dictConfig`.
- `log_active_loggers`: debug utility that inspects the live logger registry after `dictConfig` runs and prints each matched logger's name, own level, and effective level — useful for confirming the configuration took effect. For example:
```python
def log_active_loggers(
    configured_namespaces: Optional[list[str]] = None,
    *,  # keyword-only separator: everything after this must be passed by name, never by position. Prevents accidentally swapping optional args that have the same type.
    debug_logger: Optional[Logger] = None,
) -> None:
    """Utility function: inspect and print the active logging configuration for the configured namespaces.

    Iterates all currently registered loggers (via :func:`_get_registered_logger_names`)
    and keeps only those whose name equals or starts with one of the
    ``configured_namespaces`` prefixes. For each matched logger it shows the logger
    name, its own explicitly set level (if any), and the effective level (inherited
    from a parent if not set directly). This makes it easy to verify at startup that
    ``dictConfig`` applied the expected levels and that no logger is silently
    inheriting an unwanted level from a parent.

    This is a **debug/diagnostic utility** — call it immediately after
    ``logging.config.dictConfig(...)`` to confirm the configuration took effect::

        import logging, logging.config
        from devhub_python_<name>.logging_utils import build_logging_config, log_active_loggers

        cfg = build_logging_config(extra_logger_names=["my_service"])
        logging.config.dictConfig(cfg)
        log_active_loggers(list(cfg["loggers"]))
        # prints, e.g.:
        # [DEBUG] Active loggers (filtered to configured namespaces):
        #   devhub_python_<name>                   level=INFO    effective=INFO   handlers=[StreamHandler(<stdout>), RotatingFileHandler(/var/log/app.log)]
        #   devhub_python_<name>.tooling.git       level=(unset) effective=INFO   handlers=(none — propagates to parent)
        #   my_service                      level=INFO    effective=INFO   handlers=[StreamHandler(<stdout>)]

    Args:
        configured_namespaces: Logger name prefixes to include in the output.
            When ``None`` (default) all registered loggers are shown — useful
            for an initial survey of what loggers a package or library creates.
            When provided, only loggers whose name matches a prefix exactly or
            starts with ``"<prefix>."`` are shown.
        debug_logger: If supplied, the output is emitted via
            ``debug_logger.debug()``. When ``None`` (default) it is printed to
            stdout using :func:`print_debug`.
    """
    # Collect all logger names currently registered in the logging system.
    all_names = _get_registered_logger_names()

    # Filter to only the namespaces we care about if the caller specified any.
    # A logger matches if its name equals a namespace exactly (e.g. "devhub_python_<name>")
    # or is a child of it (e.g. "devhub_python_<name>.tooling.git" starts with "devhub_python_<name>.").
    if configured_namespaces is not None:
        names = [
            n for n in all_names
            if _logger_matches_namespace(n, configured_namespaces)
        ]
    else:
        names = all_names

    # Build one line per logger showing its name, own level, and effective level.
    # - own level: the level set directly on this logger (NOTSET means "inherit from parent")
    # - effective level: the level actually used for filtering — walks up the hierarchy until
    #   a non-NOTSET level is found, so this is always a concrete level name like INFO or WARNING.
    header = "Active loggers" + (" (filtered to configured namespaces)" if configured_namespaces is not None else "") + ":"
    lines = [header]
    for name in names:
        # Retrieve the Logger object. loggerDict values can be PlaceHolder objects
        # for intermediate logger nodes that have no explicit configuration.
        entry = logging.Logger.manager.loggerDict.get(name)
        if not isinstance(entry, logging.Logger):
            # PlaceHolder: an intermediate node in the hierarchy with no logger of its own.
            lines.append(f"  {name:<40} (placeholder — no logger instance)")
            continue

        # Own level: NOTSET (0) means this logger inherits its level from its parent.
        own_level = logging.getLevelName(entry.level) if entry.level != logging.NOTSET else "(unset)"
        # Effective level: the concrete level used for filtering after walking up the hierarchy.
        effective_level = logging.getLevelName(entry.getEffectiveLevel())
        # Handlers: directly attached handlers (not inherited). Each handler's class name
        # is shown alongside its destination — file path for file handlers, stream name
        # (stdout/stderr) for stream handlers. An empty list means the logger relies on
        # propagation to a parent's handlers (usually the root logger).
        handler_descs = []
        for h in entry.handlers:
            cls = type(h).__name__
            if hasattr(h, "baseFilename"):
                # RotatingFileHandler / TimedRotatingFileHandler / FileHandler
                handler_descs.append(f"{cls}({h.baseFilename})")
            elif hasattr(h, "stream") and hasattr(h.stream, "name"):
                # StreamHandler — stream.name is "<stdout>" or "<stderr>"
                handler_descs.append(f"{cls}({h.stream.name})")
            else:
                handler_descs.append(cls)
        handlers_str = ", ".join(handler_descs) if handler_descs else "(none — propagates to parent)"
        lines.append(
            f"  {name:<40} level={own_level:<10} effective={effective_level:<10} handlers=[{handlers_str}]"
        )

    msg = "\n".join(lines)

    # Emit through the provided logger at DEBUG, or fall back to the coloured print helper.
    if debug_logger:
        debug_logger.debug(msg)
    else:
        print_debug(msg)
```

> **Note:** `logging_utils` is not a centralised logging configuration module — it is a utilities module that provides optional helpers for applications to use in their own logging configuration. It does not declare any loggers itself, and it does not configure anything on import. It is safe to import from this module in any library code without risking unintended logging side effects.

---

## Summary

| Role | What to do |
|---|---|
| Library module | `logger = logging.getLogger(__name__)` — nothing else |
| Application entry point | Configure once with `basicConfig` or `dictConfig`; optionally build a utility module with a function like `build_logging_config` to avoid repeating logger configuration |
| Application sub-module | `logger = logging.getLogger(__name__)` — nothing else |
| Some exceptional cases | See the exceptions section above for patterns and rationale |
| Tuning noisy dependencies | Per-logger `"level": "WARNING"` in `dictConfig`, or `logging.getLogger("lib").setLevel(logging.WARNING)` |
| Finding logger names | Grep installed source for `getLogger`, or inspect `logging.Logger.manager.loggerDict` at runtime |
| Verifying logging setup | Call `log_active_loggers(list(cfg["loggers"]))` after `dictConfig` to see active loggers and their effective levels |

---