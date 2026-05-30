#!/usr/bin/env python3
"""
wabblespec-hud.py — Purple HUD for WabbleSpec.
Outputs 2 ANSI-colored lines for the Claude Code statusLine.

  1  [WABBLE] | SKILL | repo (branch)  | 5H:% (reset) | 1W:% (reset)
  2  waves:N/M | receipts:N/M | gate:MET                   ctx:87% context

Usage: python wabblespec-hud.py [--no-git] [--no-usage] [--no-ctx]
"""
from __future__ import annotations

import io, json, os, re, subprocess, ssl, sys, time, urllib.request
from pathlib import Path

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Color palette ─────────────────────────────────────────────────────────────
R   = '\x1b[0m'
DIM = '\x1b[2m'
BLD = '\x1b[1m'
PUR = '\x1b[35m'
BPR = '\x1b[95m'
DPR = '\x1b[38;5;135m'
SPR = '\x1b[38;5;183m'   # lavender — primary brand color
RED = '\x1b[31m'
YEL = '\x1b[33m'
GRN = '\x1b[32m'
CYN = '\x1b[36m'

SEP = f'{DIM} | {R}'

def _c(code, t): return f'{code}{t}{R}'
def spr(t):  return _c(SPR, t)
def dim(t):  return _c(DIM, t)
def grn(t):  return _c(GRN, t)
def yel(t):  return _c(YEL, t)

def _pct_color(pct):
    if pct >= 90: return RED
    if pct >= 70: return YEL
    return GRN


# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).resolve()
REPO         = _HERE.parent.parent.parent.parent.parent
STATE_JSON   = REPO / '.wabblespec' / 'state' / 'session' / 'state.json'
WAVE_PLAN    = REPO / '.wabblespec' / 'state' / 'plans' / 'current-wave-plan.md'
RECEIPTS_DIR = REPO / '.wabblespec' / 'state' / 'receipts'
L8_GATE      = REPO / '.wabblespec' / 'engine' / 'shared' / 'references' / 'l8-corpus-gate.md'
CLAUDE_DIR   = Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))
CREDS_FILE   = CLAUDE_DIR / '.credentials.json'
USAGE_CACHE  = CLAUDE_DIR / '.wabble-usage-cache.json'
OMC_CACHE    = CLAUDE_DIR / 'plugins' / 'oh-my-claudecode' / '.usage-cache-anthropic.json'

USAGE_TTL_S    = 300
API_TIMEOUT_S  = 4

# ── WabbleSpec state ──────────────────────────────────────────────────────────

def read_state():
    try: return json.loads(STATE_JSON.read_text('utf-8'))
    except: return None

def parse_wave_names():
    try:
        return re.findall(r'^### Wave \d+: (.+)$', WAVE_PLAN.read_text('utf-8'), re.MULTILINE)
    except: return []

def count_verifier_receipts(session_id):
    if not session_id or not RECEIPTS_DIR.exists(): return 0
    sid = session_id[:8]
    count = 0
    for f in RECEIPTS_DIR.glob('*.json'):
        if sid not in f.name and session_id not in f.name: continue
        try:
            if 'verifier' in json.loads(f.read_text('utf-8')).get('receipt_type', ''):
                count += 1
        except: pass
    return count

def count_receipts_found(required):
    if not required or not RECEIPTS_DIR.exists(): return 0
    stems = {f.stem for f in RECEIPTS_DIR.glob('*.json')}
    return sum(
        1 for r in required
        if any(r.replace('-receipt','').replace('_receipt','') in s for s in stems)
    )

def read_l8_gate():
    try:
        for line in L8_GATE.read_text('utf-8').split('\n')[:25]:
            if re.search(r'\bmet\b', line, re.I) and not re.search(r'not.?met', line, re.I):
                return True
    except: pass
    return False

# ── Context % from session jsonl ──────────────────────────────────────────────


# ── Git ───────────────────────────────────────────────────────────────────────

def _parse_remote_slug(url):
    url = url.strip().removesuffix('.git')
    m = re.search(r'[:/]([^/]+/[^/]+)$', url)
    return m.group(1) if m else None

def git_info(cwd):
    result = {'branch': None, 'remote': None, 'dirty': False}
    try:
        result['branch'] = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        result['dirty'] = bool(subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip())
        try:
            tracking = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
            ).decode().strip()
            remote_name = tracking.split('/')[0]
        except subprocess.CalledProcessError:
            remote_name = subprocess.check_output(
                ['git', 'remote'], cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
            ).decode().strip().split('\n')[0]
        if remote_name:
            url = subprocess.check_output(
                ['git', 'remote', 'get-url', remote_name],
                cwd=cwd, stderr=subprocess.DEVNULL, timeout=2,
            ).decode().strip()
            result['remote'] = _parse_remote_slug(url)
    except: pass
    return result

# ── Anthropic usage API ───────────────────────────────────────────────────────

def _read_creds():
    try:
        raw = json.loads(CREDS_FILE.read_text('utf-8'))
        return raw.get('claudeAiOauth', raw)
    except: return None

def _read_usage_cache():
    for path in (USAGE_CACHE, OMC_CACHE):
        try:
            d = json.loads(path.read_text('utf-8'))
            if time.time() - d.get('timestamp', 0) / 1000 < USAGE_TTL_S and d.get('data'):
                return d['data']
        except: pass
    return None

def _write_usage_cache(data):
    try:
        USAGE_CACHE.write_text(
            json.dumps({'timestamp': int(time.time() * 1000), 'data': data}), 'utf-8'
        )
    except: pass

def _fetch_usage(token):
    req = urllib.request.Request(
        'https://api.anthropic.com/api/oauth/usage',
        headers={'Authorization': f'Bearer {token}',
                 'anthropic-beta': 'oauth-2025-04-20',
                 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_S, context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode())
    except: return None

def _refresh_token(refresh):
    client_id = os.environ.get('CLAUDE_CODE_OAUTH_CLIENT_ID', '9d1c250a-e61b-44d9-88ed-5944d1962f5e')
    body = f'grant_type=refresh_token&refresh_token={urllib.request.quote(refresh)}&client_id={client_id}'
    req = urllib.request.Request(
        'https://platform.claude.com/v1/oauth/token',
        data=body.encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_S, context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode()).get('access_token')
    except: return None

def _parse_usage(raw):
    def clamp(v): return max(0, min(100, round(float(v)))) if v is not None else None
    fh = raw.get('five_hour', {})
    wk = raw.get('seven_day', {})
    result = {'fiveHour': clamp(fh.get('utilization')), 'fiveHourResets': fh.get('resets_at')}
    if 'utilization' in wk:
        result['weekly']       = clamp(wk.get('utilization'))
        result['weeklyResets'] = wk.get('resets_at')
    return result

def _format_reset(iso):
    if not iso: return None
    try:
        import datetime
        dt  = datetime.datetime.fromisoformat(iso.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff_m = int((dt - now).total_seconds() / 60)
        if diff_m <= 0: return None
        h, m = divmod(diff_m, 60)
        d, h = divmod(h, 24)
        return f'{d}d{h}h' if d else f'{h}h{m:02d}m'
    except: return None

def get_usage(no_usage=False):
    if no_usage: return {}
    cached = _read_usage_cache()
    if cached:
        return _parse_usage(cached) if 'five_hour' in cached else cached
    creds = _read_creds()
    if not creds: return {}
    token = creds.get('accessToken', '')
    raw   = _fetch_usage(token) or (_fetch_usage(_refresh_token(creds.get('refreshToken', ''))) if creds.get('refreshToken') else None)
    if raw:
        _write_usage_cache(raw)
        return _parse_usage(raw)
    _write_usage_cache(None)
    return {}

# ── Module colors ─────────────────────────────────────────────────────────────

MODULE_COLOR = {
    'executor': BPR, 'verifier': CYN, 'guard': YEL,
    'archive': GRN,  'recipe': SPR,   'specify': SPR,
    'decompose': SPR,'rollback': RED,  'dream': DPR,
}

def module_color(name):
    return MODULE_COLOR.get(name.lower(), PUR)

# ── Render ────────────────────────────────────────────────────────────────────

def render(no_git=False, no_usage=False):
    cwd   = os.getcwd()
    state = read_state()
    usage = get_usage(no_usage=no_usage)
    git   = {} if no_git else git_info(cwd)

    # ── Line 1: brand + skill (no divider) | repo (branch) | usage ──────────
    mod   = (state or {}).get('active_module') or 'IDLE'
    brand = spr('[WABBLE]')
    parts1 = [brand]

    branch = git.get('branch')
    remote = git.get('remote')
    dirty  = git.get('dirty', False)
    if branch or remote:
        repo  = dim(remote) if remote else dim('Local')
        b_col = module_color(mod) if (dirty and state) else SPR
        bpart = f' {_c(b_col, f"({branch})")}' if branch else ''
        parts1.append(repo + bpart)

    if usage:
        fh = usage.get('fiveHour')
        wk = usage.get('weekly')
        if fh is not None:
            s   = f'{dim("5H:")}{spr(f"{fh}%")}'
            rst = _format_reset(usage.get('fiveHourResets'))
            if rst: s += dim(f' ({rst})')
            parts1.append(s)
        if wk is not None:
            s   = f'{dim("1W:")}{spr(f"{wk}%")}'
            rst = _format_reset(usage.get('weeklyResets'))
            if rst: s += dim(f' ({rst})')
            parts1.append(s)

    line1 = SEP.join(parts1)

    return line1

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = set(sys.argv[1:])
    try:
        print(render(
            no_git   = '--no-git'   in args,
            no_usage = '--no-usage' in args,
        ))
    except Exception:
        print(spr('[WABBLE]'))
