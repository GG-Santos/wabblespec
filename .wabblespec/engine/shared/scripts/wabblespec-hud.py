#!/usr/bin/env python3
"""
wabblespec-hud.py — Purple HUD renderer for WabbleSpec.
Outputs up to 3 ANSI-colored lines for the Claude Code statusLine.

Usage: python wabblespec-hud.py [--no-git] [--compact]
"""
import io
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows (avoids CP1252 encoding errors with Unicode symbols)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Color palette (purple-first) ──────────────────────────────────────────────
R   = '\x1b[0m'
DIM = '\x1b[2m'
B   = '\x1b[1m'
PUR = '\x1b[35m'         # primary purple
BPR = '\x1b[95m'         # bright purple — labels, active items
DPR = '\x1b[38;5;135m'  # deep purple — accents (256-color)
SPR = '\x1b[38;5;183m'  # soft lavender — wave symbols, secondary info
RED = '\x1b[31m'
YEL = '\x1b[33m'
GRN = '\x1b[32m'
CYN = '\x1b[36m'
WHT = '\x1b[37m'

SEP = f'{DIM} | {R}'

def _c(code: str, text: str) -> str:
    return f'{code}{text}{R}'

def bpur(t): return f'{BPR}{B}{t}{R}'   # bright purple bold
def pur(t):  return _c(PUR, t)
def spr(t):  return _c(SPR, t)
def dpr(t):  return _c(DPR, t)
def dim(t):  return _c(DIM, t)
def grn(t):  return _c(GRN, t)
def yel(t):  return _c(YEL, t)
def red(t):  return _c(RED, t)
def cyn(t):  return _c(CYN, t)

# ── Path resolution ───────────────────────────────────────────────────────────
# Script lives at: <repo>/.wabblespec/engine/shared/scripts/wabblespec-hud.py
_HERE = Path(__file__).resolve()
REPO  = _HERE.parent.parent.parent.parent.parent  # 5 levels up to repo root

STATE_JSON   = REPO / '.wabblespec' / 'state' / 'session' / 'state.json'
WAVE_PLAN    = REPO / '.wabblespec' / 'state' / 'plans' / 'current-wave-plan.md'
VERSION_FILE = REPO / '.wabblespec' / 'VERSION'
RECEIPTS_DIR = REPO / '.wabblespec' / 'state' / 'receipts'
L8_GATE      = REPO / '.wabblespec' / 'engine' / 'shared' / 'references' / 'l8-corpus-gate.md'

# ── Data readers ──────────────────────────────────────────────────────────────

def read_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding='utf-8').strip()
    except Exception:
        return '?'

def read_state() -> dict | None:
    try:
        return json.loads(STATE_JSON.read_text(encoding='utf-8'))
    except Exception:
        return None

def parse_wave_names(plan_path: Path) -> list[str]:
    try:
        text = plan_path.read_text(encoding='utf-8')
        return re.findall(r'^### Wave \d+: (.+)$', text, re.MULTILINE)
    except Exception:
        return []

def count_session_verifier_receipts(session_id: str) -> int:
    if not session_id or not RECEIPTS_DIR.exists():
        return 0
    count = 0
    sid8 = session_id[:8]
    for f in RECEIPTS_DIR.glob('*.json'):
        if sid8 not in f.name and session_id not in f.name:
            continue
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
            rtype = d.get('receipt_type', '')
            if 'verifier' in rtype:
                count += 1
        except Exception:
            pass
    return count

def read_l8_gate() -> str:
    try:
        text = L8_GATE.read_text(encoding='utf-8')
        for line in text.split('\n')[:25]:
            if re.search(r'\bmet\b', line, re.I) and not re.search(r'not.?met', line, re.I):
                return 'MET'
        return '?'
    except Exception:
        return '?'

def git_info(cwd: str) -> tuple[str | None, bool]:
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        return branch, bool(status)
    except Exception:
        return None, False

def short_cwd(cwd: str) -> str:
    try:
        home = Path.home()
        rel = Path(cwd).relative_to(home)
        return '~/' + str(rel).replace('\\', '/')
    except Exception:
        return Path(cwd).name

# ── Element renderers ─────────────────────────────────────────────────────────

MODULE_COLORS = {
    'executor':  BPR,
    'verifier':  CYN,
    'guard':     YEL,
    'archive':   GRN,
    'recipe':    SPR,
    'specify':   SPR,
    'decompose': SPR,
    'rollback':  RED,
    'dream':     DPR,
}

def render_module(module: str) -> str:
    color = MODULE_COLORS.get(module, PUR)
    return f'{color}{module}{R}'

def render_receipt_chain(required: list[str]) -> str:
    if not required or not RECEIPTS_DIR.exists():
        return dim('—')
    found = 0
    all_names = {f.stem for f in RECEIPTS_DIR.glob('*.json')}
    for rtype in required:
        canonical = rtype.replace('-receipt', '').replace('_receipt', '')
        if any(canonical in n for n in all_names):
            found += 1
    ratio = f'{found}/{len(required)}'
    if found == len(required):
        return f'R:{grn(ratio)}'
    if found == 0:
        return f'R:{dim(ratio)}'
    return f'R:{yel(ratio)}'

def render_wave_progress(waves: list[str], completed: int) -> str:
    if not waves:
        return ''
    total = len(waves)
    return spr(f'w:{completed}/{total}')

def render_wave_strip(waves: list[str], completed: int) -> str:
    if not waves:
        return ''
    parts = []
    for i, name in enumerate(waves):
        # Take first significant word, strip trailing punctuation
        label = re.split(r'[,;:\s]', name.strip())[0].rstrip('.,;:')[:10]
        if i < completed:
            parts.append(f'{GRN}✓{R}{dim(label)}')
        elif i == completed:
            parts.append(f'{BPR}●{R}{pur(label)}')
        else:
            parts.append(f'{DIM}○{dim(label)}{R}')
    return '  '.join(parts)

# ── Main render ───────────────────────────────────────────────────────────────

def render(no_git: bool = False, compact: bool = False) -> str:
    cwd     = os.getcwd()
    version = read_version()
    state   = read_state()
    l8      = read_l8_gate()

    branch, dirty = (None, False) if no_git else git_info(cwd)

    # ── Line 1: context bar (hostname | cwd | branch) ─────────────────────────
    line1_parts: list[str] = []
    try:
        host = socket.gethostname().split('.')[0]
        line1_parts.append(dim(host))
    except Exception:
        pass
    line1_parts.append(dim(short_cwd(cwd)))
    if branch:
        b_str = spr(branch)
        if dirty:
            b_str += f' {yel("*")}'
        line1_parts.append(b_str)

    line1 = SEP.join(line1_parts)

    # ── Line 2: main HUD ──────────────────────────────────────────────────────
    label = f'{bpur("[WABBLE]")} {dim("v" + version)}'
    main_parts: list[str] = [label]

    if state:
        session_id = state.get('session_id', '')
        task_short = session_id[:22] + ('…' if len(session_id) > 22 else '')
        main_parts.append(f'{pur("task:" + (task_short or "—"))}')

        module = state.get('active_module') or '?'
        main_parts.append(render_module(module))

        required = state.get('required_receipts', [])
        main_parts.append(render_receipt_chain(required))

        waves     = parse_wave_names(WAVE_PLAN)
        completed = count_session_verifier_receipts(session_id)
        if waves:
            main_parts.append(render_wave_progress(waves, completed))
    else:
        main_parts.append(dim('idle'))

    l8_label = f'L8:{grn("MET") if l8 == "MET" else dim("?")}'
    main_parts.append(l8_label)

    line2 = SEP.join(main_parts)

    # ── Line 3: wave strip ────────────────────────────────────────────────────
    output_lines = [line1, line2]

    if not compact and state:
        waves     = parse_wave_names(WAVE_PLAN)
        if waves:
            session_id = state.get('session_id', '')
            completed  = count_session_verifier_receipts(session_id)
            strip = render_wave_strip(waves, completed)
            if strip:
                output_lines.append(strip)

    return '\n'.join(output_lines)

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args    = sys.argv[1:]
    no_git  = '--no-git' in args
    compact = '--compact' in args
    try:
        print(render(no_git=no_git, compact=compact))
    except Exception:
        # Silent fail — always output something
        print(bpur('[WABBLE]'))
