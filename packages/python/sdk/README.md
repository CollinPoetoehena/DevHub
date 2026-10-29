# DevHub Python SDK

Installable Python foundation for shared integrations. No domain operations are implemented yet; importing the package performs no network access or application configuration.

---

## Table of Contents

- [Installation](#installation)
- [Development](#development)
- [Adding integrations](#adding-integrations)
- [Releases](#releases)

---

## Installation

Requires Python 3.12 or newer. From a checkout:

```sh
python3 -m pip install ./python
```

After a corresponding tag has actually been published, a consumer can pin a Git installation:

```sh
python3 -m pip install 'devhub-python-sdk @ git+https://github.com/CollinPoetoehena/devhub-sdks.git@python/v0.1.0#subdirectory=python'
```

The distribution is `devhub-python-sdk`; the import is `devhub_python_sdk`. A version tag is a release reference, not a guarantee that tags cannot move; use a full commit ID for exact source identity. Consumers own their environment and dependency pinning.

---

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from this directory:

```sh
uv sync --locked
uv run --locked ruff check src tests ../scripts
uv run --locked ruff format --check src tests ../scripts
uv run --locked mypy
uv run --locked pytest
uv run --locked python -m unittest discover -s ../scripts -p 'test_*.py'
uv build
```

The committed uv lock controls development tooling; it does not impose the development environment on consumers. Update it deliberately when dependencies change. Metadata is explicit in `pyproject.toml`, and Hatchling builds the `src/` package with its `py.typed` marker.

CI also installs the built wheel and source distribution into clean environments, outside the source tree, and verifies import, metadata, and the typing marker. This checks real packaging rather than only editable-install behavior.

---

## Adding integrations

Add a domain subpackage only for a concrete operation needed by a consumer. Use upstream clients when appropriate, declare actual runtime dependencies, type public contracts, and test failures as well as success. Choose synchronous or asynchronous APIs from consumer needs, not a promise to maintain both.

Keep authentication/configuration explicit and supplied by the application. Do not configure application logging, create clients during import, or include real endpoints and credentials. Optional heavyweight providers should not be imported eagerly by the root package.

---

## Releases

Follow the shared [release procedure](../docs/releases.md#python-release). Python has its own version and tag stream, independent of Go. GitHub artifacts are supported; PyPI publishing is not configured.
