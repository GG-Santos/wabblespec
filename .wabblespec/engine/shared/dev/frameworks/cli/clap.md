# Clap (Rust CLI)

Loaded by Apply when clap in Cargo.toml is detected.

## Version baseline

clap 4.x with derive macro (preferred over builder API).

## Derive macro pattern

```rust
use clap::{Parser, Subcommand, Args};

#[derive(Parser)]
#[command(name = "tool", about = "One-line description", version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    #[arg(short, long, global = true)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Subcommand description
    Sub(SubArgs),
}

#[derive(Args)]
struct SubArgs {
    /// Positional argument description
    name: String,

    /// Output file
    #[arg(short, long, default_value = "-")]
    output: String,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Sub(args) => run_sub(args, cli.verbose),
    }
}
```

## Exit codes

Clap automatically handles:
- Exit 0: `Cli::parse()` succeeds
- Exit 2: bad arguments (clap prints usage)
- Exit 1: user code must `std::process::exit(1)` or return `Err` from `main()`

Recommended main:

```rust
fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    // anyhow::Result: exit 1 + print error on Err
    run(cli)?;
    Ok(())
}
```

## Stdout / stderr

```rust
use std::io::{self, Write};

println!("data to stdout");
eprintln!("message to stderr");

// Or for testability:
writeln!(std::io::stdout(), "data")?;
writeln!(std::io::stderr(), "error")?;
```

## Shell completion

```rust
use clap::CommandFactory;
use clap_complete::{generate, Shell};

fn print_completions(shell: Shell) {
    let mut cmd = Cli::command();
    generate(shell, &mut cmd, "tool", &mut io::stdout());
}
```

Add a `completions` subcommand to generate shell completions on demand.

## Distribution

- `cargo build --release` produces a static binary (with musl on Linux for max portability)
- Cross-compile: `cross` crate for targeting non-host platforms
- Publish to crates.io + `cargo install tool` for developer distribution
- GitHub Releases + `cargo-dist` or goreleaser for binary release automation

## Testing

```rust
#[test]
fn test_subcommand() {
    let cli = Cli::try_parse_from(["tool", "sub", "myarg"]).unwrap();
    assert!(matches!(cli.command, Commands::Sub(_)));
}

#[test]
fn test_bad_args() {
    let result = Cli::try_parse_from(["tool", "sub"]);
    assert!(result.is_err());
}
```

Use `try_parse_from` (returns Result) instead of `parse_from` (panics) in tests.
