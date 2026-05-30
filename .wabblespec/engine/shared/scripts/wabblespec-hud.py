#!/usr/bin/env python3
"""
wabblespec-hud.py — Purple HUD for WabbleSpec.
Outputs up to 3 ANSI-colored lines for the Claude Code statusLine.

Lines:
  1  host | cwd | branch -> remote  dirty*
  2  [WABBLE v0.49]  5h:[bar]%  wk:[bar]%  module  skill
  3  waves:[bar] N/M  R:[bar] N/M  L8:MET

Usage: python wabblespec-hud.py [--no-git] [--compact] [--no-usage]
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import ssl
import sys
import time
import urllib.request
from pathlib import Path

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Color palette ─────────────────────────────────────────────────────────────
R   = '\x1b[0m'
DIM = '\x1b[2m'
BLD = '\x1b[1m'
PUR = '\x1b[35m'         # primary purple
BPR = '\x1b[95m'         # bright purple — labels, active
DPR = '\x1b[38;5;135m'  # deep purple — accent
SPR = '\x1b[38;5;183m'  # soft lavender — secondary
RED = '\x1b[31m'
YEL = '\x1b[33m'
GRN = '\x1b[32m'
CYN = '\x1b[36m'

SEP = f'{DIM} | {R}'

def _c(code: str, t: str) -> str: return f'{code}{t}{R}'
def bpur(t): return f'{BPR}{BLD}{t}{R}'
def pur(t):  return _c(PUR, t)
def spr(t):  return _c(SPR, t)
def dim(t):  return _c(DIM, t)
def grn(t):  return _c(GRN, t)
def yel(t):  return _c(YEL, t)
def red(t):  return _c(RED, t)

# ── Progress bar ──────────────────────────────────────────────────────────────

def _pct_color(pct: float) -> str:
    if pct >= 90: return RED
    if pct >= 70: return YEL
    return GRN

def usage_bar(pct: float, width: int = 8, label: str = '') -> str:
    """OMC-style bar: label:[████░░░░]45%"""
    safe = max(0.0, min(100.0, pct))
    filled = round(safe / 100 * width)
    empty  = width - filled
    color  = _pct_color(safe)
    bar    = f'{color}{"█" * filled}{DIM}{"░" * empty}{R}'
    pct_str = f'{color}{round(safe)}%{R}'
    prefix = f'{dim(label + ":")}' if label else ''
    return f'{prefix}[{bar}]{pct_str}'

def wave_bar(done: int, total: int, width: int = 10) -> str:
    """Purple bar for wave/task progress."""
    if total == 0:
        return f'[{dim("░" * width)}]{dim("?/0")}'
    safe_done = max(0, min(done, total))
    filled = round(safe_done / total * width)
    empty  = width - filled
    bar    = f'{BPR}{"█" * filled}{DIM}{"░" * empty}{R}'
    ratio  = f'{spr(str(safe_done))}{dim("/")}{dim(str(total))}'
    return f'[{bar}]{ratio}'

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).resolve()
REPO         = _HERE.parent.parent.parent.parent.parent   # .wabblespec/engine/shared/scripts/ -> 5 up
STATE_JSON   = REPO / '.wabblespec' / 'state' / 'session' / 'state.json'
WAVE_PLAN    = REPO / '.wabblespec' / 'state' / 'plans' / 'current-wave-plan.md'
VERSION_FILE = REPO / '.wabblespec' / 'VERSION'
RECEIPTS_DIR = REPO / '.wabblespec' / 'state' / 'receipts'
L8_GATE      = REPO / '.wabblespec' / 'engine' / 'shared' / 'references' / 'l8-corpus-gate.md'
CLAUDE_DIR   = Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))
CREDS_FILE   = CLAUDE_DIR / '.credentials.json'
USAGE_CACHE  = CLAUDE_DIR / '.wabble-usage-cache.json'
# Also check OMC's cache (user may have OMC installed)
OMC_CACHE    = CLAUDE_DIR / 'plugins' / 'oh-my-claudecode' / '.usage-cache-anthropic.json'

USAGE_CACHE_TTL_S = 300   # 5 minutes
API_TIMEOUT_S     = 4

# ── Data: WabbleSpec ─────────────────────────────────────────────────────────

def read_version() -> str:
    try: return VERSION_FILE.read_text('utf-8').strip()
    except: return '?'

def read_state() -> dict | None:
    try: return json.loads(STATE_JSON.read_text('utf-8'))
    except: return None

def parse_wave_names() -> list[str]:
    try:
        text = WAVE_PLAN.read_text('utf-8')
        return re.findall(r'^### Wave \d+: (.+)$', text, re.MULTILINE)
    except: return []

def count_verifier_receipts(session_id: str) -> int:
    if not session_id or not RECEIPTS_DIR.exists():
        return 0
    sid = session_id[:8]
    count = 0
    for f in RECEIPTS_DIR.glob('*.json'):
        if sid not in f.name and session_id not in f.name:
            continue
        try:
            d = json.loads(f.read_text('utf-8'))
            if 'verifier' in d.get('receipt_type', ''):
                count += 1
        except: pass
    return count

def count_receipts_found(required: list[str]) -> int:
    if not required or not RECEIPTS_DIR.exists():
        return 0
    all_stems = {f.stem for f in RECEIPTS_DIR.glob('*.json')}
    found = 0
    for rtype in required:
        canonical = rtype.replace('-receipt', '').replace('_receipt', '')
        if any(canonical in s for s in all_stems):
            found += 1
    return found

def read_l8_gate() -> bool:
    try:
        text = L8_GATE.read_text('utf-8')
        for line in text.split('\n')[:25]:
            if re.search(r'\bmet\b', line, re.I) and not re.search(r'not.?met', line, re.I):
                return True
        return False
    except: return False

# ── Data: Git ─────────────────────────────────────────────────────────────────

def _parse_remote_slug(url: str) -> str | None:
    """Extract owner/repo from https or ssh remote URL."""
    url = url.strip().removesuffix('.git')
    # SSH: git@github.com:owner/repo
    m = re.search(r'[:/]([^/]+/[^/]+)$', url)
    return m.group(1) if m else None

def git_info(cwd: str) -> dict:
    """Returns dict with branch, remote (owner/repo slug), dirty."""
    result = {'branch': None, 'remote': None, 'dirty': False}
    try:
        result['branch'] = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()

        dirty_out = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        result['dirty'] = bool(dirty_out)

        # Get the remote name from the upstream tracking ref, fall back to first remote
        try:
            tracking = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
            ).decode().strip()
            remote_name = tracking.split('/')[0]  # "origin/main" -> "origin"
        except subprocess.CalledProcessError:
            try:
                remote_name = subprocess.check_output(
                    ['git', 'remote'],
                    cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
                ).decode().strip().split('\n')[0]
            except Exception:
                remote_name = ''

        # Resolve remote name to URL and extract owner/repo slug
        if remote_name:
            try:
                url = subprocess.check_output(
                    ['git', 'remote', 'get-url', remote_name],
                    cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
                ).decode().strip()
                result['remote'] = _parse_remote_slug(url)
            except Exception:
                pass
    except Exception:
        pass
    return result

def short_cwd(cwd: str) -> str:
    try:
        rel = Path(cwd).relative_to(Path.home())
        return '~/' + str(rel).replace('\\', '/')
    except:
        return Path(cwd).name

# ── Data: Anthropic usage API ─────────────────────────────────────────────────

def _read_creds() -> dict | None:
    try:
        raw = json.loads(CREDS_FILE.read_text('utf-8'))
        return raw.get('claudeAiOauth', raw)
    except: return None

def _read_usage_cache() -> dict | None:
    """Try our cache first, then OMC's cache."""
    for path in (USAGE_CACHE, OMC_CACHE):
        try:
            d = json.loads(path.read_text('utf-8'))
            age = time.time() - d.get('timestamp', 0) / 1000
            if age < USAGE_CACHE_TTL_S and d.get('data'):
                return d['data']
        except: pass
    return None

def _write_usage_cache(data: dict | None) -> None:
    try:
        payload = {'timestamp': int(time.time() * 1000), 'data': data}
        USAGE_CACHE.write_text(json.dumps(payload), 'utf-8')
    except: pass

def _fetch_usage(token: str) -> dict | None:
    """Call Anthropic OAuth usage API. Returns raw response dict or None."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        'https://api.anthropic.com/api/oauth/usage',
        headers={
            'Authorization': f'Bearer {token}',
            'anthropic-beta': 'oauth-2025-04-20',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_S, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except: return None

def _clamp(v) -> int:
    if v is None: return 0
    try: return max(0, min(100, round(float(v))))
    except: return 0

def _parse_usage(raw: dict) -> dict:
    """Parse API response → {fiveHour, weekly, fiveHourResets, weeklyResets}."""
    result = {}
    fh = raw.get('five_hour', {})
    wk = raw.get('seven_day', {})
    result['fiveHour']       = _clamp(fh.get('utilization'))
    result['fiveHourResets'] = fh.get('resets_at')
    if 'utilization' in wk:
        result['weekly']       = _clamp(wk.get('utilization'))
        result['weeklyResets'] = wk.get('resets_at')
    return result

def _format_reset(iso_str: str | None) -> str | None:
    if not iso_str: return None
    try:
        import datetime
        dt = datetime.datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = dt - now
        if diff.total_seconds() <= 0: return None
        total_m = int(diff.total_seconds() / 60)
        h, m = divmod(total_m, 60)
        d, h = divmod(h, 24)
        if d > 0: return f'{d}d{h}h'
        return f'{h}h{m}m'
    except: return None

def get_usage(no_usage: bool = False) -> dict:
    """Return usage dict with fiveHour/weekly keys (int 0-100) or empty."""
    if no_usage:
        return {}
    cached = _read_usage_cache()
    if cached:
        return _parse_usage(cached) if 'five_hour' in cached else cached

    creds = _read_creds()
    if not creds:
        return {}
    token = creds.get('accessToken', '')
    if not token:
        return {}

    raw = _fetch_usage(token)
    if raw:
        _write_usage_cache(raw)
        return _parse_usage(raw)

    # Try token refresh if expired
    refresh = creds.get('refreshToken', '')
    if refresh:
        new_token = _refresh_token(refresh)
        if new_token:
            raw = _fetch_usage(new_token)
            if raw:
                _write_usage_cache(raw)
                return _parse_usage(raw)

    _write_usage_cache(None)
    return {}

def _refresh_token(refresh_token: str) -> str | None:
    """Attempt OAuth token refresh. Returns new access token or None."""
    ctx = ssl.create_default_context()
    client_id = os.environ.get('CLAUDE_CODE_OAUTH_CLIENT_ID', '9d1c250a-e61b-44d9-88ed-5944d1962f5e')
    body = f'grant_type=refresh_token&refresh_token={urllib.request.quote(refresh_token)}&client_id={client_id}'
    req = urllib.request.Request(
        'https://platform.claude.com/v1/oauth/token',
        data=body.encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_S, context=ctx) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            return d.get('access_token')
    except: return None

# ── Module colors ─────────────────────────────────────────────────────────────

MODULE_COLOR = {
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
    color = MODULE_COLOR.get(module.lower(), PUR)
    return f'{color}{module}{R}'

# ── Render ────────────────────────────────────────────────────────────────────

def render(no_git: bool, no_usage: bool, compact: bool) -> str:
    cwd     = os.getcwd()
    version = read_version()
    state   = read_state()
    l8_met  = read_l8_gate()
    usage   = get_usage(no_usage=no_usage)
    git     = {} if no_git else git_info(cwd)

    # ── Line 1: brand + skill + git + usage ──────────────────────────────────
    branch = git.get('branch')
    remote = git.get('remote')
    dirty  = git.get('dirty', False)

    parts1: list[str] = [bpur('[WABBLE]')]

    if state:
        module = state.get('active_module') or '?'
        parts1.append(render_module(module.upper()))
    else:
        parts1.append(dim('IDLE'))

    if branch:
        git_str = spr(branch)
        if remote:
            git_str += dim(' → ') + dim(remote)
        if dirty:
            git_str += f' {yel("*")}'
        parts1.append(git_str)

    if usage:
        fh = usage.get('fiveHour')
        wk = usage.get('weekly')
        if fh is not None:
            bar_str = usage_bar(fh, width=6, label='5h')
            if fh >= 70:
                reset = _format_reset(usage.get('fiveHourResets'))
                if reset:
                    bar_str += dim(f' {reset}')
            parts1.append(bar_str)
        if wk is not None:
            bar_str = usage_bar(wk, width=6, label='wk')
            if wk >= 70:
                reset = _format_reset(usage.get('weeklyResets'))
                if reset:
                    bar_str += dim(f' {reset}')
            parts1.append(bar_str)

    line1 = SEP.join(parts1)

    # ── Line 2: task progress ─────────────────────────────────────────────────
    parts2: list[str] = []

    waves = parse_wave_names()
    if waves:
        session_id = (state or {}).get('session_id', '')
        completed  = count_verifier_receipts(session_id)
        color = GRN if completed == len(waves) else SPR
        parts2.append(f'{dim("waves:")}{_c(color, f"{completed}/{len(waves)}")}')

    if state:
        required = state.get('required_receipts', [])
        if required:
            found = count_receipts_found(required)
            color = GRN if found == len(required) else YEL if found > 0 else DIM
            parts2.append(f'{dim("receipts:")}{_c(color, f"{found}/{len(required)}")}')

    parts2.append(f'{dim("gate:")}{grn("MET") if l8_met else dim("?")}')

    line2 = SEP.join(parts2)

    return '\n'.join([line1, line2])

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args     = set(sys.argv[1:])
    no_git   = '--no-git'   in args
    no_usage = '--no-usage' in args
    compact  = '--compact'  in args
    try:
        print(render(no_git=no_git, no_usage=no_usage, compact=compact))
    except Exception:
        print(bpur('[WABBLE]'))
