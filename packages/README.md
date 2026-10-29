TODO: add here generic packages explanations

TODO: add what is not in here, such as Ansible, Terraform, etc.:
- TODO: add here only a README.md with stating Ansible is versioned through Git and these are few roles I use and the ones I do use is not generic such as proxmox is only for my homelab and not generic for my personal projects, etc.
- TODO: then add devhub-ansible-users is generic but that is hosted separate, etc.








################################### Old: integrate with new setup in DevHub repo later

# DevHub SDKs

> TODO: Just added this for initial repository setup and documentation. No actual code added yet, but the structure and workflows are in place. Add code later.

Independent Python and Go SDKs for reusable integrations, maintained together in one repository. This initial foundation provides packaging, checks, and release workflows; it does **not** yet provide DNS, storage, or other vendor integrations.

For shared package design and engineering practices, see [DevHub's Engineering & Coding Reference](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/README.md). This repository documents its own setup, design decisions, and exceptions.

---

## Table of Contents

- [Packages](#packages)
- [Language choices](#language-choices)
- [Design and boundaries](#design-and-boundaries)
- [Development](#development)
- [Releases](#releases)

---

## Packages

| Package | Identifier | Requirements | Release tag |
|---------|------------|--------------|-------------|
| [Python](python/README.md) | Distribution `devhub-python-sdk`; import `devhub_python_sdk` | Python 3.12+ | `python/v0.1.0` |
| [Go](go/README.md) | Module `github.com/CollinPoetoehena/devhub-sdks/go` | Go 1.25+ | `go/v0.1.0` |

Versions and supported capabilities are independent. A Python release does not require a Go release or imply equivalent features. The Python metadata starts at `0.1.0`; no release is implied by this checkout.

---

## Language choices

- **Python for productive automation:** I already use Python extensively at work, and it is a practical choice for scripting, API integrations, operational automation, and connecting existing tools. Its readable syntax, broad ecosystem, and fast development cycle make it useful for turning a recurring task into maintainable automation. Familiarity helps me deliver useful integrations without learning a new stack for every task; Python is not automatically the best fit for every performance or deployment requirement.
- **Go for infrastructure tooling and broader experience:** Go is widely used for cloud-native infrastructure, network services, command-line tools, controllers, and agents. Static typing, compiled executables, built-in concurrency primitives, and a relatively small language make it attractive for dependable operational tooling, while target-platform and dependency constraints still matter. Because I already spend much of my working time with Python, using Go here deliberately broadens my software engineering experience rather than reinforcing only one language. I also find Go enjoyable to write, which matters for a personal project I want to keep using and improving.
- **Depth before more languages:** Python and Go are well-established choices in DevOps, platform automation, and backend/infrastructure software engineering, not the only important languages across all software development. Keeping the initial set small lets me build deeper expertise in their idioms, testing, packaging, and operational behavior instead of spreading maintenance and learning across many stacks. Java, Rust, and other languages are not excluded because they are unsuitable; they simply do not need an SDK here without a concrete consumer or capability that justifies one.
- **Extend when there is a real need:** A Java, Rust, or other native SDK can be added to this repository later, with its own ecosystem conventions, checks, and release lifecycle. Add a language to solve a demonstrated problem or support an actual consumer, not to complete a language checklist or promise identical capabilities everywhere. DevHub's [language and tool overview](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Languages_and_Tools.md#languages-and-tools) provides broader comparisons.

---

## Design and boundaries

- **One maintainer, one repository:** I am the sole maintainer, and these SDKs are part of my wider DevHub ecosystem and intended for frequent use in my own tooling. Keeping the related packages together makes it convenient to move between integrations, review changes, and maintain documentation and CI in one place. At this scope, separate repositories would add settings, navigation, duplicated maintenance, and cross-repository coordination without a corresponding ownership or access-control benefit. One repository is the best fit for my current needs and likely remains sufficient for the foreseeable scope, not a universal rule; see DevHub's [repository organization guide](../reference/engineering/Repository_Organization.md#choose-boundaries-not-repository-counts).
- **One coherent SDK per language:** Keep related domains in one Python distribution and one Go module for now, with focused domain subpackages rather than a separately released package for every integration. That reduces dependency and release coordination for a single maintainer and makes recurring shared behavior easier to maintain. It does not mean one giant client, mandatory imports of every provider, or mixing unrelated applications into the SDK. Each language retains its own package boundary, dependencies, checks, and releases.
- **Large SDKs are a useful precedent, not a template:** Enterprise SDK families such as the [AWS SDK for Go v2](https://github.com/aws/aws-sdk-go-v2) and [Azure SDK for Go](https://github.com/Azure/azure-sdk-for-go) group many related integrations in substantial language-specific repositories. They use separate repositories for different languages, and these Go repositories contain multiple service modules rather than one indivisible installable package. The relevant lesson is that many domains can share a coherent SDK repository, not that their exact packaging or organization should be copied. This project's scope and maintenance capacity are much smaller, so it does not need their organizational complexity.
- **Split only for a demonstrated boundary:** If dependencies, consumers, permissions, ownership, or release coordination eventually make a package or repository split worthwhile, it remains an option. Size alone is not a reason to multiply repositories, and a split is not free: preserve or migrate published identifiers, Python imports, Go module paths, and consumer installation instructions deliberately. Until there is a real benefit, keep the simpler shared repository and native package boundaries.
- `devhub-sdks` deliberately differs from the single-language `devhub-<type>-<topic>` repository convention because it hosts two native SDKs; see [DevHub naming conventions](../docs/PROJECT-STRUCTURE.md#naming-conventions).
- Reuse supported vendor clients; add recurring domain behavior and reliability contracts, not a complete shadow API. Keep Python exceptions/context managers and Go errors/contexts idiomatic instead of translating classes mechanically. DevHub explains [why a shared SDK can be worth the effort](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Packages.md#why-a-shared-sdk-can-be-worth-the-effort) and how to [keep its scope deliberate](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Packages.md#keep-the-scope-deliberate).
- Add the first integration from a real consumer need. Do not pre-create domains, provider interfaces, a universal transport, or synchronous/asynchronous variants without a demonstrated use.
- Infrastructure provisioning, deployment, operational orchestration, credentials, and private homelab configuration remain outside these packages. Applications own environment configuration, business decisions, and adoption of package updates; see [team workflows and reusable layers](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Packages.md#team-workflows-and-reusable-layers).
- Shared semantics may justify shared fixtures later, but no service, FFI bridge, or generated schema framework is needed simply because two languages exist; see [working across languages](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Packages.md#working-across-languages).
- The repository license has not yet been selected. Packaging and technical availability do not grant an open-source license; choose one before distributing for third-party reuse.

---

## Development

Follow the package READMEs for local commands. Python uses uv, Hatchling, Ruff, mypy, and pytest; Go uses its standard toolchain.

DevHub's [Python](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Languages_and_Tools.md#python) and [Go](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Languages_and_Tools.md#go) practices provide language-specific background. Its [testing and validation](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Concepts.md#testing-and-validation) and [documentation](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Concepts.md#documentation) guidance explain the shared approach; this repository retains the concrete commands and supported behavior.

Python CI checks 3.12, 3.13, and 3.14. Go CI checks the minimum 1.25 toolchain and the current stable release. PRs and pushes to `main` run both workflows; each release reruns its language's checks. No job contacts homelab services.

The implemented tests cover release validation and Python distribution contents. Go currently contains only package documentation, so `go test ./...` is a compilation check with no behavioral tests. Add domain tests with the first integration, including failure paths, cancellation/resource handling, and approved opt-in integration targets.

---

## Releases

- [Release procedures](docs/releases.md) explain independent tags, checks, GitHub artifacts, and installation, applying DevHub's shared [versioning and distribution guidance](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Packages.md#versioning-and-distribution).
- Python tags must match the version in `python/pyproject.toml`. Go uses the `go/` tag prefix because its module is in a subdirectory.
- Published tags and artifacts are immutable. Correct mistakes with a new version; do not delete and reuse a consumed version.
- Python releases attach a wheel and source distribution to a GitHub release. Go releases create a source-release entry; Go consumers resolve the tagged module. No binaries or vendor capabilities are fabricated.
- PyPI publishing is intentionally not configured. Git installation and GitHub release artifacts are sufficient initially; add trusted publishing only after choosing the index and registering ownership.
