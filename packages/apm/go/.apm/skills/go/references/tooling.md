# Go Tooling

DevHub defaults for Go tooling, adapted from the tooling section of [ECC `golang-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/golang-patterns/SKILL.md) and updated to golangci-lint v2. Repository configuration and the Go and common instructions take precedence over this reference.

## Defaults

| Concern | Tool | Notes |
|---|---|---|
| Go version | `go` directive in `go.mod` | Optional `toolchain` line for a newer toolchain |
| Formatting | `gofmt`, `goimports` | Run directly or as golangci-lint formatters |
| Static analysis | `go vet`, golangci-lint v2 | The standard linter set includes staticcheck |
| Tests | `go test` | With `-race` and `-cover` |
| Vulnerability audit | `govulncheck` | Focuses on vulnerable code the module actually calls |

## Commands

```sh
# Build and run
go build ./...
go run ./cmd/myapp

# Testing
go test ./...
go test -race ./...
go test -cover ./...

# Static analysis and formatting
go vet ./...
golangci-lint run
golangci-lint fmt

# Modules
go mod tidy
go mod verify

# Vulnerabilities
govulncheck ./...
```

Install golangci-lint from its official binaries rather than with `go install`, and install govulncheck with `go install golang.org/x/vuln/cmd/govulncheck@latest`.

## .golangci.yml

golangci-lint v2 requires `version: "2"`, moves linter settings under `linters.settings`, and configures formatters separately:

```yaml
version: "2"

linters:
  default: standard
  enable:
    - errorlint
    - misspell
    - unconvert
    - unparam
  settings:
    errcheck:
      check-type-assertions: true
    govet:
      enable:
        - shadow

formatters:
  enable:
    - gofmt
    - goimports
```

## References

- [go command](https://pkg.go.dev/cmd/go)
- [gofmt](https://pkg.go.dev/cmd/gofmt)
- [go vet](https://pkg.go.dev/cmd/vet)
- [golangci-lint configuration](https://golangci-lint.run/docs/configuration/file/)
- [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
- [Go Modules Reference](https://go.dev/ref/mod)
