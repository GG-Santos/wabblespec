# Click / Typer (Python CLI)

Loaded by Apply when click or typer imports are detected.

## Click patterns

```python
import click

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """Tool description."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

@cli.command()
@click.argument('name')
@click.option('--output', '-o', type=click.Path(), default='-', 
              help='Output file (- for stdout)')
@click.pass_context
def subcommand(ctx, name, output):
    """Subcommand description."""
    # Implementation
```

### Click decorators

| Decorator | Purpose |
|---|---|
| `@click.command()` | Define a command |
| `@click.group()` | Define a command group |
| `@click.argument()` | Positional argument |
| `@click.option()` | Named option |
| `@click.pass_context` | Inject Context object |

### Click types

- `click.Path()` — file system path with validation options (`exists=True`, `file_okay=True`)
- `click.File()` — opens file automatically; supports `-` for stdin/stdout
- `click.Choice(['a', 'b'])` — enum-style choice with validation
- `click.IntRange(min, max)` — bounded integer

### Error handling

```python
raise click.UsageError("Invalid argument: expected X, got Y")  # exits 2 + prints usage hint
raise click.ClickException("Operation failed: reason")          # exits 1 + prints message
click.echo("Progress message", err=True)                        # stderr
```

## Typer patterns

Typer wraps Click with type annotations:

```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def main(
    name: str,
    verbose: bool = typer.Option(False, '--verbose', '-v'),
    output: Optional[str] = typer.Option(None, '--output', '-o'),
):
    """Tool description."""
    if verbose:
        typer.echo("Running...", err=True)
```

Typer auto-generates help text from docstrings and type annotations. Prefer Typer for new Python CLIs.

## Testing Click/Typer

```python
from click.testing import CliRunner

def test_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['subcommand', 'myarg', '--verbose'])
    assert result.exit_code == 0
    assert 'expected output' in result.output
```

Use `CliRunner.invoke()` — it captures stdout/stderr and does not actually run the process, making tests fast.

## Packaging

- Entry point in `pyproject.toml`:
```toml
[project.scripts]
{tool-name} = "{package}:cli"
```
- Distribute via PyPI or as a binary with PyInstaller/Nuitka
- `pipx install {package}` for global install without environment pollution
