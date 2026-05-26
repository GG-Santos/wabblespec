from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_SRC = ROOT / "packages" / "memory" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


def _load_script(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mcp_setup_uses_memory_server_name_and_checkout_launcher(monkeypatch, capsys):
    import memory.cli as cli

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(cli, "_current_python_has_server_dependencies", lambda: False)

    class Args:
        palace = None

    cli.cmd_mcp(Args())

    output = capsys.readouterr().out.replace("\\", "/")
    assert "mcp add memory --" in output
    assert "scripts/memory-mcp.py" in output
    assert "mcp add wabblespec_memory" not in output
    assert "Dependency note:" in output


def test_memory_mcp_help_does_not_import_server(monkeypatch, capsys):
    launcher = _load_script(ROOT / "scripts" / "memory-mcp.py", "memory_mcp_launcher_test")
    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "memory.mcp_server":
            raise AssertionError("--help must not import the MCP server")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(sys, "argv", ["memory-mcp.py", "--help"])
    monkeypatch.setattr(builtins, "__import__", guarded_import)

    launcher.main()

    output = capsys.readouterr().out
    assert "usage: memory-mcp [--palace PATH]" in output


def test_neutral_bootstrap_script_exists_and_legacy_wrappers_delegate_to_it():
    neutral = ROOT / "scripts" / "memory-bootstrap.py"
    legacy = (ROOT / "scripts" / "wabblespec-memory-bootstrap.py").read_text(encoding="utf-8")
    retired = (ROOT / "scripts" / "wabblespec-mempalace-bootstrap.py").read_text(
        encoding="utf-8"
    )

    assert neutral.is_file()
    assert 'with_name("memory-bootstrap.py")' in legacy
    assert 'with_name("memory-bootstrap.py")' in retired
