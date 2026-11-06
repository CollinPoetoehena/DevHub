# DevHub Go Package

`devhub-go` is an opt-in APM package for repositories that use Go. It adds one Go instruction and the `go` skill with focused references on top of the [common package](../common/README.md), whose instructions always apply.

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content).

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`go.instructions.md`](.apm/instructions/go.instructions.md) | Instruction (`**/*.go`, `**/go.mod`, `**/go.sum`) | Toolchain defaults, mandatory rules, and validation commands; points to the skill |
| [`go`](.apm/skills/go/SKILL.md) | Skill | Index and gotchas for Go work |
| [`go/references/patterns.md`](.apm/skills/go/references/patterns.md) | Skill reference | Error handling, concurrency, interface design, package organization, struct design, and performance |
| [`go/references/conventions.md`](.apm/skills/go/references/conventions.md) | Skill reference | Naming, formatting, version-specific APIs, HTTP handlers and clients, and readers and buffers |
| [`go/references/testing.md`](.apm/skills/go/references/testing.md) | Skill reference | Table-driven tests, helpers, golden files, mocking, benchmarks, fuzzing, and coverage |
| [`go/references/tooling.md`](.apm/skills/go/references/tooling.md) | Skill reference | Commands, golangci-lint v2 configuration, and govulncheck |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `go/references/patterns.md` | [ECC `golang-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/golang-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Moved the tooling section to `tooling.md` |
| `go/references/conventions.md` | [awesome-copilot `go.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/go.instructions.md) | Adapted | `797337f` (2026-11-06) | Removed the tools and development workflow section, which `tooling.md` and the common Git instructions own |
| `go/references/testing.md` | [ECC `golang-testing`](https://github.com/affaan-m/ECC/blob/main/skills/golang-testing/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | None |
| `go/references/tooling.md` | Tooling section of [ECC `golang-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/golang-patterns/SKILL.md) | Authored | `b38be6a` (2026-11-06) | Rewritten for DevHub defaults; linter configuration updated to the golangci-lint v2 format; govulncheck added |
| Instruction and `SKILL.md` index | DevHub | Authored | Not applicable | None |

---

## Consumption

The package depends on the [common package](../common/README.md), so installing it also installs `devhub-common`. List both in the consumer's `apm.yml` to keep the baseline explicit, then run `apm install`:

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/common
    - CollinPoetoehena/DevHub/packages/apm/go
```

State the Go version and validation commands in the repository's `AGENTS.md`. Changes are recorded in the [changelog](CHANGELOG.md).
