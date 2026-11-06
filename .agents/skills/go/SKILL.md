---
name: go
description: 'Go patterns, conventions, testing, and tooling for DevHub repositories: error handling, interfaces, concurrency, context, naming, version-specific APIs, table-driven tests, fuzzing, benchmarks, and gofmt, golangci-lint, and govulncheck setup. Use when writing, testing, reviewing, or setting up Go code. Opens one focused reference per task.'
---

# Go

Index for Go work. Open only the reference the task needs; the Go and common instructions take precedence over the references.

## When to Use This Skill

- Writing, refactoring, or reviewing Go code
- Designing Go packages, interfaces, or concurrency
- Writing table-driven tests, benchmarks, or fuzz tests
- Setting up or changing Go modules, linters, or CI checks

## Steps

1. **Write or change code.** Open [references/patterns.md](references/patterns.md) for error handling, concurrency, interface design, package organization, struct design, and performance patterns.
2. **Check conventions.** Open [references/conventions.md](references/conventions.md) for naming, formatting, version-specific APIs, HTTP handlers and clients, and readers and buffers.
3. **Write or change tests.** Open [references/testing.md](references/testing.md) for table-driven tests, subtests, helpers, golden files, mocking with interfaces, benchmarks, fuzzing, and coverage.
4. **Set up or change tooling.** Open [references/tooling.md](references/tooling.md) for commands, golangci-lint configuration, and vulnerability checks.
5. **Validate.** Run the validation commands from the Go instructions and report each result.

## Gotchas

- **Typed nil in an interface:** an interface holding a nil pointer is not `nil`; return a literal `nil` for `error` results.
- **Loop variables before Go 1.22:** when `go.mod` declares a version below 1.22, loop variables are shared across iterations, so closures and goroutines capture the last value.
- **`defer` in loops:** deferred calls run when the function returns, not per iteration; move the loop body into a function.
- **Concurrent map writes:** maps are not safe for concurrent writes and crash the program; guard them with a mutex.
- **Shared slice backing arrays:** `append` to a sub-slice can overwrite the caller's data; copy or use a full slice expression.
- **No default HTTP timeout:** `http.DefaultClient` waits forever; configure a client with a `Timeout`, and always close response bodies.

## References

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Go standard library](https://pkg.go.dev/std)
