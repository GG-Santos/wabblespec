#!/usr/bin/env python3
"""Copy legacy backend collections into WabbleSpec Memory collection names."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Minimal primer: find repo root and add to sys.path so _shared is importable.
def _primer() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")


ROOT = _primer()


def _require_backend():
    """Import the memory backend, with a clear error if not installed."""
    try:
        from _shared.memory_backend import (  # noqa: PLC0415
            CLOSETS_COLLECTION,
            DRAWERS_COLLECTION,
            LEGACY_CLOSETS_COLLECTION,
            LEGACY_DRAWERS_COLLECTION,
            get_collection,
            get_legacy_collection,
            memory_path,
        )
        return {
            "CLOSETS_COLLECTION": CLOSETS_COLLECTION,
            "DRAWERS_COLLECTION": DRAWERS_COLLECTION,
            "LEGACY_CLOSETS_COLLECTION": LEGACY_CLOSETS_COLLECTION,
            "LEGACY_DRAWERS_COLLECTION": LEGACY_DRAWERS_COLLECTION,
            "get_collection": get_collection,
            "get_legacy_collection": get_legacy_collection,
            "memory_path": memory_path,
        }
    except ModuleNotFoundError as exc:
        print(
            f"ERROR: WabbleSpec Memory backend not available ({exc}).\n"
            "Install with: python -m pip install -e packages/memory",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc


def _count_or_zero(collection_name: str, *, legacy: bool = False, be: dict) -> int:
    try:
        collection = (
            be["get_legacy_collection"](collection_name, create=False)
            if legacy
            else be["get_collection"](collection_name, create=False)
        )
        return int(collection.count())
    except Exception:
        return 0


def _open_legacy(collection_name: str, be: dict):
    try:
        return be["get_legacy_collection"](collection_name, create=False)
    except Exception:
        return None


def _read_batch(collection, offset: int, batch_size: int):
    try:
        return collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas", "embeddings"],
        )
    except Exception:
        return collection.get(limit=batch_size, offset=offset, include=["documents", "metadatas"])


def _copy_batch(target, batch) -> tuple[int, bool]:
    ids = list(batch.ids or [])
    if not ids:
        return 0, True
    documents = list(batch.documents or [""] * len(ids))
    metadatas = list(batch.metadatas or [{}] * len(ids))
    embeddings = batch.embeddings

    if len(documents) < len(ids):
        documents.extend([""] * (len(ids) - len(documents)))
    if len(metadatas) < len(ids):
        metadatas.extend([{}] * (len(ids) - len(metadatas)))

    if embeddings is not None:
        try:
            target.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
            return len(ids), True
        except Exception:
            pass

    target.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids), False


def migrate_pair(
    old_name: str,
    new_name: str,
    *,
    apply: bool,
    batch_size: int,
    be: dict,
) -> dict[str, Any]:
    old_collection = _open_legacy(old_name, be)
    old_count = int(old_collection.count()) if old_collection is not None else 0
    before_count = _count_or_zero(new_name, be=be)

    report: dict[str, Any] = {
        "old_collection": old_name,
        "new_collection": new_name,
        "old_count": old_count,
        "new_count_before": before_count,
        "copied": 0,
        "embeddings_preserved": None,
        "applied": apply,
        "verified": False,
    }

    if not apply or old_collection is None or old_count == 0:
        report["new_count_after"] = before_count
        report["verified"] = old_count == 0 or before_count >= old_count
        return report

    target = be["get_collection"](new_name, create=True)
    embeddings_preserved = True
    offset = 0
    while offset < old_count:
        batch = _read_batch(old_collection, offset, batch_size)
        copied, preserved = _copy_batch(target, batch)
        if copied == 0:
            break
        report["copied"] += copied
        embeddings_preserved = embeddings_preserved and preserved
        offset += copied

    after_count = _count_or_zero(new_name, be=be)
    report["new_count_after"] = after_count
    report["embeddings_preserved"] = embeddings_preserved
    report["verified"] = after_count >= old_count
    return report


def write_receipt(payload: dict[str, Any], memory_path_fn) -> Path:
    receipts_dir = Path(memory_path_fn()) / "migration-receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = receipts_dir / f"memory-backend-migration-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate WabbleSpec Memory backend collections")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing")
    parser.add_argument("--apply", action="store_true", help="Copy legacy collections into new names")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()

    # Defer backend import to after arg parse so --help works without chromadb.
    be = _require_backend()

    apply = bool(args.apply and not args.dry_run)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory_path": be["memory_path"](),
        "mode": "apply" if apply else "dry-run",
        "collections": [
            migrate_pair(
                be["LEGACY_DRAWERS_COLLECTION"],
                be["DRAWERS_COLLECTION"],
                apply=apply,
                batch_size=args.batch_size,
                be=be,
            ),
            migrate_pair(
                be["LEGACY_CLOSETS_COLLECTION"],
                be["CLOSETS_COLLECTION"],
                apply=apply,
                batch_size=args.batch_size,
                be=be,
            ),
        ],
        "preserved_files": [
            "knowledge_graph.sqlite3",
            "tunnels.json",
            "hallways.json",
            "*.json memory artifacts",
        ],
    }
    payload["verified"] = all(item["verified"] for item in payload["collections"])

    if apply:
        receipt = write_receipt(payload, be["memory_path"])
        payload["receipt"] = str(receipt)

    print(json.dumps(payload, indent=2))
    return 0 if (not apply or payload["verified"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
