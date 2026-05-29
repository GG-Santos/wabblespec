"""
receipt-db.py — DuckDB receipt store for WabbleSpec.

Replaces 200+ scattered JSON receipt files with a single DuckDB database.
DuckDB reads existing JSON natively via read_json_auto() — no migration needed.

Operations:
    init        Create or open the receipt database
    import      Bulk-import existing JSON receipt files into DuckDB
    write       Write a single receipt JSON to DuckDB (+ optionally keep JSON file)
    query       Run an ad-hoc SQL query against the receipts table
    stats       Print receipt counts and coverage stats
    export      Export a receipt from DuckDB to JSON

Schema (receipts table):
    receipt_id      TEXT PRIMARY KEY    -- filename stem (e.g. wave-1-receipt)
    session_id      TEXT
    module          TEXT
    status          TEXT
    timestamp       TEXT
    wave            INTEGER
    delta_class     TEXT
    receipt_json    TEXT                -- full JSON as stored text

Usage:
    # Initialize the DB:
    python .wabblespec/engine/shared/scripts/receipt-db.py init

    # Import all existing JSON receipts:
    python .wabblespec/engine/shared/scripts/receipt-db.py import

    # Write a receipt JSON to DB (pipe from receipt-writer.py):
    receipt-writer.py ... --out - | receipt-db.py write --id wave-1-receipt

    # Query: all FAIL receipts in last 10 sessions
    python .wabblespec/engine/shared/scripts/receipt-db.py query \\
        "SELECT receipt_id, session_id, timestamp FROM receipts WHERE status='FAIL' LIMIT 20"

    # Stats:
    python .wabblespec/engine/shared/scripts/receipt-db.py stats

    # Export to JSON:
    python .wabblespec/engine/shared/scripts/receipt-db.py export --id wave-1-receipt

Exit codes:
    0  success
    1  bad arguments or query error
    2  database not found / not writable
"""

import sys
import os
import json
import glob
import argparse
from datetime import datetime, timezone

try:
    import duckdb
except ImportError:
    print("ERROR: duckdb not installed. Run: pip install duckdb", file=sys.stderr)
    sys.exit(2)


DB_RELATIVE = ".wabblespec/state/receipts/receipts.duckdb"


def find_repo_root(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        if os.path.isdir(os.path.join(candidate, ".wabblespec")):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def get_db_path(repo_root):
    return os.path.join(repo_root, DB_RELATIVE)


def open_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            receipt_id   TEXT PRIMARY KEY,
            session_id   TEXT,
            module       TEXT,
            status       TEXT,
            timestamp    TEXT,
            wave         INTEGER,
            delta_class  TEXT,
            receipt_json TEXT
        )
    """)
    return con


def receipt_to_row(receipt_id, data):
    return {
        "receipt_id": receipt_id,
        "session_id": data.get("session_id") or data.get("task_id"),
        "module": data.get("module"),
        "status": data.get("status"),
        "timestamp": data.get("timestamp") or data.get("written_at"),
        "wave": (lambda w: int(w) if isinstance(w, (int, float)) or (isinstance(w, str) and w.isdigit()) else None)(data.get("wave")),
        "delta_class": data.get("delta_class"),
        "receipt_json": json.dumps(data),
    }


def cmd_init(args, repo_root):
    db_path = get_db_path(repo_root)
    con = open_db(db_path)
    count = con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
    con.close()
    print(f"Receipt DB ready: {db_path} ({count} rows)")


def cmd_import(args, repo_root):
    db_path = get_db_path(repo_root)
    con = open_db(db_path)
    receipts_dir = os.path.join(repo_root, ".wabblespec", "state", "receipts")
    pattern = os.path.join(receipts_dir, "*.json")
    files = glob.glob(pattern)

    imported = skipped = errors = 0
    for path in files:
        receipt_id = os.path.splitext(os.path.basename(path))[0]
        if receipt_id in ("README",):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            errors += 1
            continue

        row = receipt_to_row(receipt_id, data)
        try:
            con.execute(
                """
                INSERT OR REPLACE INTO receipts
                    (receipt_id, session_id, module, status, timestamp, wave, delta_class, receipt_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [row["receipt_id"], row["session_id"], row["module"], row["status"],
                 row["timestamp"], row["wave"], row["delta_class"], row["receipt_json"]],
            )
            imported += 1
        except Exception as e:
            print(f"  WARN: {receipt_id}: {e}", file=sys.stderr)
            errors += 1

    con.close()
    print(f"Imported {imported} receipts ({skipped} skipped, {errors} errors)")


def cmd_write(args, repo_root):
    raw = sys.stdin.read() if args.json_stdin else args.json_string
    if not raw:
        print("ERROR: No JSON provided. Use --json or pipe via stdin.", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    receipt_id = args.id or (
        f"{data.get('module', 'unknown')}-receipt-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    db_path = get_db_path(repo_root)
    con = open_db(db_path)
    row = receipt_to_row(receipt_id, data)
    con.execute(
        """
        INSERT OR REPLACE INTO receipts
            (receipt_id, session_id, module, status, timestamp, wave, delta_class, receipt_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [row["receipt_id"], row["session_id"], row["module"], row["status"],
         row["timestamp"], row["wave"], row["delta_class"], row["receipt_json"]],
    )
    con.close()
    print(f"Wrote receipt: {receipt_id}")


def cmd_query(args, repo_root):
    db_path = get_db_path(repo_root)
    if not os.path.isfile(db_path):
        print(f"ERROR: Receipt DB not found at {db_path}. Run 'init' first.", file=sys.stderr)
        sys.exit(2)
    con = duckdb.connect(db_path, read_only=True)
    try:
        result = con.execute(args.sql).fetchdf()
        print(result.to_string(index=False))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        con.close()
        sys.exit(1)
    con.close()


def cmd_stats(args, repo_root):
    db_path = get_db_path(repo_root)
    if not os.path.isfile(db_path):
        print(f"Receipt DB not found at {db_path}. Run 'init' then 'import'.")
        return
    con = duckdb.connect(db_path, read_only=True)
    total = con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
    by_status = con.execute(
        "SELECT status, COUNT(*) as n FROM receipts GROUP BY status ORDER BY n DESC"
    ).fetchall()
    by_module = con.execute(
        "SELECT module, COUNT(*) as n FROM receipts GROUP BY module ORDER BY n DESC LIMIT 10"
    ).fetchall()
    con.close()

    print(f"Receipt DB: {db_path}")
    print(f"Total receipts: {total}")
    print("\nBy status:")
    for row in by_status:
        print(f"  {row[0] or 'null':<12} {row[1]}")
    print("\nTop modules:")
    for row in by_module:
        print(f"  {row[0] or 'null':<30} {row[1]}")


def cmd_export(args, repo_root):
    db_path = get_db_path(repo_root)
    if not os.path.isfile(db_path):
        print(f"ERROR: DB not found.", file=sys.stderr)
        sys.exit(2)
    con = duckdb.connect(db_path, read_only=True)
    row = con.execute(
        "SELECT receipt_json FROM receipts WHERE receipt_id = ?", [args.id]
    ).fetchone()
    con.close()
    if not row:
        print(f"ERROR: receipt_id '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    print(row[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create or open the receipt DB.")
    sub.add_parser("import", help="Bulk-import existing JSON receipt files.")

    p_write = sub.add_parser("write", help="Write a JSON receipt to the DB.")
    p_write.add_argument("--id", metavar="RECEIPT_ID",
                         help="receipt_id key (defaults to module-receipt-<timestamp>).")
    p_write.add_argument("--json", metavar="JSON_STRING", dest="json_string",
                         help="JSON string to write.")
    p_write.add_argument("--stdin", action="store_true", dest="json_stdin",
                         help="Read JSON from stdin.")

    p_query = sub.add_parser("query", help="Run SQL against the receipts table.")
    p_query.add_argument("sql", metavar="SQL")

    sub.add_parser("stats", help="Print receipt counts and top modules.")

    p_export = sub.add_parser("export", help="Export a receipt JSON by ID.")
    p_export.add_argument("--id", required=True, metavar="RECEIPT_ID")

    args = parser.parse_args()

    repo_root = find_repo_root()
    if not repo_root:
        print("ERROR: Cannot find repo root.", file=sys.stderr)
        sys.exit(2)

    dispatch = {
        "init": cmd_init,
        "import": cmd_import,
        "write": cmd_write,
        "query": cmd_query,
        "stats": cmd_stats,
        "export": cmd_export,
    }
    dispatch[args.command](args, repo_root)


if __name__ == "__main__":
    main()
