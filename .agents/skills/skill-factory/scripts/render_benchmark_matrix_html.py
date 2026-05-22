#!/usr/bin/env python3
"""Render a static HTML summary for a skill benchmark matrix report."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_json_report(root: Path) -> dict[str, Any]:
    try:
        from scripts.report_benchmark_matrix import write_report
    except ModuleNotFoundError:  # Allows `python scripts/render_benchmark_matrix_html.py`.
        from report_benchmark_matrix import write_report

    return write_report(root)


def format_score(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.3f}"
    return ""


def format_int(value: Any) -> str:
    if isinstance(value, int):
        return f"{value:,}"
    return escape(str(value))


def tag(value: Any) -> str:
    return f"<code>{escape(str(value))}</code>"


def table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    body = "\n".join(body_rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def metric_cards(totals: dict[str, Any], valid: bool) -> str:
    labels = [
        ("Tasks", totals.get("tasks")),
        ("Lanes", totals.get("agents")),
        ("Categories", totals.get("categories")),
        ("Category/niche pairs", totals.get("niches")),
        ("Output targets", totals.get("output_targets")),
        ("Valid", valid),
    ]
    cards = []
    for label, value in labels:
        cards.append(
            "<section class=\"metric\">"
            f"<span>{escape(label)}</span>"
            f"<strong>{escape(str(value))}</strong>"
            "</section>"
        )
    return "\n".join(cards)


def rows_for_leaderboard(report: dict[str, Any]) -> list[list[Any]]:
    return [
        [
            tag(item.get("agent")),
            format_int(item.get("tasks")),
            format_score(item.get("score_average")),
        ]
        for item in report.get("leaderboard", [])
    ]


def rows_for_agents(report: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for agent, summary in sorted(report.get("by_agent", {}).items()):
        score_means = summary.get("score_means", {})
        check_rates = summary.get("check_pass_rates", {})
        rows.append([
            tag(agent),
            format_int(summary.get("tasks")),
            format_score(summary.get("score_average")),
            format_score(score_means.get("structure_completeness")),
            format_score(check_rates.get("appears_in_eval_viewer")),
        ])
    return rows


def rows_for_output_targets(report: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for target, summary in sorted(report.get("by_output_target", {}).items()):
        score_means = summary.get("score_means", {})
        rows.append([
            tag(target),
            format_int(summary.get("tasks")),
            format_score(summary.get("score_average")),
            format_score(score_means.get("testability")),
            format_score(score_means.get("token_usage")),
        ])
    return rows


def rows_for_categories(report: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for category, summary in sorted(report.get("by_category", {}).items()):
        score_means = summary.get("score_means", {})
        rows.append([
            tag(category),
            format_int(summary.get("tasks")),
            format_score(summary.get("score_average")),
            format_score(score_means.get("domain_specificity")),
            format_score(score_means.get("safety_quality")),
        ])
    return rows


def qualitative_summary(report: dict[str, Any]) -> str:
    audit = report.get("qualitative_audit") or {}
    summary = audit.get("summary") or {}
    if not audit:
        return "<p>No qualitative audit loaded.</p>"
    rows = [
        ["Valid", escape(str(audit.get("valid")))],
        ["Errors", escape(str(summary.get("errors", 0)))],
        ["Warnings", escape(str(summary.get("warnings", 0)))],
        ["Stored findings", escape(str(len(audit.get("findings", []))))],
    ]
    return table(["Metric", "Value"], rows)


def exhaustive_summary(report: dict[str, Any]) -> str:
    review = report.get("exhaustive_review") or {}
    summary = review.get("summary") or {}
    if not review:
        return "<p>No exhaustive review loaded.</p>"
    rows = [
        ["Valid", escape(str(review.get("valid")))],
        ["Errors", escape(str(summary.get("errors", 0)))],
        ["Warnings", escape(str(summary.get("warnings", 0)))],
        ["JSON files parsed", escape(str(summary.get("json_files_parsed", 0)))],
        ["Python files parsed", escape(str(summary.get("python_files_parsed", 0)))],
        ["Generated scripts executed", escape(str(summary.get("generated_scripts_executed", 0)))],
        ["Generated hooks executed", escape(str(summary.get("generated_hooks_executed", 0)))],
    ]
    return table(["Metric", "Value"], rows)


def render_html(report: dict[str, Any]) -> str:
    totals = report.get("totals", {})
    valid = bool(report.get("valid"))
    root = report.get("root", "")
    error_count = len(report.get("errors", []))
    validity_class = "ok" if valid else "bad"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Benchmark Matrix Report</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #5b6871;
      --line: #d9e0e5;
      --panel: #f7f9fa;
      --accent: #146c94;
      --good: #1f7a4c;
      --bad: #b42318;
      --surface: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font: 15px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      margin-bottom: 24px;
      padding-bottom: 18px;
    }}
    h1 {{
      font-size: 30px;
      line-height: 1.15;
      margin: 0 0 8px;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 18px;
      margin: 30px 0 10px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); margin: 0; }}
    code {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 5px;
      white-space: nowrap;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 22px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
      min-height: 86px;
    }}
    .metric span {{
      color: var(--muted);
      display: block;
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      line-height: 1.1;
    }}
    .status {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 650;
      margin-top: 12px;
    }}
    .status.ok {{ color: var(--good); }}
    .status.bad {{ color: var(--bad); }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      min-width: 620px;
      background: var(--surface);
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 11px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: var(--panel);
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    footer {{
      color: var(--muted);
      border-top: 1px solid var(--line);
      margin-top: 34px;
      padding-top: 16px;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Benchmark Matrix Report</h1>
      <p>Root: {tag(root)}</p>
      <div class="status {validity_class}">Valid: {escape(str(valid))} | Errors: {error_count}</div>
    </header>

    <section class="metrics">
      {metric_cards(totals, valid)}
    </section>

    <h2>Leaderboard</h2>
    <div class="table-wrap">
      {table(["Lane", "Tasks", "Average score"], rows_for_leaderboard(report))}
    </div>

    <h2>Lanes</h2>
    <div class="table-wrap">
      {table(["Lane", "Tasks", "Avg", "Structure", "Viewer"], rows_for_agents(report))}
    </div>

    <h2>Output Targets</h2>
    <div class="table-wrap">
      {table(["Output target", "Tasks", "Avg", "Testability", "Token usage"], rows_for_output_targets(report))}
    </div>

    <h2>Categories</h2>
    <div class="table-wrap">
      {table(["Category", "Tasks", "Avg", "Domain", "Safety"], rows_for_categories(report))}
    </div>

    <h2>Qualitative Audit</h2>
    <div class="table-wrap">
      {qualitative_summary(report)}
    </div>

    <h2>Exhaustive Review</h2>
    <div class="table-wrap">
      {exhaustive_summary(report)}
    </div>

    <footer>
      Scores are deterministic structural heuristics from eval.json. Qualitative
      and exhaustive gates are machine-checkable review signals.
    </footer>
  </main>
</body>
</html>
"""


def render_report(root: Path, output: Path | None = None, refresh: bool = False) -> dict[str, Any]:
    report_path = root / "benchmark_report.json"
    rebuilt = refresh or not report_path.exists()
    report = build_json_report(root) if rebuilt else read_json(report_path)
    output_path = output or root / "benchmark_report.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(report), encoding="utf-8")
    return {
        "valid": True,
        "rebuilt_report": rebuilt,
        "source": str(report_path),
        "output": str(output_path),
        "bytes": output_path.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render benchmark_report.json as static HTML.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--refresh", action="store_true", help="Rebuild benchmark_report.json before rendering.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = render_report(args.root, args.output, refresh=args.refresh)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"render_benchmark_matrix_html: wrote {result['output']} ({result['bytes']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
