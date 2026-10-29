# DevHub Go SDK

Native Go module for shared integrations. The initial root package `sdk` documents the package family; no domain API or vendor clients exist yet.

---

## Table of Contents

- [Module and installation](#module-and-installation)
- [Development](#development)
- [Adding integrations](#adding-integrations)
- [Releases](#releases)

---

## Module and installation

Requires Go 1.25 or newer. The module path is `github.com/CollinPoetoehena/devhub-sdks/go`. After the corresponding release tag has actually been published, run this in a consuming module:

```sh
go get github.com/CollinPoetoehena/devhub-sdks/go@v0.1.0
```

Future domain packages live below that path, such as `/dns`; do not import an example domain before it exists. For local development across checkouts, use a local Go workspace rather than committing machine-specific `replace` paths.

For a private Git host/repository, configure Git credentials separately and set an appropriate `GOPRIVATE` pattern before resolving the module. `GOPRIVATE` controls proxy/checksum handling; it does not authenticate Git.

---

## Development

From this directory:

```sh
gofmt -w .
go vet ./...
go test ./...
go build ./...
```

There are no Go runtime dependencies, so `go.sum` is not needed yet. There are also no behavioral tests because there is no domain implementation; the initial `go test` run only compiles the package. Add meaningful tests alongside the first capability, not placeholder assertions.

---

## Adding integrations

Use focused domain packages and short Go package names, not a mechanical translation of Python classes. Return errors with useful context, propagate cancellation through `context.Context`, and make client/resource ownership explicit. Reuse upstream clients and extract `internal/` helpers only after concrete reuse appears.

Keep provisioning and application workflows outside the module. Unit and local-server tests must not depend on a live homelab; any future live integration tests require explicit opt-in, an approved target, and cleanup.

---

## Releases

Follow the [release procedure](../docs/releases.md#go-release). The repository tag is `go/v0.1.0`, while the consumer selects module version `v0.1.0`. A v2 release needs a deliberate module-path and workflow migration; the current guard rejects it.
