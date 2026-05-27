# Engineering Gateway — Dependency Standards

Universal dependency hygiene standards. Platform modules handle platform-specific package managers.

---

## Dependency Freshness

**Rule:** No direct dependency more than 2 major versions behind current stable.

Why major versions matter: each skipped major version represents accumulated breaking changes, security patches, and deprecations that must eventually be resolved. The further behind, the harder the migration.

**Measurement:**
```bash
# Node — npm-check or npm outdated
npx npm-check --update-all --skip-unused  # interactive
npm outdated                               # list all outdated

# Python — pip-outdated or pip list --outdated
pip list --outdated --format=columns

# Go — go list -u
go list -u -m all

# Rust — cargo outdated
cargo outdated
```

**Action on finding:** Direct dependency 2+ major versions behind → open ticket, schedule update in next sprint. Do not defer indefinitely.

**Transitive dependencies:** Do not chase transitive dependency versions — only when a vulnerability requires it.

---

## EOL Runtime Detection

**Rule:** Project must not run on an EOL runtime in production.

**EOL status sources:**
- Node: https://endoflife.date/nodejs — LTS releases only
- Python: https://endoflife.date/python
- Go: two most recent minor releases supported
- Rust: latest stable (rolling)

**Common EOL violations:**
- Node 16 (EOL 2023-09-11)
- Python 3.8 (EOL 2024-10-07)
- Node 18 (EOL 2025-04-30)

**Enforcement:**
```bash
# Declare runtime version in project (then CI checks it):
# Node: .nvmrc or .node-version
# Python: .python-version or pyproject.toml [tool.python.requires-python]
# Go: go.mod `go` directive

# CI check (example for Node):
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
  echo "FAIL: Node $NODE_VERSION is EOL. Use Node 20+."
  exit 1
fi
```

---

## Lock File Policy

**Rule:** Lock files are committed and up-to-date.

| Ecosystem | Lock file | Committed |
|---|---|---|
| Node | `package-lock.json` or `yarn.lock` or `pnpm-lock.yaml` | Yes |
| Python (app) | `requirements.txt` pinned exact OR `poetry.lock` | Yes |
| Python (library) | No lock file — specify ranges in `pyproject.toml` | N/A |
| Go | `go.sum` | Yes |
| Rust (binary) | `Cargo.lock` | Yes |
| Rust (library) | `Cargo.lock` | No (gitignored) |

**Lock file freshness:** CI must verify lock file is up to date with manifest:
```bash
# Node
npm ci  # fails if package-lock.json is out of sync with package.json

# Python (Poetry)
poetry check

# Go
go mod verify

# Rust
cargo verify-project
```

---

## Dependency Minimalism

**Rule:** Each dependency added is a conscious decision. No unused dependencies.

**Unused dependency detection:**
```bash
# Node
npx depcheck

# Python
pip-autoremove --list  # or: importchecker

# Go
go mod tidy  # removes unused, fails if go.mod changes after running
```

**Addition criteria:** Before adding a dependency, ask:
1. Is this functionality available in the standard library? (Prefer stdlib)
2. Is the dependency actively maintained? (Last commit < 12 months ago)
3. Does it have a security track record? (Check CVE history)
4. What is the transitive dependency cost?

**Ban list pattern:** Some dependencies are categorically banned — maintain a `depcheck.json` or equivalent config with project-specific banned packages.

---

## Private Registry Configuration

**If using a private npm/PyPI/Cargo registry:**

**Rule:** Registry source must be locked — no fallback to public registry.

```bash
# npm — prevent fallback to public registry for scoped packages
# .npmrc:
@myorg:registry=https://private.registry.example.com
//private.registry.example.com/:_authToken=${REGISTRY_TOKEN}
# Do NOT add: fallback-registry=https://registry.npmjs.org

# pip — index-url replaces default, extra-index-url adds but allows fallback (avoid)
# pip.conf:
[global]
index-url = https://private.pypi.example.com/simple/
# Avoid extra-index-url for security-sensitive packages (dependency confusion attack)
```

**Dependency confusion prevention:** For all internal packages, ensure they are published to private registry with a scope or namespace that cannot be claimed on the public registry.
