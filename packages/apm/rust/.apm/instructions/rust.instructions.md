---
description: "Use when writing, testing, or reviewing Rust code: toolchain defaults, mandatory rules, and validation commands on top of the common instructions."
applyTo: "**/*.rs,**/Cargo.toml,**/Cargo.lock,**/rust-toolchain.toml"
---

# Rust Instructions

These rules add Rust specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `rust` skill before adding modules, tests, or tooling; it opens one reference per task.

## Toolchain

Follow the repository's existing tooling. For new crates, default to:

- **Toolchain:** stable Rust through `rustup`, pinned in `rust-toolchain.toml` when the project needs a specific version.
- **Crate metadata:** the latest stable `edition` and a declared `rust-version` in `Cargo.toml`.
- **Formatting and linting:** `cargo fmt` and `cargo clippy` with warnings denied.
- **Tests:** `cargo test`.
- **Dependency audit:** `cargo audit`.

## Rules

- Return `Result` and propagate errors with `?`; do not use `unwrap()` or `expect()` in library or production paths outside tests and proven invariants.
- Give libraries typed errors, for example with `thiserror`; applications may use `anyhow` with added context.
- Take borrowed parameters such as `&str` and `&[T]` where ownership is not needed, and avoid clones that only satisfy the borrow checker.
- Use `unsafe` only when unavoidable, keep the block minimal, and document its invariants in a `// SAFETY:` comment.
- Never block or hold a `std::sync::Mutex` guard across `.await` in async code; use async primitives or `spawn_blocking`.
- Keep the public API minimal with `pub(crate)` and implement standard traits, such as `Debug`, `Display`, and `From`, where they apply.
- Commit `Cargo.lock` for applications and binaries.

## Validation

Run from the workspace root; use the repository's configured commands when they differ:

```sh
cargo fmt --all --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo audit
```

## References

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [Clippy documentation](https://doc.rust-lang.org/clippy/)
