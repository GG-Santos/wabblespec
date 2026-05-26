"""
bm25.py — Shared BM25 search engine over WabbleSpec text corpora.
Consumers: nexus, explore

Usage:
    python bm25.py --corpus <path> --query <text> [options]

Options:
    --corpus    Directory of .md or .json files to index, OR a pre-built index JSON
    --query     Search query string
    --top-k     Return top-k results (default: 5)
    --field     JSON field to extract text from when corpus contains JSON files (default: content)
    --save-index  Path to save built index for reuse
    --load-index  Path to load pre-built index (skips corpus scan)
    --output    Path to write results JSON (default: stdout)
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_-]+", text.lower())


def extract_text(path: Path, field: str) -> str:
    if path.suffix == ".json":
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return str(obj.get(field, ""))
            return ""
        except Exception:
            return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def build_index(corpus_dir: str, field: str) -> dict:
    base = Path(corpus_dir)
    if not base.is_dir():
        print(f"ERROR: corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)

    docs: list[dict] = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json", ".txt"):
            text = extract_text(p, field)
            tokens = tokenize(text)
            docs.append({"path": str(p), "tokens": tokens, "length": len(tokens)})

    avg_dl = sum(d["length"] for d in docs) / max(len(docs), 1)

    df: dict[str, int] = {}
    for doc in docs:
        for term in set(doc["tokens"]):
            df[term] = df.get(term, 0) + 1

    return {"docs": docs, "df": df, "avg_dl": avg_dl, "N": len(docs)}


def bm25_score(query_terms: list[str], doc: dict, df: dict, N: int, avg_dl: float,
               k1: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    tf_map: dict[str, int] = {}
    for t in doc["tokens"]:
        tf_map[t] = tf_map.get(t, 0) + 1

    dl = doc["length"]
    for term in query_terms:
        tf = tf_map.get(term, 0)
        if tf == 0:
            continue
        n_t = df.get(term, 0)
        idf = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1.0)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
        score += idf * tf_norm
    return score


def search(index: dict, query: str, top_k: int) -> list[dict]:
    query_terms = tokenize(query)
    docs = index["docs"]
    df = index["df"]
    N = index["N"]
    avg_dl = index["avg_dl"]

    scored = []
    for doc in docs:
        s = bm25_score(query_terms, doc, df, N, avg_dl)
        if s > 0.0:
            scored.append({"path": doc["path"], "score": round(s, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="BM25 search over WabbleSpec corpus")
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--field", default="content")
    parser.add_argument("--save-index", default=None)
    parser.add_argument("--load-index", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.load_index:
        idx_path = Path(args.load_index)
        if not idx_path.exists():
            print(f"ERROR: index file not found: {args.load_index}", file=sys.stderr)
            sys.exit(1)
        index = json.loads(idx_path.read_text(encoding="utf-8"))
    elif args.corpus:
        index = build_index(args.corpus, args.field)
        if args.save_index:
            Path(args.save_index).write_text(json.dumps(index, indent=2), encoding="utf-8")
            print(f"Index saved: {args.save_index} ({index['N']} docs)", file=sys.stderr)
    else:
        print("ERROR: provide --corpus or --load-index", file=sys.stderr)
        sys.exit(1)

    results = search(index, args.query, args.top_k)
    output = {
        "query": args.query,
        "top_k": args.top_k,
        "result_count": len(results),
        "results": results,
    }

    out_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"Results written: {args.output} ({len(results)} hits)")
    else:
        print(out_json)


if __name__ == "__main__":
    main()
