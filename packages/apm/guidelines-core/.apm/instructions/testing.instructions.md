---
description: "Use when adding or changing tests. Covers behavior-focused cases, edge conditions, assertions, determinism, regression checks, and project test tooling."
applyTo: "**"
---

# Testing Guidelines

- **Test observable behavior.** Assert expected results and relevant side effects rather than implementation details.
- **Cover appropriate cases.** Test normal behavior and invalid inputs. Where applicable, include missing, null, empty, and below/at/above-boundary values without redundant combinations.
- **Check failures and side effects.** Verify expected error behavior and that failed operations do not cause unintended state changes.
- **Preserve behavior.** Add regression coverage for fixed defects and retain coverage for existing behavior the change could affect.
- **Keep tests meaningful and deterministic.** Use assertions that would catch regressions; avoid dependence on timing, execution order, or external state.
- **Use project tooling.** Follow the existing test framework and conventions. Run focused tests for the change and any broader checks required by the project.
- **Choose test levels by the behavior and boundary under verification.** Use unit tests for isolated logic, integration tests at component boundaries, and end-to-end or broader workflow tests when behavior spans the system.

For boundary validation, see the [coding guidelines](coding.instructions.md). For security-sensitive changes and required negative cases, see the [security guidelines](security.instructions.md).
