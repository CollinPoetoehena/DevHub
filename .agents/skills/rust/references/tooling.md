# Rust Tooling

DevHub defaults for Rust tooling, adapted from the tooling section of [ECC `rust-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/rust-patterns/SKILL.md). Repository configuration and the Rust and common instructions take precedence over this reference.

## Defaults

| Concern | Tool | Notes |
|---|---|---|
| Toolchain | rustup | Pin in `rust-toolchain.toml` when needed |
| Formatting | rustfmt (`cargo fmt`) | Default style unless `rustfmt.toml` exists |
| Linting | Clippy (`cargo clippy`) | Warnings denied in CI; lint levels in `Cargo.toml` |
| Tests and coverage | `cargo test`, cargo-llvm-cov | |
| Dependency audit | cargo-audit | cargo-deny when licenses and sources also need checks |

## Commands

```sh
# Build and check
cargo build
cargo check                   # fast type checking without code generation
cargo clippy --all-targets --all-features -- -D warnings
cargo fmt --all

# Testing
cargo test
cargo test -- --nocapture     # show println output
cargo test --lib              # unit tests only
cargo test --test integration # one integration test target
cargo llvm-cov                # coverage

# Dependencies
cargo audit                   # known vulnerabilities in Cargo.lock
cargo tree                    # dependency tree
cargo update                  # update within version requirements

# Performance
cargo bench
```

## Configuration

`rust-toolchain.toml` pins the toolchain and components for everyone:

```toml
[toolchain]
channel = "stable"
components = ["clippy", "rustfmt"]
```

Declare lint levels in `Cargo.toml` so local runs and CI agree:

```toml
[package]
name = "my-crate"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"

[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
pedantic = { level = "warn", priority = -1 }
unwrap_used = "warn"
```

Use `unsafe_code = "forbid"` only for crates without unsafe code.

## References

- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [Cargo lints table](https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section)
- [rustup toolchain file](https://rust-lang.github.io/rustup/overrides.html#the-toolchain-file)
- [rustfmt](https://rust-lang.github.io/rustfmt/)
- [Clippy documentation](https://doc.rust-lang.org/clippy/)
- [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
- [cargo-deny](https://embarkstudios.github.io/cargo-deny/)
- [cargo-llvm-cov](https://github.com/taiki-e/cargo-llvm-cov)
