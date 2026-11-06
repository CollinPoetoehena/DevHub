---
name: python
description: 'Python patterns, testing, and tooling for DevHub repositories: idioms, type hints, error handling, data classes, concurrency, pytest fixtures and mocking, and uv, ruff, and mypy setup. Use when writing, testing, reviewing, or setting up Python code. Opens one focused reference per task.'
---

# Python

Index for Python work. Open only the reference the task needs; the Python and common instructions take precedence over the references.

## When to Use This Skill

- Writing, refactoring, or reviewing Python code
- Writing or reviewing pytest tests, fixtures, mocks, or coverage
- Designing Python packages, modules, or project layout
- Setting up or changing Python tooling, dependencies, or `pyproject.toml`

## Steps

1. **Write or change code.** Open [references/patterns.md](references/patterns.md) for idioms, type hints, error handling, context managers, data classes, decorators, concurrency, and package layout.
2. **Write or change tests.** Open [references/testing.md](references/testing.md) for pytest structure, fixtures, parametrization, markers, mocking, and async tests.
3. **Set up or change tooling.** Open [references/tooling.md](references/tooling.md) for uv, ruff, mypy, pytest configuration, and dependency auditing.
4. **Validate.** Run the validation commands from the Python instructions and report each result.

## Gotchas

- **Mutable defaults are shared:** a default `[]` or `{}` is created once and shared by every call; default to `None`.
- **Late-binding closures:** functions created in a loop capture the variable, not its current value; bind it with a default argument or `functools.partial`.
- **Patch where it is looked up:** `unittest.mock.patch` must target the name in the module under test, such as `app.service.httpx`, not the module that defines it.
- **Blocking calls in async code:** a synchronous call such as `time.sleep` or `requests.get` inside `async def` blocks the event loop; use an async library or `asyncio.to_thread`.
- **Naive datetimes:** `datetime.now()` returns a naive value and `datetime.utcnow()` is deprecated; use `datetime.now(timezone.utc)`.
- **Identity versus equality:** compare with `None` using `is`, and never compare strings or numbers with `is`.

## Related Skills

- `fastapi`: FastAPI applications.
- `django`: Django and Django REST framework applications.

## References

- [Python documentation](https://docs.python.org/3/)
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
