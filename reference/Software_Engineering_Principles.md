# Coding & Software Engineering Principles

Language-agnostic principles that apply across every project in this repository — Python packages, Ansible roles, Terraform modules, shell scripts, and any potential future languages (e.g. Java, Go, etc.) alike.

These principles are **heuristics, not laws**. They exist to reduce the cost of the *next* change; when two of them conflict (and they often do), pick the one that keeps the code easiest to understand and change.

Language-specific conventions live next to the language:

- [Python Reference & Best Practices](./python/README.md)
- [Ansible](../packages/Ansible.md)
- [Terraform](../packages/Terraform.md)
- [Helm](../packages/Helm.md)

## Table of Contents

- [How to apply these principles](#how-to-apply-these-principles)
  - [They are trade-offs, not rules](#they-are-trade-offs-not-rules)
  - [Scale the rigour to the stakes](#scale-the-rigour-to-the-stakes)
  - [Cases where deliberately "breaking" a principle is correct](#cases-where-deliberately-breaking-a-principle-is-correct)
  - [How to decide, in practice](#how-to-decide-in-practice)
  - [Failure modes on both ends](#failure-modes-on-both-ends)
- [The short list](#the-short-list)
- [DRY — Don't Repeat Yourself](#dry--dont-repeat-yourself)
- [KISS — Keep It Simple](#kiss--keep-it-simple)
- [YAGNI — You Aren't Gonna Need It](#yagni--you-arent-gonna-need-it)
- [SOLID](#solid)
  - [S — Single Responsibility](#s--single-responsibility)
  - [O — Open/Closed](#o--openclosed)
  - [L — Liskov Substitution](#l--liskov-substitution)
  - [I — Interface Segregation](#i--interface-segregation)
  - [D — Dependency Inversion](#d--dependency-inversion)
- [Coupling & Cohesion](#coupling--cohesion)
- [Separation of Concerns](#separation-of-concerns)
- [Composition over Inheritance](#composition-over-inheritance)
- [Law of Demeter](#law-of-demeter)
- [Fail Fast & Principle of Least Astonishment](#fail-fast--principle-of-least-astonishment)
- [Clean Architecture](#clean-architecture)
- [Twelve-Factor App](#twelve-factor-app)
- [OOP — Object-Oriented Programming](#oop--object-oriented-programming)
- [Working principles](#working-principles)
- [When principles conflict](#when-principles-conflict)
- [Further reading](#further-reading)

---

## How to apply these principles

Read the rest of this document as a set of **defaults to reach for**, not a checklist to satisfy. Every principle below was written as a reaction to a specific kind of pain, and each one has a cost that is only worth paying when that pain is actually likely. Applying all of them at maximum strength to every piece of code produces something *worse* than applying none of them: a system where a one-line change touches six files, each of which is technically perfect.

### They are trade-offs, not rules

Every principle buys something and charges something:

| Principle | What it buys | What it charges |
|---|---|---|
| DRY | One place to change a rule; no forgotten copies. | Coupling — every caller of the abstraction now shares its fate. |
| SOLID / Dependency Inversion | Substitutable, testable units. | Indirection — the reader must follow an interface to find the real behaviour. |
| Clean Architecture | Business rules outlive frameworks and databases. | Layers, mappers, and boilerplate for data crossing boundaries. |
| Open/Closed | New variants without editing existing code. | Registries and polymorphism instead of an `if` a junior can read in five seconds. |
| Fail fast | Bugs surface at the boundary. | Less tolerance for messy but survivable real-world input. |

So the question is never "does this follow DRY?" but **"is the coupling I am about to introduce cheaper than the duplication I am about to remove?"** If you cannot say what a principle is buying you *in this specific file*, you are applying it out of habit.

### Scale the rigour to the stakes

The right amount of structure depends on the code's expected lifetime, blast radius, and number of readers:

| Context | Reasonable level of rigour |
|---|---|
| One-off script, spike, or throwaway experiment | Almost none. Make it readable, hard-code what is stable, delete it when done. |
| Internal automation (homelab playbooks, helper scripts) | Clear names, no secrets in code, obvious structure. Do not build plugin systems. |
| A reusable package or shared module | Real interfaces, dependency injection at the seams, tests against the public contract. |
| A long-lived service with several contributors | The full set: layering, explicit boundaries, tests, documented failure behaviour. |

A useful heuristic: **the cost of a principle is paid once, by you, now; the benefit is paid out over the lifetime of the code, to everyone who touches it.** Short-lived code with one reader rarely earns that back.

### Cases where deliberately "breaking" a principle is correct

- **Repeat yourself to stay simple.** Two Ansible roles or two Terraform modules with a few similar-looking blocks are usually healthier than one parameterised super-module with a dozen conditionals. Duplication is visible and local; the wrong abstraction is invisible and global. Prefer duplication when the two copies are likely to *diverge*, when the shared part is small, or when the abstraction would need flags to describe the difference.
- **Skip the interface until the second implementation.** An abstraction extracted from a single example almost always encodes the accident rather than the essence. Wait until you can see what genuinely varies (see [YAGNI](#yagni--you-arent-gonna-need-it)).
- **Keep the layers flat when the domain is thin.** A CLI that reads a file, transforms it, and writes another file does not need entities, use cases, and adapters. Keeping the transform as a pure function already captures ~90% of what Clean Architecture would buy here.
- **Do not fail fast on expected operational noise.** A briefly unreachable peer, a transient DNS failure, or a rate-limited API is a normal condition to retry and degrade around — not a reason to abort. Fail fast on *programmer errors and invalid configuration*, where continuing hides a bug.
- **A longer function can beat five tiny ones.** "Single responsibility" is about reasons to change, not line counts. Splitting a linear, cohesive procedure into fragments that are each called exactly once forces the reader to reassemble it mentally.
- **Match the surrounding code over the "better" pattern.** Consistency inside a file or module is itself a principle. Introducing a new style in one place makes the codebase harder to read than either style used uniformly.

### How to decide, in practice

When you are unsure whether to apply a principle, work through these in order:

1. **Name the pain.** What concrete problem does this prevent — a rule getting out of sync, an untestable dependency, a layer that cannot be swapped? If you cannot name it, do not pay for it.
2. **Estimate the likelihood.** Is that problem probable for *this* code, or is it a scenario you invented to justify the design?
3. **Compare the costs.** Weigh the indirection you are adding against the duplication or rigidity you are removing.
4. **Prefer the reversible option.** Duplication is easy to unify later; a bad abstraction with many callers is expensive to unpick. When genuinely torn, choose the one that is cheaper to undo.
5. **Write down the decision.** If you knowingly deviate, one comment or commit-message line stating *why* turns "sloppy" into "deliberate" for the next reader.

### Failure modes on both ends

Both extremes are real and both are common:

- **Under-applying** — copy-pasted business rules that drift apart, functions that do networking and formatting and persistence at once, credentials in code, no seam to test against. Symptom: every change is risky and nothing can be tested without the real system.
- **Over-applying** — interfaces with one implementation, factories producing factories, config for things that never vary, four files touched to add one field. Symptom: nobody can answer "where does this actually happen?" without a debugger.

Judging which side you are on is a skill built by reading and changing code over time, not by memorising acronyms. The principles below are the vocabulary for that judgement — they are not a substitute for it.

---

## The short list

| Principle | One-line rule | Smell it prevents |
|---|---|---|
| DRY (Don't Repeat Yourself) | Every piece of *knowledge* has one authoritative home. | Same rule changed in three places, two of them forgotten. |
| KISS (Keep It Simple, Stupid) | Prefer the boring solution that a tired reader understands. | Clever one-liners, needless metaprogramming. |
| YAGNI (You Aren't Gonna Need It) | Build what is needed now, not what might be needed. | Config flags and plugin hooks nobody uses. |
| SOLID (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) | Small, substitutable, dependency-inverted units. | God classes, `isinstance` ladders, rigid inheritance. |
| Low coupling / high cohesion | Things that change together live together. | Shotgun surgery across many modules for one change. |
| Separation of concerns | Business rules, I/O, and presentation are separate. | SQL and HTML in the same function. |
| Fail fast | Invalid state stops at the boundary, loudly. | Corrupt data discovered three layers later. |
| Least astonishment | Behaviour matches the name and the convention. | `get_user()` that also writes to the database. |

---

## DRY — Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." — *The Pragmatic Programmer*

DRY is about **knowledge**, not about identical characters. Two functions that happen to look the same today but answer different questions are *not* a DRY violation — merging them couples two things that will diverge.

- Duplicated **business rules**, magic numbers, IP ranges, retry limits, port numbers → extract into one constant/module/variable file.
- Duplicated **structure** with different meanings (e.g. two similar-looking Ansible tasks for different services) → usually leave alone.

The counter-force is **WET** ("write everything twice"): duplicate up to twice, abstract on the third occurrence, once you can actually see what varies. A wrong abstraction is more expensive than the duplication it removed.

```python
# Not DRY: the same retry policy is re-derived in every caller
resp = request(url, retries=3, backoff=2)
resp = request(url, retries=3, backoff=2)

# DRY: one authoritative representation of the policy
DEFAULT_RETRY = RetryPolicy(retries=3, backoff=2)
resp = request(url, retry=DEFAULT_RETRY)
```

---

## KISS — Keep It Simple

Optimise for the reader, not for the writer. Code is read far more often than it is written, and the reader is usually you, months later, during an incident.

- Choose the smallest construct that solves the problem: a function before a class, a class before a framework.
- Avoid speculative indirection — a layer that only ever has one implementation is a layer that only adds a hop.
- Flat beats nested; early returns beat pyramids of `if`.
- If a piece of code needs a comment to explain *what* it does (as opposed to *why*), it is usually too clever.

---

## YAGNI — You Aren't Gonna Need It

Do not build features, options, or abstractions for hypothetical future requirements.

- Cost of building it now: implementation, tests, docs, and the maintenance of code nobody exercises.
- Cost of building it later: usually the same, but with real requirements instead of guessed ones.

YAGNI is **not** an excuse for unextensible code — it is an argument for *simple* code, which is the easiest kind to extend when the requirement actually arrives.

Common violations in this repository's domains: a config option with exactly one possible value, an abstract base class with one subclass, a Terraform variable that is never overridden.

---

## SOLID

Five object-oriented design principles (Robert C. Martin). They are most relevant when designing classes and modules with several implementations; do not force them onto a 30-line script.

### S — Single Responsibility

A module should have **one reason to change** — meaning one stakeholder/actor requesting changes, not "does one thing".

```python
# Two reasons to change: report layout (business) and storage format (ops)
class Report:
    def calculate(self) -> Decimal: ...
    def save_to_disk(self, path: Path) -> None: ...

# One reason each
class Report:
    def calculate(self) -> Decimal: ...

class ReportWriter:
    def save(self, report: Report, path: Path) -> None: ...
```

### O — Open/Closed

Open for extension, closed for modification: adding a new case should mean adding code, not editing a growing `if/elif` chain in the middle of existing logic.

In practice: register new implementations against a protocol/interface, or use a lookup table keyed by type, instead of extending a conditional every time a new variant appears.

### L — Liskov Substitution

Any subclass must be usable wherever the base class is expected, without the caller checking which one it holds. A subclass that raises `NotImplementedError` for an inherited method, narrows accepted inputs, or strengthens preconditions breaks the contract — the inheritance is wrong, not the caller.

### I — Interface Segregation

Many small, focused interfaces beat one fat interface. A consumer should not be forced to depend on methods it never calls; in Python this typically means narrow `Protocol`s (`SupportsRead`, `SupportsClose`) rather than one large abstract base class.

### D — Dependency Inversion

High-level policy should not depend on low-level details; both depend on abstractions.

```python
# Detail-dependent: the scheduler can only ever talk to Postgres
class Scheduler:
    def __init__(self) -> None:
        self._db = PostgresClient(DSN)

# Inverted: the caller decides; tests can pass a fake
class Scheduler:
    def __init__(self, store: JobStore) -> None:
        self._store = store
```

This is what makes code testable without patching internals: dependencies are **injected**, not constructed in place.

---

## Coupling & Cohesion

The two measurements most of the other principles are really about.

| | Meaning | Goal |
|---|---|---|
| **Coupling** | How much one module must know about another's internals. | Low — communicate through narrow, stable interfaces. |
| **Cohesion** | How strongly the elements inside a module belong together. | High — everything in the module serves one purpose. |

Practical signals of high coupling: a change in one module forces edits in several unrelated ones (*shotgun surgery*); tests require elaborate mocks; imports form cycles.

Practical signals of low cohesion: a `utils.py` that grows forever; a class whose fields are used by disjoint sets of methods.

---

## Separation of Concerns

Keep distinct responsibilities in distinct places, and in particular keep **pure logic** separate from **I/O**:

- Parsing/validating input ≠ applying business rules ≠ persisting ≠ presenting.
- Pure functions (no network, no disk, no clock, no globals) are trivially testable and reusable; push side effects to the edges of the system.
- The same idea applies outside application code: Ansible roles separate `defaults/`, `tasks/`, and `templates/`; Terraform separates variables, resources, and outputs.

---

## Composition over Inheritance

Prefer assembling behaviour from small collaborating objects over deep class hierarchies.

Inheritance couples a subclass to the base class's implementation forever and is a single, rigid axis of variation. Composition lets behaviours vary independently and be swapped at runtime.

Use inheritance when there is a genuine "is-a" relationship *and* the Liskov substitution rule holds; use composition (or a `Protocol`) for "has-a"/"can-do" relationships.

---

## Law of Demeter

"Talk only to your immediate friends." A method should call methods on its own fields, its parameters, and objects it created — not walk a chain of foreign objects.

```python
# Train wreck: knows the shape of three other objects
city = order.customer.address.city

# Ask, don't traverse
city = order.shipping_city()
```

Chained access hard-codes the structure of unrelated classes into the caller, so every refactor of those classes ripples outward.

---

## Fail Fast & Principle of Least Astonishment

- **Fail fast** — validate at the system boundary and stop immediately on invalid state, with a message that names the offending value. Do not "helpfully" continue with a default that hides a bug; a crash at the boundary is cheaper to debug than corrupt data found later.
- **Least astonishment** — behaviour must match what the name, signature, and surrounding conventions promise. No hidden writes in a getter, no silent retries, no swallowed exceptions.
- **Errors are part of the API** — document what a unit raises and let unexpected exceptions propagate rather than catching broadly (see [Exceptions](./python/Exceptions.md)).

---

## Clean Architecture

Clean Architecture (Robert C. Martin) — and its relatives *Hexagonal / Ports & Adapters* and *Onion Architecture* — arrange a system as concentric layers with **one rule**: source-code dependencies point **inwards only**.

*Source: [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html), Robert C. Martin.*

```
┌───────────────────────────────────────────────────────────────────┐
│  Frameworks & Drivers: Devices, Web, DB, UI, external interfaces  │
│   ┌───────────────────────────────────────────────────────────┐   │
│   │  Interface Adapters: controllers, gateways, presenters    │   │
│   │   ┌───────────────────────────────────────────────────┐   │   │
│   │   │  Application Business Rules: use cases            │   │   │
│   │   │   ┌───────────────────────────────────────────┐   │   │   │
│   │   │   │  Enterprise Business Rules                │   │   │   │
│   │   │   │  (Entities)                               │   │   │   │
│   │   │   └───────────────────────────────────────────┘   │   │   │
│   │   └───────────────────────────────────────────────────┘   │   │
│   └───────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘

   source-code dependencies ──────────────────────────────→ inwards only
```

An outer ring may name and use anything inside it; an inner ring must not name anything outside it. Control still has to flow back outwards, which is done with **ports** — interfaces declared by the inner layer and implemented by the outer one:

```
                       ┌── owned by the use case layer ──┐

  Controller ──calls──→   «Use Case Input Port»              (interface)
                                   ▲ implements
                                   │
                          Use Case Interactor                (inner ring)
                                   │ calls
                                   ▼
  Presenter  ←implements─  «Use Case Output Port»            (interface)
```

The interactor never mentions the controller or the presenter — it only knows the two ports it owns.

| Layer | Contains | Knows about |
|---|---|---|
| **Entities** | Core domain objects and rules that would exist even without software. | Nothing outside itself. |
| **Use cases** | Application-specific workflows orchestrating entities. | Entities only. |
| **Interface adapters** | Controllers, presenters, repositories, API/CLI mappers. | Use cases and entities. |
| **Frameworks & drivers** | Web framework, database, message broker, filesystem, cloud SDKs. | Everything inwards. |

Key consequences:

- The database, HTTP framework, and cloud provider are **details** — plugged in at the outer ring, replaceable without touching business rules.
- Inner layers define the interfaces (**ports**); outer layers implement them (**adapters**). Crossing a boundary inwards is done via dependency inversion.
- Data crossing a boundary is a simple structure owned by the inner layer — never an ORM row or framework request object leaking inwards.
- The pay-off is testability and longevity; the cost is indirection, so scale the number of layers to the size of the system. A small script does not need four rings — but it still benefits from keeping business logic out of the I/O code.

---

## Twelve-Factor App

A checklist for services that must run reliably in containers and be deployed repeatably — highly relevant to anything deployed in the homelab.

The factors most often violated:

- **Config in the environment** — no credentials, hostnames, or endpoints hard-coded or committed. Config that varies between deploys comes from the environment (or a secret store/vault), not from code.
- **Explicit, isolated dependencies** — pinned and declared (`requirements.txt`/lockfile, `requirements.yml`, provider version constraints), never relying on packages that happen to exist on the host.
- **Stateless processes** — state lives in backing services (database, object store, volume), so a process can be killed and rescheduled at any time.
- **Logs as event streams** — write to stdout/stderr and let the platform collect them; the application does not manage log files or rotation.
- **Dev/prod parity** — the same images, the same provisioning code, the same versions across environments.
- **Disposability** — fast startup and graceful shutdown on `SIGTERM`.

---

## OOP — Object-Oriented Programming

This is a programming paradigm based on the concept of "objects", which are instances of classes that encapsulate both data and behavior. OOP aims to promote code reuse, modularity, and maintainability through principles such as encapsulation, inheritance, and polymorphism. See for explanation [Python reference: Classes & Generics](./python/Classes_Generics.md#object-oriented-programming--fundamentals)

---

## Working principles

- **Boy Scout Rule** — leave the code slightly cleaner than you found it, but keep clean-ups out of unrelated changes so reviews stay readable.
- **Make it work, make it right, make it fast** — in that order, and only measure before optimising. "Premature optimisation is the root of all evil" (Knuth) refers to *unmeasured* optimisation.
- **Technical debt is a deliberate loan** — taking a shortcut is legitimate when it is recorded (issue/TODO with context) and repaid; unrecorded shortcuts are just mess.
- **Small, reversible changes** — small commits and small PRs with one intent each are easier to review, bisect, and revert.
- **Tests describe behaviour** — test the public contract, not private internals, otherwise every refactor breaks the suite.
- **Automate anything done three times** — scripts and playbooks over remembered manual steps; the automation is also the documentation.
- **Document the *why*** — the code already shows the what; comments and commit messages carry the reasoning, constraints, and rejected alternatives.

---

## When principles conflict

They will. Some common tensions and the usual tie-breaker:

| Tension | Tie-breaker |
|---|---|
| DRY vs. low coupling | Prefer duplication over a shared abstraction that couples two things which change for different reasons. |
| SOLID/Clean Architecture vs. KISS & YAGNI | Add a layer or an interface when a second implementation or a real testing need exists — not in anticipation. |
| Fail fast vs. resilience | Fail fast on *programming errors and invalid config*; degrade gracefully on *expected operational failures* (a peer being briefly unreachable). |
| Consistency vs. "better" new pattern | Follow the surrounding conventions; change the convention deliberately and everywhere, not silently in one file. |

The single question worth asking during review: **what will it cost to change this in six months?**

---

## Further reading

- [The Twelve-Factor App](https://12factor.net/)
- [The Clean Architecture (blog.cleancoder.com)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) — DRY, orthogonality, tracer bullets.
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/) — the same ideas, condensed into 19 lines.
