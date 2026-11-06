---
name: rust
description: 'Rust patterns, conventions, testing, and tooling for DevHub repositories: ownership and borrowing, error handling, enums, traits and generics, iterators, concurrency, unsafe code, crate structure, unit and integration tests, proptest, mockall, and cargo, clippy, and cargo-audit setup. Use when writing, testing, reviewing, or setting up Rust code. Opens one focused reference per task.'
---

# Rust

Index for Rust work. Open only the reference the task needs; the Rust and common instructions take precedence over the references.

## When to Use This Skill

- Writing, refactoring, or reviewing Rust code
- Designing crate structure, traits, or error types
- Writing unit, integration, async, property-based, or doc tests
- Setting up or changing Cargo, Clippy, or CI checks

## Steps

1. **Write or change code.** Open [references/patterns.md](references/patterns.md) for ownership, error handling, enums and pattern matching, traits and generics, iterators, concurrency, unsafe code, and the module system.
2. **Check conventions.** Open [references/conventions.md](references/conventions.md) for naming, API design guidelines, patterns to follow and avoid, and the quality checklist.
3. **Write or change tests.** Open [references/testing.md](references/testing.md) for unit and integration tests, error and panic tests, async tests, proptest, mockall, doc tests, benchmarks, and coverage.
4. **Set up or change tooling.** Open [references/tooling.md](references/tooling.md) for commands, toolchain and lint configuration, and dependency audits.
5. **Validate.** Run the validation commands from the Rust instructions and report each result.

## Gotchas

- **Lock guards across `.await`:** holding a `std::sync::MutexGuard` across `.await` makes the future non-`Send` or deadlocks; drop the guard first or use an async mutex.
- **Integer overflow differs by profile:** overflow panics in debug builds and wraps in release builds; use `checked_`, `saturating_`, or `wrapping_` operations explicitly.
- **String slicing by byte:** `&s[a..b]` panics when an index is not on a character boundary; use `chars()` or `char_indices()`.
- **Parallel tests share the process:** `cargo test` runs tests on several threads, so tests that change environment variables or shared files must be serialized.
- **Edition changes behavior:** some syntax and semantics depend on the crate's `edition`; check it before applying newer idioms.

## References

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust standard library](https://doc.rust-lang.org/std/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
