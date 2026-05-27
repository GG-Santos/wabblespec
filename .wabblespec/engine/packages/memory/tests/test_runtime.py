from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_SRC = ROOT / "packages" / "memory" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


def test_configure_project_uses_project_local_runtime(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / ".wabblespec").mkdir(parents=True)
    monkeypatch.chdir(repo)

    from memory.runtime import configure_project

    config = configure_project(repo)

    assert config.memory_path == repo / ".wabblespec" / "memory"
    assert config.runtime_path == config.memory_path / ".runtime"
    assert config.lock_dir == config.runtime_path / "locks"
    assert config.wal_dir == config.runtime_path / "wal"
    assert config.state_dir == config.runtime_path / "hook_state"
    assert os.environ["WABBLESPEC_MEMORY_PATH"] == str(config.memory_path)
    assert os.environ["WABBLESPEC_MEMORY_WAL_DIR"] == str(config.wal_dir)
    assert (config.state_dir / "mine_pids").is_dir()


def test_runtime_config_prevents_home_state_defaults(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    fake_home = tmp_path / "home"
    (repo / ".wabblespec").mkdir(parents=True)
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))

    from memory.runtime import configure_project

    config = configure_project(repo)
    import memory.hooks_cli as hooks_cli
    import memory.knowledge_graph as knowledge_graph

    hooks_cli = importlib.reload(hooks_cli)
    knowledge_graph = importlib.reload(knowledge_graph)

    assert hooks_cli.PALACE_ROOT == config.memory_path
    assert hooks_cli.STATE_DIR == config.state_dir
    assert knowledge_graph.KnowledgeGraph().db_path == str(config.knowledge_graph_path)
    assert not (fake_home / ".wabblespec_memory").exists()


def test_legacy_import_namespace_is_not_used():
    forbidden = [
        "from " + "wabblespec_memory",
        "import " + "wabblespec_memory",
        "wabblespec_memory" + ".",
        "vendor/" + "wabblespec_memory",
        "vendor\\" + "wabblespec_memory",
    ]
    checked_suffixes = {".py", ".md", ".toml", ".yaml", ".yml", ".json"}
    ignored_parts = {".git", "__pycache__", ".wabblespec"}

    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        if ignored_parts.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(term in text for term in forbidden):
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
