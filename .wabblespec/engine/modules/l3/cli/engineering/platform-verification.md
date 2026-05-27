# CLI Engineering — Platform Verification

How to run and interpret the CLI verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# From project root, after build:
python scripts/run-platform-gates.py --platform cli

# Or manually, per gate:
bash modules/l3/cli/verification/run-gates.sh <tool-binary>
```

---

## Per-Language Test Harness

### Node CLI
```bash
npm run build
node dist/cli.js --version
node dist/cli.js --help
time node dist/cli.js --version    # startup gate
node dist/cli.js <cmd> | cat       # pipe gate
```

### Python CLI
```bash
pip install -e .
python -m <package> --version
time python -m <package> --version
python -m <package> <cmd> | cat
```

### Go CLI
```bash
go build -o ./bin/<tool> ./cmd/<tool>
./bin/<tool> --version
time ./bin/<tool> --version
./bin/<tool> <cmd> | cat
```

### Rust CLI
```bash
cargo build --release
./target/release/<tool> --version
time ./target/release/<tool> --version
./target/release/<tool> <cmd> | cat
```

---

## Interpreting Results

**Gate PASS:** All exit codes correct, outputs match contracts, timing within budget.

**Gate FAIL — startup time over budget:**
- Profile import/load time: `node --trace-require dist/cli.js --version 2>&1 | head -50`
- Python: `python -X importtime -m <package> --version 2>&1 | head -50`
- Identify heaviest import and defer it to subcommand load time

**Gate FAIL — ANSI in pipe:**
- Find all `chalk`, `kleur`, `colorama`, `termcolor` uses
- Ensure TTY detection wraps all color output
- Pattern: `if (process.stdout.isTTY) { useColor() } else { noColor() }`

**Gate FAIL — exit code mismatch:**
- Trace all exit paths: search for `process.exit(`, `sys.exit(`, `os.Exit(`, `std::process::exit(`
- Map each to declared exit code registry
- Add missing exit codes to registry OR align code to registry

**Gate FAIL — credential arg accepted:**
- Search for arg definitions that include: `api_key`, `apikey`, `password`, `secret`, `token`, `key`
- Convert each to env var loading
- Add migration note to changelog if breaking change

---

## Regression Prevention

After gates pass once:
1. Record gate results in platform activation receipt
2. Add gate checks to CI (see build-toolchain.md)
3. Any change to arg parsing, output format, or config loading requires re-running all gates
4. Gate results are not cached — run fresh on each release candidate
