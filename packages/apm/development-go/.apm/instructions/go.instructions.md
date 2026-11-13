---
description: "Use when writing, testing, or reviewing Go code: toolchain defaults, essential conventions, and validation commands alongside the common guidelines."
applyTo: "**/*.go,**/go.mod,**/go.sum"
---

# Go Guidelines

Use general best practices for Go and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Go, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

## Toolchain

Follow the repository's existing tooling. For new modules, default to:

- **Go version:** the `go` directive in `go.mod`, set to a supported release; add a `toolchain` line only when a newer toolchain is required.
- **Formatting:** `gofmt` and `goimports`.
- **Static analysis:** `go vet` and `golangci-lint` v2 with a committed `.golangci.yml`.
- **Tests:** `go test` with the race detector.
- **Vulnerability audit:** `govulncheck`.

## Rules

- Write exactly one `package` clause per file, matching the other files in the directory; check the existing clause before replacing file content.
- Check every returned error; wrap it with context using `fmt.Errorf("...: %w", err)`, inspect it with `errors.Is` or `errors.As`, and either handle or return it, never both log and return.
- Pass `context.Context` as the first parameter of functions that do I/O or can block; never store it in a struct.
- Give every goroutine a defined exit and an owner that waits for it; protect shared state with channels or `sync` primitives.
- Accept interfaces and return concrete types; define interfaces where they are used.
- Use only language features and APIs supported by the `go` directive, such as `sync.WaitGroup.Go` from Go 1.25 and method patterns in `net/http.ServeMux` from Go 1.22.
- Use `any` instead of `interface{}`, and close files and response bodies with `defer` after checking the error.

## Validation

Run from the module root; use the repository's configured commands when they differ:

```sh
gofmt -l .
go vet ./...
golangci-lint run
go test -race ./...
govulncheck ./...
go mod tidy -diff
```

`gofmt -l` and `go mod tidy -diff` must print nothing.

Use the `go` skill for additional Go procedures and references.

## References

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Go Modules Reference](https://go.dev/ref/mod)
- [Go release history](https://go.dev/doc/devel/release)
- [golangci-lint](https://golangci-lint.run/)
- [govulncheck](https://go.dev/doc/security/vuln/)

Use relevant available skills for additional procedures and references.
