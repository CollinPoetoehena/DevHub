---
description: "Use when writing, testing, or reviewing Python code: toolchain defaults, mandatory rules, and validation commands on top of the common instructions."
applyTo: "**/*.py,**/*.pyi,**/pyproject.toml"
---

# Python Instructions

These rules add Python specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `python` skill before adding modules, tests, or tooling; it opens one reference per task.
- Apply the `fastapi` skill for FastAPI code and the `django` skill for Django code.

## Toolchain

Follow the repository's existing tooling and supported Python versions. For new projects, default to:

- **Project and dependencies:** `uv` with `pyproject.toml`, a declared `requires-python`, and a committed `uv.lock`.
- **Formatting and linting:** `ruff format` and `ruff check`, which replace black, isort, and flake8.
- **Type checking:** `mypy`, strict for new packages.
- **Tests:** `pytest` with `pytest-cov`.
- **Vulnerability audit:** `pip-audit`.

## Rules

- Annotate public functions, methods, and module-level constants with modern syntax: `list[str]` and `X | None`, not `typing.List` or `Optional`.
- Catch specific exceptions and chain them with `raise ... from err`; never use a bare `except:` or swallow errors.
- Never use mutable default arguments; default to `None` and create the value inside the function.
- Manage files, locks, connections, and other resources with context managers.
- Use `pathlib.Path` for paths, f-strings for formatting, and `logging` instead of `print` outside command-line output.
- Declare dependencies only in the repository's manifest; do not assume locally installed packages are application dependencies.
- Before adding a client or helper, check whether a shared DevHub Python package already provides it; keep operational commands separate from reusable library code.
- Categorize tests with registered pytest markers, such as `unit` and `integration`, and keep tests independent of execution order and external services.

## Validation

Run from the repository root; use the repository's configured commands when they differ:

```sh
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest --cov --cov-report=term-missing
uv run pip-audit
```

## References

- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python documentation](https://docs.python.org/3/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [pytest](https://docs.pytest.org/en/stable/)
