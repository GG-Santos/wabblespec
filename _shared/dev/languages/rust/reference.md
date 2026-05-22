# Rust Reference

> **Type:** Language reference | Loaded by platform packages on demand.

---

## Toolchain

| Tool | Decision | Notes |
|---|---|---|
| Toolchain pin | `rust-toolchain.toml` | Committed — pins stable/nightly + components |
| Format | `rustfmt` | `cargo fmt --check` in CI |
| Lint | `clippy` | `cargo clippy -- -D warnings` — warnings as errors |
| Test | `cargo test` | Unit + integration + doc tests |
| Build | `cargo build --release` | Never ship debug builds |

```toml
# rust-toolchain.toml
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy"]
```

---

## Cargo.lock Policy

| Target | Cargo.lock |
|---|---|
| Binary / application | **Committed** — reproducible builds |
| Library (crate.io publish) | `.gitignore`d — consumers set their own lock |

---

## Error Handling

Use `thiserror` for library errors, `anyhow` for application errors.

```rust
// Library: typed errors with thiserror
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

// Application: anyhow for ergonomic propagation
use anyhow::{Context, Result};

fn load_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read config from {path}"))?;
    Ok(toml::from_str(&content)?)
}
```

**Never `.unwrap()` in production paths.** Use `?`, `expect("invariant: ...")` with explanation, or explicit match.

---

## Ownership and Borrowing

```rust
// Prefer borrowing over cloning
fn process(data: &[u8]) -> usize { data.len() }  // borrow
fn take_ownership(data: Vec<u8>) { ... }          // only if you need to

// Avoid premature cloning
// Bad:
let result = expensive_fn(data.clone());
// Good:
let result = expensive_fn(&data);  // if function only reads
```

**Clone is explicit in Rust by design.** Each `.clone()` is a cost marker — review them.

---

## Async (Tokio)

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Use tokio::spawn for concurrent tasks
    let handle = tokio::spawn(async move {
        fetch_data().await
    });
    let result = handle.await??;  // double ? — JoinError + inner error
    Ok(())
}

// Structured concurrency with JoinSet
let mut set = tokio::task::JoinSet::new();
for url in urls {
    set.spawn(fetch(url));
}
while let Some(result) = set.join_next().await {
    handle(result??);
}
```

---

## Non-Negotiable Rules

1. `rust-toolchain.toml` committed — all contributors use same toolchain.
2. `clippy -- -D warnings` in CI — no warnings in production code.
3. No `.unwrap()` in non-test code without documented invariant: `expect("msg")`.
4. No `unsafe` without safety comment explaining why it's sound.
5. `cargo audit` in CI — check for known vulnerabilities in dependencies.
6. Binaries: `Cargo.lock` committed. Libraries: `Cargo.lock` gitignored.

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Borrow checker fight | Over-eager ownership | Borrow instead of clone; restructure lifetimes |
| Async deadlock | Holding non-Send type across await | Use `drop(guard)` before `.await` |
| Binary size bloat | Debug info in release | `cargo build --release`; add `strip = true` to profile |
| Dependency compile time | Too many dependencies | Audit with `cargo tree`; prefer std where possible |
| `unwrap` panic in prod | Optimistic assumption | Replace with `?` or `expect` with invariant comment |
