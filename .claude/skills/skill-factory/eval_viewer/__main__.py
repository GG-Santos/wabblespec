#!/usr/bin/env python3
"""Serve static skill benchmark matrix outputs with `python -m eval_viewer`."""

from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from scripts.render_benchmark_matrix_html import render_report


class BenchmarkHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path in {"/", ""}:
            self.path = "/benchmark_report.html"
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        pass


def ensure_report(root: Path, refresh: bool = False) -> dict[str, Any]:
    return render_report(root, refresh=refresh)


def serve(root: Path, port: int) -> str:
    handler = partial(BenchmarkHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"eval_viewer: serving {root} at {url}")
    print("eval_viewer: press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("eval_viewer: stopped")
    finally:
        server.server_close()
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve skill benchmark matrix outputs.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--watch", action="store_true", help="Accepted for eval-viewer CLI compatibility.")
    parser.add_argument("--include", action="append", default=[], help="Accepted scan glob; static server serves the root.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild benchmark_report.json before serving.")
    parser.add_argument("--once", action="store_true", help="Render and exit without starting the server.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"--root does not exist or is not a directory: {root}")

    result = ensure_report(root, refresh=args.refresh)
    result["root"] = str(root)
    result["port"] = args.port
    result["watch"] = bool(args.watch)
    result["include"] = args.include

    if args.once:
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"eval_viewer: rendered {result['output']}")
        return 0

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    serve(root, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
