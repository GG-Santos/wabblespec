# Python Reference

> **Type:** Language reference | Loaded by platform packages on demand.

---

## Toolchain

| Tool | Decision | Notes |
|---|---|---|
| Version | 3.11+ (prefer 3.12+) | 3.10 minimum for `match` and `TypeAlias` |
| Package manager | uv (preferred) / pip + venv | uv is 10–100x faster than pip |
| Lint + format | ruff | Replaces flake8 + black + isort — one tool |
| Type checker | mypy (strict) / pyright | `strict = true` in mypy config |
| Test | pytest | |
| Task runner | just / Makefile | |

---

## Project Structure

```
project/
  src/
    mypackage/
      __init__.py
      py.typed          # Marker file — declares package ships type stubs
  tests/
  pyproject.toml        # Single source of truth for deps, build, lint config
  uv.lock               # Committed — equivalent to package-lock.json
  .python-version       # Pin Python version for uv
```

**`src/` layout** — prevents accidental import of uninstalled package. Always use it for libraries.

---

## pyproject.toml (minimal)

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.ruff]
target-version = "py311"
line-length = 88
[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I"]

[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## Type Hints

Type hints required for all library code. Optional for scripts, but preferred.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence  # avoid runtime import cycle

def process(items: list[str], limit: int = 10) -> dict[str, int]:
    ...

# Use `|` union syntax (3.10+), not Union[]
def parse(value: str | int | None) -> str:
    ...
```

**No `# type: ignore` without comment explaining why.** Each suppression is a debt entry.

---

## Async

```python
import asyncio

# Use asyncio.TaskGroup (3.11+) — not asyncio.gather for exception safety
async def fetch_all(urls: list[str]) -> list[str]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]
```

`asyncio.TaskGroup` cancels sibling tasks on first exception — safer than `gather`.

---

## Non-Negotiable Rules

1. `uv.lock` (or `requirements.txt` with pinned hashes) committed — reproducible installs.
2. `py.typed` marker file in library packages — required for mypy to check callers.
3. No mutable default arguments: `def f(items=[])` is a bug. Use `None` and assign inside.
4. No bare `except:` — always catch specific exception types.
5. `pathlib.Path` over `os.path` for all file operations.
6. Secrets via environment variables — never hardcoded. Read with `os.environ["KEY"]` (raises if missing, not `os.getenv` which silently returns None).

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Different behavior across environments | Float version pin (`>=1.2`) | Pin exact versions in lockfile |
| mypy passes, runtime fails | Missing `py.typed`, no strict mode | Add `py.typed`, enable `strict = true` |
| Test pollution between runs | Shared mutable state | Use fixtures with `yield` for setup/teardown |
| Silent None propagation | `os.getenv` returns None, no check | Use `os.environ["KEY"]` or validate at startup |
| Mutable default arg bug | `def f(items=[])` | Use `def f(items: list | None = None)` |
