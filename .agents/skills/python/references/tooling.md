# Python Tooling

DevHub defaults for Python tooling, adapted from the tooling section of [ECC `python-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) and updated to a single toolchain. Repository configuration and the Python and common instructions take precedence over this reference.

## Defaults

| Concern | Tool | Notes |
|---|---|---|
| Project, dependencies, and Python versions | uv | `pyproject.toml` with a committed `uv.lock` |
| Formatting and import sorting | `ruff format`, `ruff check` (rule `I`) | Replaces black and isort |
| Linting | `ruff check` | Replaces flake8 and most pylint checks |
| Type checking | mypy | Strict for new packages |
| Tests and coverage | pytest, pytest-cov | Markers registered in configuration |
| Vulnerability audit | pip-audit | Audits the locked environment |

## Project Setup

```sh
uv init --package my-package                       # new package with a src/ layout
uv add httpx pydantic                              # runtime dependencies
uv add --dev mypy pip-audit pytest pytest-cov ruff # development dependencies
uv sync                                            # create or update .venv from uv.lock
```

Commit `pyproject.toml` and `uv.lock`; never commit `.venv/`. In CI, use `uv sync --locked` so an outdated lock file fails the build.

## pyproject.toml

```toml
[project]
name = "my-package"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["httpx", "pydantic"]

[dependency-groups]
dev = ["mypy", "pip-audit", "pytest", "pytest-cov", "ruff"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"]

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers"]
markers = [
    "unit: fast tests without external dependencies",
    "integration: tests that need external services",
]

[tool.coverage.run]
source = ["src"]
branch = true
```

`uv add` records lower version bounds in `dependencies` and `dependency-groups`; `uv.lock` pins the exact versions.

## Commands

```sh
uv run ruff format .                          # format code
uv run ruff check --fix .                     # lint and sort imports
uv run mypy .                                 # type check
uv run pytest --cov --cov-report=term-missing # tests with coverage
uv run pytest -m "not integration"            # skip tests that need external services
uv run pip-audit                              # known vulnerabilities in installed dependencies
uv lock --upgrade                             # refresh locked versions
```

## References

- [uv documentation](https://docs.astral.sh/uv/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PEP 735: Dependency groups](https://peps.python.org/pep-0735/)
