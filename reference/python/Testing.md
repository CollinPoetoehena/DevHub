# Testing

This document describes the testing design used in Python. All packages should follow the best practices/conventions from Python and pytest itself:
- [unittest](https://docs.python.org/3/library/unittest.html) — the standard library test framework, and the vocabulary (fixture, test case, assertion) everything else builds on.
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) — patching and test doubles, including [where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch), which is the single most common source of a test that silently tests nothing.
- [pytest — Get Started](https://docs.pytest.org/en/stable/getting-started.html) and [How-to guides](https://docs.pytest.org/en/stable/how-to/index.html) — the framework used in this codebase.
- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) and [conftest.py](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files) — shared setup, and where it belongs.
- [pytest — Monkeypatching](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) and [Parametrizing](https://docs.pytest.org/en/stable/how-to/parametrize.html) — replacing dependencies and covering variants without copy-paste.
- [pytest — Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) — layout, `src/` and import modes.

**Only the conventions that need extra attention, or that are specific to this codebase, are documented below.**

## Table of Contents
- [General principles](#general-principles)
- [Structure](#structure)
- [Running against the latest source](#running-against-the-latest-source)
- [Generating tests with AI](#generating-tests-with-ai)
  - [General Workflow](#general-workflow)
  - [Additional General Points](#additional-general-points)
  - [What to check before finalizing the result](#what-to-check-before-finalizing-the-result)
- [Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered](#important-focus-on-highquality-application-code-keep-test-code-simple-stable-purposedriven--not-overengineered)
- [Optional Extra Testing: Static Code Analysis; see Static_Code_Analysis.md](./StaticCodeAnalysis.md)

---

## General principles
- **Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered.** This is very important to save time and effort and therefore named explicitly, see details in [Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered](#important-focus-on-highquality-application-code-keep-test-code-simple-stable-purposedriven--not-overengineered).
- **Test the public surface, not the internals.** A test imports the way a consumer does — through the owning facade — so a refactor that moves a class between files does not break the suite; see [Package Initialization & Importing](./Package_Initialization_Importing.md#which-path-to-use).
- **One test file per source module (even though it may become large),** named `test_<module>.py`. The mapping is mechanical, so the test for a module is found without searching; see [Structure](#structure), even though that test file may become quite large (see [Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered](#important-focus-on-highquality-application-code-keep-test-code-simple-stable-purposedriven--not-overengineered)). 
- **The test name states the behaviour, not the method.** `test_timeout_fires_and_does_not_hang` reads as a claim about the system; `test_run_tool_2` does not.
- **One behaviour per test.** A test that asserts three unrelated things reports one failure and hides the other two.
- **Patch at one seam, not everywhere.** Find the single boundary the module talks to the outside world through (a subprocess runner, a transport, a client) and replace that. Patching six call sites in one test usually means the seam is missing from the design, not from the test.
- **Patch where the name is looked up,** not where it is defined — a module doing `from x import y` binds its own reference, so `x.y` is the wrong target ([where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch)).
- **Do not mock what is cheap and real.** A temporary file (`tmp_path`), a local Git repository, or a subprocess running the interpreter is more faithful than a mock and usually shorter.
- **Cover the failure paths, not only the happy one.** Most of what this codebase's modules exist for is translating failures — a timeout, a missing binary, a wrong exit code — so a suite that only tests success tests the least valuable half.
- **Pin every regression.** When a bug is fixed, a test that fails against the old behaviour goes in with the fix, and the docstring names the bug. That test is the only thing preventing the same mistake twice.
- **Never put real credentials, hostnames, or tokens in a test.** Use obvious placeholders, and assert that secrets do *not* appear in logs, command arguments, or error messages where the source code promises they do not.
- **Shared fixtures live in `conftest.py`,** which pytest loads automatically — test modules request them by name and import nothing.
- **Logging, functions, classes.** The conventions in [Logging](./Logging.md), [Functions](./Functions.md), and [Classes & Generics](./Classes_Generics.md) apply to test code as well, at the lighter bar described in [Important: application code first](#important-application-code-first).

---

## Structure
**The test tree mirrors the source tree**, one directory per source package and one test module per source module, so locating and maintaining a test is mechanical rather than a search. The test module keeps the source module's name with a test_ prefix, and sits at the same position in the tree — so the path of a test is derivable from the path of the code it covers, in both directions:

```
example_package/:
src/example_package/              test/
├── __init__.py                   ├── __init__.py                  required, see below
├── exceptions.py                 ├── conftest.py                  suite-wide fixtures
├── models/                       ├── fakes.py                     optional shared test doubles (root-level utility)
│   └── shared_model.py           ├── test_exceptions.py
├── domain_a/                     ├── models/
│   └── some_client.py            │   ├── __init__.py
└── domain_b/                     │   └── test_shared_model.py
    ├── some_module.py            ├── domain_a/
    └── ops/                      │   ├── __init__.py
        ├── process.py            │   └── test_some_client.py
        └── deploy.py             └── domain_b/
                                      ├── __init__.py
                                      ├── conftest.py              fixtures for this subtree only
                                      ├── test_some_module.py
                                      └── ops/
                                          ├── __init__.py
                                          ├── test_process.py
                                          └── test_deploy.py
```

- **Every test directory needs an `__init__.py`, including `test/` itself.** Mirroring means two different source modules can share a basename (domain_b/process.py and domain_b/ops/process.py → two test_process.py files). Under pytest's default prepend import mode, two test modules with the same basename and no package to distinguish them is a **collection error**, not a warning. The `__init__.py` files make each test module fully qualified (`test.domain_b.ops.test_process`), which removes the ambiguity. This is the documented requirement for mirrored layouts ([Choosing a test layout: Tests outside application code](https://docs.pytest.org/en/stable/explanation/goodpractices.html#choosing-a-test-layout)). The alternative — `--import-mode=importlib`, which handles duplicate basenames without `__init__.py` — also works, but prefer the `__init__.py` files: they keep the default import mode, and make the helper imports below behave predictably.
- **A new source module means a new test module, in the mirrored position.** If a source file is worth its own file, its tests are worth theirs; appending them to a neighbouring test file is how a 10000-line test module starts (large test files are generally fine, but try to split them logically if they grow too big; see [Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered](#important-focus-on-highquality-application-code-keep-test-code-simple-stable-purposedriven--not-overengineered)).
- **Testing utilities go at the root of test/ when more than one subtree needs them** — test doubles, builders, sample payloads, small assertion helpers. They are ordinary modules (test/fakes.py, test/helpers.py, test/samples.py), imported by their fully qualified path because test/ is a package:

  ```python
  from test.fakes import RunToolRecorder   # ✅ shared utility at the test root
  ```

  Keep them plural and purpose-named (fakes.py, helpers.py) rather than named after the first class they hold — run_tool_recorder.py becomes a lie the moment a second double is added. A utility only one subtree uses can sit in that subtree instead, following the same rule one level down.
- **Never name a utility module `test_*.py`.** pytest would collect it as a test module, and a class in it named `Test*` would trigger collection warnings. A helper is not a test.
- **conftest.py holds fixtures, not utilities, and sits at the narrowest level that needs it.** The root test/conftest.py holds what the whole suite uses; a conftest.py inside a mirrored directory holds what only that subtree uses, so an unrelated test is not affected by it. pytest loads these automatically and test modules request fixtures by name — never import from a conftest.py directly, as that breaks under `--import-mode=importlib`.
- **Setup used by a single test module stays in that module,** so its whole context is visible on one screen. Promote it to a conftest.py or a root utility only when a second module needs it.
- **Group within a file by the function or class under test,** in the same order as the source, with a comment banner per group. The test file then reads as a table of contents for the module it covers.

---

## Running against the latest source
- **By default, tests run directly against `src/` with no install step.** `pyproject.toml` puts `src/` on `sys.path` for pytest, so the suite always exercises the working copy — edit a module, run `pytest`, see the result:
```toml
[tool.pytest.ini_options]
# This part is required to be able to run tests, otherwise this will fail.
# Add src/ to the Python path so tests can import the package without installing it first.
# This lets pytest discover the package the same way the installed version would be found.
pythonpath = ["src"]
testpaths = ["test"]
```
- **Run the whole suite, or one file:**
  ```bash
  cd example_package
  pytest test/                                                            # everything
  pytest test/domain_a/                                                   # one entire module
  pytest test/test_domain_a.py                                            # one module file
  pytest test/test_domain_a.py::TestDomainA                               # one test class in one module file
  pytest test/test_domain_a.py::TestDomainA::test_specific_behavior       # one test function in one module file
  pytest test/ -k "timeout"                                               # one behaviour across modules
  ```
- **Optional: Verify against the published artifact before a release.** Publish the version, install it into the venv (see [docs/1_LocalSetup_Prerequisites.md](../../1_LocalSetup_Prerequisites.md)), activate the venv, and run the suite from a directory *outside* `src/`. This catches what a `sys.path` run cannot: a module missing from the wheel, a package that was never declared, or a missing runtime dependency that only worked locally because it happened to be installed.
- **Both modes run the same tests.** Nothing in the suite may depend on which of the two is in use — a test that imports through a relative path or reaches into `src/` breaks the installed run and defeats the check.

---

## Generating tests with AI
> **Tip — Test Generation:** Use AI to generate the tests (e.g. `Claude Opus` in GitHub Copilot or in Microsoft Copilot after providing the source files (see [DevHub AI Reference](../AI.md))) for the code in `src/`. Always review the generated tests for correctness and completeness before relying on them. This will save you time and effort, and improve the overall quality of your test suite compared to writing all tests manually.

### General Workflow
**Apply a structured workflow; Start with a plan generation & Request incrementally (e.g. per domain/sub-package).** If the codebase is large, you can ask the model to generate tests for specific domains/sub-packages incrementally, rather than all at once. This can make the review and verification process more manageable and less overwhelming. This also often provides better output (i.e. higher quality and more focused tests) because the model has less context dilution (large code bases often have distinct domains/sub-packages that are generally irrelevant for other parts). **General workflow you can apply for this reason:** Provide the AI model with all the context (e.g. the full repository source code, any relevant project context, the project structure, etc.), and ask for it to analyze it and generate a short plan for generating tests (do not generate tests yet). Then you can ask the AI incrementally to generate tests for each part, with the model now having the full context ready to improve its answers.

See for more information about *Prompt Engineering* to get the best possible answers: [DevHub AI Reference: Prompt Engineering](../AI.md#prompt-engineering).

**See [general points](#additional-general-points) below, such as how to provide the context effectively, what to provide, etc., for more guidance.**

### Additional General Points
**Getting good output is mostly a matter of what you give the model and what you check afterwards (see [workflow](#general-workflow) above, below are just some additional general points):**
- **Provide the full source files, not fragments.** A model that cannot see the imports, the module docstring, or the exception types will invent them, and a test built on an invented API fails for the wrong reason. So, provide the complete source files to the model, such as the files in `src/` that you want to generate tests for.
**Provide any relevant context, such as the purpose of the project and individual modules, the project structure, etc.** This helps the model generate tests that are aligned with the actual usage and constraints of the code. For example, providing it the project structure via `tree` output gives the model a clear view of the file hierarchy and relationships. 
- **Say what matters most about the module.** "This wraps a subprocess; the timeout and the secret-redaction are the parts that must not regress" produces a materially different suite than "write tests for this file".
- **Ask for one test file per source module,** matching [Structure](#structure), and for shared setup to go in `conftest.py`. Without that instruction the default is one large file.
- **Name the known bugs.** A model told "this previously raised `TypeError` because the exception was constructed with a keyword argument" writes the regression test that pins it; a model not told this has no way to know.
- **Ask for the reasoning in the docstrings.** A test whose docstring explains *why* the behaviour matters stays maintainable; a bare `test_x_returns_y` gets deleted by the next person who sees it fail.
- **Iterate and refine.** After generating tests, review them, run them, and refine the prompts and/or the generated tests with AI further as needed to improve coverage and correctness.
- **Any other action that may be required for your specific situation.** Some situations require a specific addition, the above points and general points only. So, if your situation requires anything specific to be added, add it.

### What to check before finalizing the result
**What to check before finalizing the result** — this is the part that is not optional:
- **Run it.** A generated suite that has never been executed proves nothing. All of it must pass.
- **Verify it actually fails.** Break the source deliberately — remove the timeout, delete a validation, return the wrong value — and confirm the relevant test fails. A test that passes against broken code is worse than no test, because it reports safety that does not exist. This is the single most valuable review step.
- **Check the assertions are real.** Watch for tests that assert a mock was called with what the same test just configured, or that re-implement the function's logic in the assertion. Both pass unconditionally.
- **Check the coverage matches the risk.** Models reliably cover the happy path and under-cover the failure paths, which is the opposite of where the value is for most modules here.
- **Check for invented API.** A method, parameter, or exception the model assumed exists will show up as an error rather than a failure — which is easy to miss in a suite that is otherwise green.

> **General rule:** Check for correctness, but do not over‑engineer the tests. They must be clear, stable, and focused on verifying behaviour and covering risk — not built to production‑grade standards. So, check for correctness and stop there. See details in [Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered](#important-focus-on-highquality-application-code-keep-test-code-simple-stable-purposedriven--not-overengineered).

---

## Important: Focus on high‑quality application code; keep test code simple, stable, purpose‑driven — not over‑engineered
Test code matters, but **the application code (in `src/`) is the code that runs in production and is actually consumed by downstream systems, and it is where code quality effort belongs.** The two are not held to the same bar, and deliberately so:
- **Do not over-engineer the tests.** Time spent perfecting a fixture hierarchy, removing every duplicated line, or abstracting three similar tests into one parametrised helper is time not spent on the code that actually ships. A test suite that is slightly repetitive (i.e. `not DRY`) but obviously correct is a good suite.
- **Duplication in tests is often a feature.** A test should be readable in isolation, without following a chain of helpers to find out what it actually asserts — so the DRY pressure that applies to `src/` is much weaker here. A shared helper that hides the setup makes a failure harder to diagnose, which is precisely when readability matters most.
- **AI-generated test code from a strong model is generally good enough to keep as-is** once you have checked it as described above. The reasons are structural, not a matter of trusting the model:
  - **Tests are verifiable in a way application code is not.** A test's correctness is demonstrated by running it — green against working code, red against broken code. That is an objective check available in seconds, whereas judging whether application code is well-designed takes review and experience.
  - **Tests have no downstream callers.** Nothing imports the test suite, so a clumsy fixture or an awkward name imposes no cost on anyone else. A clumsy abstraction in `src/` propagates to every consumer and every future change.
  - **Test code is highly patterned,** which is exactly what these models are strongest at: arrange/act/assert (AAA testing framework), parametrised variants, fixture setup, and standard assertion style are near-mechanical once the behaviour is decided.
  - **The cost of an imperfect test is bounded and visible.** It fails, and you fix it. The cost of an imperfect abstraction in application code is unbounded and shows up much later.
- **The one exception is correctness.** None of the above applies to whether a test is *right*. A test that does not fail when the code breaks is worthless regardless of how clean it reads, which is why the verification step above is the part to spend your review time on.

**The rule of thumb:** **treat source code (`src/`) as production‑grade code** with as good as possible code quality. It should follow the standards defined in our design documents and uphold solid engineering practices — DRY, KISS, clarity, maintainability, long‑term stability, etc. In contrast, test code serves a different purpose. **The goal for test code (`test/`) is to be correct, readable, and focused on covering the risk, and stop there**. They validate behaviour, and while they should absolutely maintain reasonable quality, they do not need to be elegant, abstract, or architecturally impressive. Their **primary objective is confidence in tested code (i.e. proving the source code is correct), not good code quality**. Avoid over‑engineering test code — the value lies in what the tests verify, not in how clever or intricate the test code is or how well it adheres to traditional software engineering principles. Unlike source code, test code is not shipped to production, is not consumed by downstream systems, does not need long‑term architectural stability, and should not consume engineering time that is better spent elsewhere. Keeping tests simple and almost fully [AI-generated](#generating-tests-with-ai) frees time and attention for the things that matter most: strengthening the application code, improving documentation, and reducing complexity across the system.