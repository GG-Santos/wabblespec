"""
version-bump.py — Deterministic semver bumper for .wabblespec/VERSION.

Reads VERSION, applies a bump, writes back. No LLM reasoning required.

Usage:
    python .wabblespec/engine/shared/scripts/version-bump.py --bump ADDITIVE
    python .wabblespec/engine/shared/scripts/version-bump.py --bump BREAKING
    python .wabblespec/engine/shared/scripts/version-bump.py --bump COSMETIC
    python .wabblespec/engine/shared/scripts/version-bump.py --show          # print current version only
    python .wabblespec/engine/shared/scripts/version-bump.py --set 1.2.3     # force a specific version

Delta-class to semver component mapping:
    BREAKING  -> major (x.0.0)
    ADDITIVE  -> minor (0.x.0)
    COSMETIC  -> patch (0.0.x)

During the 0.x.y pre-stabilization period (major == 0):
    BREAKING still increments minor (not major), to reserve major for post-stabilization.
    This matches the seed pipeline convention documented in version-policy.md.
    Pass --pre-stabilization (default when major == 0) or --no-pre-stabilization to override.

Exit codes:
    0  success
    1  bad arguments or bump type
    2  VERSION file missing or unparseable
"""

import sys
import os
import argparse
import re


VALID_BUMPS = {"BREAKING", "ADDITIVE", "COSMETIC"}


def find_version_file(start_dir=None):
    """Walk up from start_dir looking for .wabblespec/VERSION."""
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(8):  # max 8 levels up
        path = os.path.join(candidate, ".wabblespec", "VERSION")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def read_version(path):
    """Read and parse a semver string from path. Returns (major, minor, patch)."""
    try:
        raw = open(path, encoding="utf-8").read().strip()
    except OSError as e:
        print(f"ERROR: Cannot read VERSION file at {path}: {e}", file=sys.stderr)
        sys.exit(2)
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", raw)
    if not m:
        print(
            f"ERROR: VERSION file contains '{raw}' — expected x.y.z format.",
            file=sys.stderr,
        )
        sys.exit(2)
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), raw


def bump(major, minor, patch, delta_class, pre_stabilization):
    """Return (new_major, new_minor, new_patch) after applying delta_class."""
    if delta_class == "BREAKING":
        if pre_stabilization:
            # Reserve major for post-stabilization; BREAKING bumps minor during 0.x.y
            return major, minor + 1, 0
        return major + 1, 0, 0
    elif delta_class == "ADDITIVE":
        return major, minor + 1, 0
    else:  # COSMETIC
        return major, minor, patch + 1


def write_version(path, version_str):
    """Write version_str atomically to path."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(version_str + "\n")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(
        description="Bump .wabblespec/VERSION by delta class.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--bump",
        choices=["BREAKING", "ADDITIVE", "COSMETIC"],
        help="Delta class that drives the bump.",
    )
    group.add_argument("--show", action="store_true", help="Print current version and exit.")
    group.add_argument("--set", metavar="VERSION", help="Force VERSION to an exact string.")

    parser.add_argument(
        "--version-file",
        metavar="PATH",
        help="Explicit path to VERSION file. Defaults to auto-discovery.",
    )
    parser.add_argument(
        "--pre-stabilization",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Treat BREAKING as minor bump (default when major == 0). "
            "Use --no-pre-stabilization to force major bump even at 0.x.y."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute new version but do not write it.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of plain text.",
    )

    args = parser.parse_args()

    # Locate VERSION
    if args.version_file:
        vpath = args.version_file
        if not os.path.isfile(vpath):
            print(f"ERROR: VERSION file not found at {vpath}", file=sys.stderr)
            sys.exit(2)
    else:
        vpath = find_version_file()
        if vpath is None:
            print(
                "ERROR: Could not find .wabblespec/VERSION. Run from inside the repo.",
                file=sys.stderr,
            )
            sys.exit(2)

    major, minor, patch, raw = read_version(vpath)
    current = raw

    # --show
    if args.show:
        if args.json:
            import json
            print(json.dumps({"version": current, "path": vpath}))
        else:
            print(current)
        sys.exit(0)

    # --set
    if args.set:
        new_version = args.set.strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", new_version):
            print(f"ERROR: --set value '{new_version}' is not x.y.z format.", file=sys.stderr)
            sys.exit(1)
        if not args.dry_run:
            write_version(vpath, new_version)
        if args.json:
            import json
            print(json.dumps({"previous": current, "new": new_version, "dry_run": args.dry_run}))
        else:
            action = "(dry-run)" if args.dry_run else ""
            print(f"{current} -> {new_version} {action}".strip())
        sys.exit(0)

    # --bump
    pre_stab = args.pre_stabilization
    if pre_stab is None:
        pre_stab = major == 0  # default: pre-stabilization when major is 0

    new_major, new_minor, new_patch = bump(major, minor, patch, args.bump, pre_stab)
    new_version = f"{new_major}.{new_minor}.{new_patch}"

    if not args.dry_run:
        write_version(vpath, new_version)

    if args.json:
        import json
        print(
            json.dumps(
                {
                    "previous": current,
                    "new": new_version,
                    "delta_class": args.bump,
                    "pre_stabilization": pre_stab,
                    "dry_run": args.dry_run,
                    "path": vpath,
                }
            )
        )
    else:
        action = " (dry-run)" if args.dry_run else ""
        print(f"{current} -> {new_version}{action}")

    sys.exit(0)


if __name__ == "__main__":
    main()
