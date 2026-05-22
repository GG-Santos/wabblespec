#!/usr/bin/env python3
"""Regression check: compare a new grading.json against a baseline.

Surfaces score deltas per axis. Exits non-zero when any axis regresses
by more than the threshold (default 0.2 points on the 1–5 scale, or
when a previously-passing axis now fails).

Usage:
    python -m scripts.regression_check \
        --baseline path/to/baseline-grading.json \
        --current path/to/grading.json \
        [--threshold 0.2] \
        [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def _axis_score(grading: dict[str, Any], axis: str) -> float | None:
    """Pull a numeric score for a known axis, or None if absent."""
    if axis == "overall_output_quality":
        return grading.get("v4_output_quality", {}).get("overall_output_quality_score")
    if axis == "downstream_output":
        return grading.get("invocation_simulation", {}).get("downstream_output_score")
    if axis == "artifact_pass_rate":
        s = grading.get("summary", {})
        total = s.get("total") or 0
        if not total:
            return None
        return float(s.get("passed", 0)) / total
    if axis == "runtime_coupling_errors":
        # Lower is better — return negative so larger = better, matching other axes
        findings = grading.get("runtime_coupling", {}).get("findings", [])
        return -sum(1 for f in findings if f.get("severity") == "error")
    return None


def _axis_passed(grading: dict[str, Any], axis: str) -> bool | None:
    if axis == "overall_output_quality":
        return grading.get("v4_output_quality", {}).get("output_quality_passed")
    if axis == "downstream_output":
        return grading.get("invocation_simulation", {}).get("downstream_output_passed")
    if axis == "artifact_pass_rate":
        s = grading.get("summary", {})
        if not s.get("total"):
            return None
        return s.get("failed", 0) == 0
    if axis == "runtime_coupling_errors":
        return grading.get("runtime_coupling", {}).get("runtime_coupling_passed")
    return None


AXES = (
    "overall_output_quality",
    "downstream_output",
    "artifact_pass_rate",
    "runtime_coupling_errors",
)


def compare(baseline: dict[str, Any], current: dict[str, Any], threshold: float) -> dict[str, Any]:
    """Compute axis-by-axis deltas. Returns a structured report."""
    report: dict[str, Any] = {
        "baseline_schema_version": baseline.get("schema_version"),
        "current_schema_version": current.get("schema_version"),
        "threshold": threshold,
        "axes": {},
        "regressions": [],
        "improvements": [],
        "regressed": False,
    }

    for axis in AXES:
        b = _axis_score(baseline, axis)
        c = _axis_score(current, axis)
        b_pass = _axis_passed(baseline, axis)
        c_pass = _axis_passed(current, axis)

        entry: dict[str, Any] = {
            "baseline": b,
            "current": c,
            "baseline_passed": b_pass,
            "current_passed": c_pass,
            "delta": None,
            "regressed": False,
        }

        if b is not None and c is not None:
            delta = round(c - b, 4)
            entry["delta"] = delta

            # Regression triggers:
            # 1. Score dropped by more than threshold
            # 2. Was passing, now failing
            if delta < -threshold:
                entry["regressed"] = True
                report["regressions"].append({
                    "axis": axis,
                    "reason": f"score dropped {abs(delta):.2f} (> {threshold})",
                    "baseline": b,
                    "current": c,
                })
            elif b_pass is True and c_pass is False:
                entry["regressed"] = True
                report["regressions"].append({
                    "axis": axis,
                    "reason": "was passing, now failing",
                    "baseline": b,
                    "current": c,
                })
            elif delta > threshold:
                report["improvements"].append({
                    "axis": axis,
                    "delta": delta,
                    "baseline": b,
                    "current": c,
                })

        report["axes"][axis] = entry

    report["regressed"] = bool(report["regressions"])
    return report


def render_text(report: dict[str, Any]) -> str:
    lines = ["Regression check"]
    lines.append("=" * 50)
    lines.append(f"Threshold: +/-{report['threshold']}")
    lines.append("")
    lines.append(f"{'Axis':<32} {'Baseline':>10} {'Current':>10} {'Delta':>8}  Status")
    lines.append("-" * 76)
    for axis, e in report["axes"].items():
        b = "—" if e["baseline"] is None else f"{e['baseline']:.3f}"
        c = "—" if e["current"] is None else f"{e['current']:.3f}"
        d = "—" if e["delta"] is None else f"{e['delta']:+.3f}"
        status = "REGRESSED" if e["regressed"] else ("PASS" if e.get("current_passed") else "fail" if e.get("current_passed") is False else "")
        lines.append(f"{axis:<32} {b:>10} {c:>10} {d:>8}  {status}")
    lines.append("")
    if report["regressions"]:
        lines.append(f"REGRESSIONS: {len(report['regressions'])}")
        for r in report["regressions"]:
            lines.append(f"  - {r['axis']}: {r['reason']} ({r['baseline']} → {r['current']})")
    else:
        lines.append("No regressions.")
    if report["improvements"]:
        lines.append(f"Improvements: {len(report['improvements'])}")
        for i in report["improvements"]:
            lines.append(f"  + {i['axis']}: +{i['delta']:.3f}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Regression check on grading.json")
    p.add_argument("--baseline", type=Path, required=True, help="Baseline grading.json")
    p.add_argument("--current", type=Path, required=True, help="Current grading.json")
    p.add_argument("--threshold", type=float, default=0.2,
                   help="Score-drop threshold to flag as regression (default 0.2)")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = p.parse_args()

    baseline = _read(args.baseline)
    current = _read(args.current)
    report = compare(baseline, current, args.threshold)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))

    return 1 if report["regressed"] else 0


if __name__ == "__main__":
    sys.exit(main())
