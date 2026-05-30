"""
crdt_merge_test.py — Unit tests for crdt_merge.py

Tests:
  1. LWW determinism (same result regardless of argument order)
  2. LWW higher-timestamp wins
  3. LWW tie-break is deterministic
  4. OR-Set union preserves all unique items, no duplicates
  5. top-level merge handles mixed value types
  6. No KeyError or exception on overlapping keys

Run: python crdt_merge_test.py
Exit 0 on all pass, 1 on any failure.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crdt_merge import lww_merge, or_set_union, merge


def test(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
        sys.exit(1)


def main():
    print("crdt_merge tests")

    # --- LWW tests ---
    a = {"x": {"val": 1, "ts": 100.0}, "y": {"val": "hello", "ts": 50.0}}
    b = {"x": {"val": 2, "ts": 200.0}, "z": {"val": True, "ts": 10.0}}

    merged_ab = lww_merge(a, b)
    merged_ba = lww_merge(b, a)

    test("LWW: higher ts wins (x)", merged_ab["x"]["val"] == 2)
    test("LWW: key only in a survives (y)", merged_ab["y"]["val"] == "hello")
    test("LWW: key only in b survives (z)", merged_ab["z"]["val"] is True)

    # Determinism: merge(a,b) == merge(b,a) for non-tied keys
    test("LWW: determinism for higher-ts keys",
         merged_ab["x"]["val"] == merged_ba["x"]["val"])
    test("LWW: both have all keys", set(merged_ab) == {"x", "y", "z"})

    # Tie-break test
    tie_a = {"k": {"val": "alpha", "ts": 100.0}}
    tie_b = {"k": {"val": "beta", "ts": 100.0}}
    tie_ab = lww_merge(tie_a, tie_b)
    tie_ba = lww_merge(tie_b, tie_a)
    test("LWW: tie-break is deterministic", tie_ab["k"]["val"] == tie_ba["k"]["val"])

    # --- OR-Set tests ---
    list_a = [1, 2, 3]
    list_b = [3, 4, 5]
    union = or_set_union(list_a, list_b)
    test("OR-Set: all unique items present", set(union) == {1, 2, 3, 4, 5})
    test("OR-Set: no duplicates", len(union) == 5)
    test("OR-Set: a-items appear first", union[0] == 1)

    # --- top-level merge ---
    wa = {
        "config": {"val": {"debug": True}, "ts": 100.0},
        "tags": ["alpha", "beta"],
        "count": 3,
    }
    wb = {
        "config": {"val": {"debug": False}, "ts": 200.0},
        "tags": ["beta", "gamma"],
        "extra": "new",
    }
    result = merge(wa, wb)
    test("merge: LWW config resolved by ts", result["config"]["val"]["debug"] is False)
    test("merge: OR-Set tags union", set(result["tags"]) == {"alpha", "beta", "gamma"})
    test("merge: key only in wb present", result.get("extra") == "new")
    test("merge: key only in wa present", result.get("count") == 3)

    # Determinism with swapped args (for keys with ts)
    result2 = merge(wb, wa)
    test("merge: deterministic config resolution across swap",
         result["config"]["val"]["debug"] == result2["config"]["val"]["debug"])

    print("All tests PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
