# Static Code Analysis

This document describes how static code analysis is run on the Python packages. Static analysis inspects the source without executing it, which catches a category of problems — circular imports, unused code, unreachable branches — that tests only surface once the affected code path happens to run.

The tool used in this repository is [Pylint](https://pylint.readthedocs.io/en/latest/), pinned in [requirements.txt](../../../requirements.txt).

> **Why `pylint` and not other packages like `pydeps`, etc.:** Pylint is the official choice for comprehensive static code analysis in Python. It provides a comprehensive set of static checks, including circular imports, unused code, and code style issues. It integrates well with CI/CD pipelines and offers detailed messages that help maintain code quality. Other tools like `pydeps` focus primarily on visualizing dependencies and do not provide the same level of static analysis coverage.

## Table of Contents

- [Running Pylint](#running-pylint)
- [Enabling a single check](#enabling-a-single-check)
- [Checking circular imports](#checking-circular-imports)
  - [Reading the output](#reading-the-output)
  - [Resolving a cyclic import](#resolving-a-cyclic-import)

---

## Running Pylint

Run Pylint from the `src/` directory of the package, so the package is resolved from the source tree instead of from the installed distribution in the virtual environment:

```bash
cd example_package/src
pylint example_package
```

Pylint ends with a score out of 10 and a non-zero exit code when it emitted any message, which is what makes it usable in a pipeline.

> **Do not aim for a perfect score.** Pylint is a tool to catch potential issues, not a measure of code quality. Focus on the messages and fix the underlying problems rather than trying to achieve a 10/10 score. You do not need to fix every minor issue if it does not affect the correctness or maintainability of your code.

---

## Enabling a single check

A full Pylint run reports every enabled check at once, which is noisy when you are looking for one specific class of problem. Disable everything first and re-enable only the check you care about:

```bash
pylint <package> --disable=all --enable=<check-name>
```

The score is still computed over the full rule set, so a run with a single check enabled typically reports a near-perfect score even when it found the problem you were looking for. Read the messages, not the score.

---

## Checking circular imports

A circular import is two or more modules that import each other, directly or through their `__init__.py`. Python does not always fail on one — it fails only when the cycle is entered at a point where a name is used before the partially-initialised module has defined it — so a cycle can sit in the codebase unnoticed until an unrelated import order changes. Pylint finds the cycle itself, regardless of whether it currently breaks:

```
(venv) <computer name>:~/projects/example_package/src$ pylint example_package --disable=all --enable=cyclic-import
************* Module example_package.metrics_alerting.parser
example_package/metrics_alerting/parser.py:1:0: R0401: Cyclic import (example_package.dns -> example_package.dns.interfaces.authoritative) (cyclic-import)

-----------------------------------
Your code has been rated at 9.99/10
```

> `cyclic-import` is only reported reliably when the whole package is checked in one run, because Pylint has to see every module to build the import graph. Do not narrow the run to a single file when looking for cycles.

### Reading the output

The message reports the *cycle*, not the offending line: `example_package.dns -> example_package.dns.interfaces.authoritative` means the package facade `example_package/dns/__init__.py` imports from `interfaces/authoritative.py`, which imports back from `example_package.dns`. The file and line in front of the message (`parser.py:1:0`) is only where Pylint happened to observe the cycle, so start from the arrow chain instead.

### Resolving a cyclic import

The cause is almost always a module importing from its own package facade rather than from the module that defines the name. See [Importing from within the package itself](./Package_Initialization.md#importing-from-within-the-package-itself) for the rule that `__init__.py` is the leaf importer: it imports from the modules below it, never the other way around.

**Solution for above example:**
- **Inside a package, import from the defining module** (`from example_package.dns.models.dns_record import DNSRecordSet`), not from the package facade (`from example_package.dns import DNSRecordSet`). The facade is for callers outside the package.
- **Move the shared type up**, into a package that both sides may import, when two domains genuinely need the same model — that is what `example_package/models/` is for.
- **Import only for type checking** when the import exists purely for annotations, using `if typing.TYPE_CHECKING:` with a string annotation. This removes the import at runtime and therefore the cycle, but it hides a design problem rather than fixing one, so prefer the two options above.
