---
description: "Use when writing, testing, or reviewing Rust code: toolchain defaults, essential conventions, and validation commands alongside the common guidelines."
applyTo: "**/*.rs,**/Cargo.toml,**/Cargo.lock,**/rust-toolchain.toml"
---

# Rust Guidelines

Use general best practices for Rust and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Rust, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

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

Use the `rust` skill for additional Rust procedures and references.

## References

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [Clippy documentation](https://doc.rust-lang.org/clippy/)

Use relevant available skills for additional procedures and references.
