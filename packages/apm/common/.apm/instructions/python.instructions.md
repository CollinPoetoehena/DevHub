---
description: "Use when writing Python code for DevHub integrations and operational tooling."
applyTo: "**/*.py, **/*.pyi"
---

# Python Instructions

@path/common/base-coding-standards.md

> This file extends [common/coding.instructions.md](../instructions/common/coding.instructions.md) with Python specific content.

## Framework

Use **pytest** as the testing framework.

## Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

## Test Organization

Use `pytest.mark` for test categorization:

```python
import pytest

@pytest.mark.unit
def test_calculate_total():
    ...

@pytest.mark.integration
def test_database_connection():
    ...
```

## Reference

See skill: `python-testing` for detailed pytest patterns and fixtures.

Developer note (Copilot may ignore this note): these instructions are distributed in the common APM package. See the [Copilot setup guide](https://github.com/CollinPoetoehena/devhub/blob/master/docs/COPILOT-SETUP.md) for installation and maintenance.

- Prefer the supported `devhub_python_sdk` interfaces for shared Kubernetes, monitoring, storage, core integration, and other needs. Check existing capabilities before adding another client or helper; use vendor APIs directly where the SDK does not cover the requirement.
- Keep operational commands and deployment-maintenance workflows in `devhub_tools`, separate from the SDK's reusable service interfaces.
- Reuse the repository's existing dependency manifests and supported Python versions; do not assume locally installed convenience packages are application dependencies.