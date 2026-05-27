"""
wabble-sound.py  —  WabbleSpec lifecycle audio feedback.

Three invocation modes:

  --hook         (Claude Code hook registration)
                 Read stdin once, spawn self as detached worker, exit
                 immediately.  Never blocks Claude Code.  Register this
                 mode in settings.json for every hook event that needs
                 audio (PreToolUse, PostToolUse, SessionStart, etc.).

  --stdin-file F (worker mode — spawned by --hook automatically)
                 Read hook JSON from file F, delete it, parse, play.
                 Never invoke directly.

  --event NAME   (direct lifecycle trigger)
                 Play a named WabbleSpec lifecycle sound with no stdin.
                 Used by Python scripts (archive.py) that are already
                 running in a detached Popen.

Soundpack: .wabblespec/engine/shared/sounds/  (startrek-bridge layout)
  system/      — session-start, compacting
  interactive/ — message-sent, notification
  completion/  — agent-complete, completion
  success/     — success, wave-complete
  error/       — error, guard-blocked
  loading/     — bash-start, git-commit-start, read-start, …

Env override: WABBLE_SOUNDPACK_DIR=/path/to/soundpack
Env disable:  WABBLE_SOUND_ENABLED=0

Silent-fail contract: every error is caught; never raises; never blocks caller.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Event categories  (mirrors claudio internal/hooks/parser.go EventCategory)
# ---------------------------------------------------------------------------

LOADING     = "loading"
SUCCESS     = "success"
ERROR       = "error"
INTERACTIVE = "interactive"
COMPLETION  = "completion"
SYSTEM      = "system"

# ---------------------------------------------------------------------------
# EventContext
# ---------------------------------------------------------------------------

@dataclass
class EventContext:
    category: str     = INTERACTIVE
    tool_name: str    = ""
    original_tool: str = ""
    is_success: bool  = False
    has_error: bool   = False
    sound_hint: str   = ""
    file_type: str    = ""
    operation: str    = ""


# ---------------------------------------------------------------------------
# WabbleSpec lifecycle event table
# ---------------------------------------------------------------------------

_LIFECYCLE_MAP: dict[str, EventContext] = {
    "session-start":  EventContext(category=SYSTEM,      sound_hint="session-start",  operation="session-start"),
    "task-start":     EventContext(category=SYSTEM,      sound_hint="task-start",     operation="task-start"),
    "wave-start":     EventContext(category=LOADING,     sound_hint="wave-start",     operation="wave-start"),
    "wave-complete":  EventContext(category=SUCCESS,     sound_hint="wave-complete",  operation="wave-complete"),
    "archive-done":   EventContext(category=COMPLETION,  sound_hint="archive-done",   operation="archive-done"),
    "pre-compact":    EventContext(category=SYSTEM,      sound_hint="compacting",     operation="compact"),
    "compacting":     EventContext(category=SYSTEM,      sound_hint="compacting",     operation="compact"),
    "instinct-run":   EventContext(category=SYSTEM,      sound_hint="instinct-run",   operation="instinct-run"),
    "synth-run":      EventContext(category=SYSTEM,      sound_hint="synth-run",      operation="synth-run"),
    "guard-blocked":  EventContext(category=ERROR,       sound_hint="guard-blocked",  operation="guard-blocked"),
    "message-sent":   EventContext(category=INTERACTIVE, sound_hint="message-sent",   operation="prompt"),
    "notification":   EventContext(category=INTERACTIVE, sound_hint="notification",   operation="notification"),
    "agent-complete": EventContext(category=COMPLETION,  sound_hint="agent-complete", operation="stop"),
}


def make_lifecycle_context(event_name: str) -> EventContext:
    ctx = _LIFECYCLE_MAP.get(event_name)
    if ctx is None:
        return EventContext(category=INTERACTIVE, sound_hint="default", operation="unknown")
    # Return a copy so callers cannot mutate the table
    from dataclasses import replace
    return replace(ctx)


# ---------------------------------------------------------------------------
# Hook JSON parser  (mirrors claudio internal/hooks/parser.go GetContext)
# ---------------------------------------------------------------------------

_KNOWN_SUBCOMMANDS: dict[str, set] = {
    "git":    {"add","commit","push","pull","clone","checkout","branch","merge",
               "rebase","status","log","diff","fetch","remote","tag","stash","reset"},
    "npm":    {"install","uninstall","update","start","stop","test","run","build"},
    "docker": {"build","run","pull","push","start","stop","ps","exec","compose"},
    "go":     {"build","run","test","install","get","mod","fmt","vet"},
    "pip":    {"install","uninstall","list","show","freeze"},
    "cargo":  {"build","run","test","check","fmt","clippy"},
    "gh":     {"pr","issue","repo","release","auth","workflow"},
}


def _extract_command(event: dict) -> Optional[dict]:
    tool_input = event.get("tool_input")
    if not tool_input:
        return None
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(tool_input, dict):
        return None
    command_str = tool_input.get("command", "")
    if not command_str:
        return None
    words = [w for w in command_str.split() if not w.startswith("-")]
    if not words:
        return None
    cmd = words[0]
    sub: Optional[str] = None
    if len(words) >= 2:
        candidate = words[1]
        if "/" not in candidate and "." not in candidate and "://" not in candidate:
            known = _KNOWN_SUBCOMMANDS.get(cmd)
            if known is None or candidate in known:
                sub = candidate
    return {"command": cmd, "subcommand": sub} if sub else {"command": cmd}


def _analyze_tool_response(event: dict) -> tuple[bool, bool, str]:
    """Returns (success, has_error, error_type)."""
    response = event.get("tool_response")
    if not response:
        return True, False, ""
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return False, True, ""
    if not isinstance(response, dict):
        return True, False, ""
    if response.get("interrupted"):
        return False, True, "tool-interrupted"
    if response.get("stderr", ""):
        return False, True, ""
    return True, False, ""


def _detect_notification_type(event: dict) -> str:
    msg = (event.get("message") or "").lower()
    if any(kw in msg for kw in ("permission", "needs permission")):
        return "notification-permission"
    if any(kw in msg for kw in ("idle", "been idle")):
        return "notification-idle"
    return "notification"


def parse_hook_event(data: bytes) -> Optional[EventContext]:
    """Parse Claude Code hook JSON payload into an EventContext."""
    try:
        event = json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(event, dict):
        return None

    event_name = event.get("hook_event_name", "")
    tool_name  = event.get("tool_name") or ""
    ctx        = EventContext(tool_name=tool_name)

    if event_name == "UserPromptSubmit":
        ctx.category   = INTERACTIVE
        ctx.sound_hint = "message-sent"
        ctx.operation  = "prompt"

    elif event_name == "PreToolUse":
        ctx.category  = LOADING
        ctx.operation = "tool-start"
        cmd_info      = _extract_command(event) if tool_name == "Bash" else None
        if cmd_info:
            ctx.original_tool = "Bash"
            ctx.tool_name     = cmd_info["command"]
            sub               = cmd_info.get("subcommand") or ""
            if sub:
                ctx.sound_hint = f"{cmd_info['command'].lower()}-{sub.lower()}-start"
            else:
                ctx.sound_hint = f"{cmd_info['command'].lower()}-start"
        elif tool_name:
            ctx.sound_hint = f"{tool_name.lower()}-start"

    elif event_name == "PostToolUse":
        success, has_error, error_type = _analyze_tool_response(event)
        ctx.is_success = success
        ctx.has_error  = has_error
        ctx.category   = ERROR if has_error else SUCCESS
        ctx.operation  = "tool-complete"
        cmd_info       = _extract_command(event) if tool_name == "Bash" else None
        suffix         = "error" if has_error else "success"
        if cmd_info:
            ctx.original_tool = "Bash"
            ctx.tool_name     = cmd_info["command"]
            sub               = cmd_info.get("subcommand") or ""
            if sub:
                ctx.sound_hint = f"{cmd_info['command'].lower()}-{sub.lower()}-{suffix}"
            else:
                ctx.sound_hint = f"{cmd_info['command'].lower()}-{suffix}"
        elif tool_name:
            if error_type:
                ctx.sound_hint = error_type
            else:
                ctx.sound_hint = f"{tool_name.lower()}-{suffix}"

    elif event_name == "Stop":
        ctx.category   = COMPLETION
        ctx.sound_hint = "agent-complete"
        ctx.operation  = "stop"

    elif event_name == "SubagentStop":
        ctx.category   = COMPLETION
        ctx.sound_hint = "subagent-complete"
        ctx.operation  = "subagent-stop"

    elif event_name == "SessionStart":
        ctx.category   = SYSTEM
        ctx.sound_hint = "session-start"
        ctx.operation  = "session-start"

    elif event_name == "PreCompact":
        ctx.category   = SYSTEM
        ctx.sound_hint = "compacting"
        ctx.operation  = "compact"

    elif event_name == "Notification":
        ctx.category   = INTERACTIVE
        ctx.sound_hint = _detect_notification_type(event)
        ctx.operation  = "notification"

    else:
        ctx.category   = INTERACTIVE
        ctx.sound_hint = "default"
        ctx.operation  = "unknown"

    return ctx


# ---------------------------------------------------------------------------
# Sound mapper  (mirrors claudio internal/sounds/mapper.go fallback chain)
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """mirrors sounds/mapper.go normalizeName."""
    name = name.lower().replace(" ", "-").replace("_", "-")
    out  = []
    for ch in name:
        out.append(ch if (ch.isalnum() or ch == "-") else "-")
    name = "".join(out)
    while "--" in name:
        name = name.replace("--", "-")
    return name.strip("-")


def _operation_suffix(category: str, operation: str) -> str:
    if category == SUCCESS:     return "success"
    if category == ERROR:       return "error"
    if category == LOADING:     return "start"
    if category == COMPLETION:  return "complete"
    if "start"    in operation: return "start"
    if "complete" in operation: return "complete"
    return ""


def map_sound(ctx: EventContext) -> list[str]:
    """
    Build a fallback path list (no extensions) for this context.
    Returns paths in priority order; first existing file wins.
    Mirrors claudio's 5-level fallback chain.
    """
    paths: list[str] = []
    cat = ctx.category

    # Level 1: exact hint
    if ctx.sound_hint:
        paths.append(f"{cat}/{_normalize(ctx.sound_hint)}")

    # Level 2: tool + suffix  (when tool name was extracted)
    if ctx.tool_name:
        suffix = _operation_suffix(cat, ctx.operation)
        if suffix:
            paths.append(f"{cat}/{_normalize(ctx.tool_name)}-{suffix}")

    # Level 3: original tool + suffix  (when Bash was unwrapped to command)
    if ctx.original_tool and ctx.original_tool != ctx.tool_name:
        suffix = _operation_suffix(cat, ctx.operation)
        if suffix:
            paths.append(f"{cat}/{_normalize(ctx.original_tool)}-{suffix}")

    # Level 4: operation-specific
    if ctx.operation:
        paths.append(f"{cat}/{_normalize(ctx.operation)}")

    # Level 5: category-specific fallback
    paths.append(f"{cat}/{cat}")

    # Level 6: default
    paths.append("default")

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def resolve_sound(paths: list[str], soundpack_dir: Path) -> Optional[Path]:
    """Walk fallback chain; return the first file found. Tries mp3, wav, aiff."""
    for rel in paths:
        for ext in (".mp3", ".wav", ".aiff"):
            candidate = soundpack_dir / (rel + ext)
            if candidate.exists():
                return candidate
    return None


# ---------------------------------------------------------------------------
# Audio playback  (Windows-native; silent-fail everywhere)
# ---------------------------------------------------------------------------

def play_sound(path: Path, volume: float = 0.7) -> bool:
    """Play an audio file. Silent-fail: never raises."""
    if not path or not path.exists():
        return False
    try:
        if sys.platform == "win32":
            return _play_windows(path, volume)
        return _play_unix(path)
    except Exception:
        return False


def _play_mci(abs_path: str) -> bool:
    """
    Play via Windows MCI API (winmm.dll mciSendStringW).
    Works in non-interactive/detached sessions where WMP COM stays in
    playState 9 (Transitioning) and never produces audio.
    Blocks the calling thread until playback completes.
    """
    try:
        import ctypes
        winmm = ctypes.windll.winmm
        alias = "wabble_snd"
        r = winmm.mciSendStringW(
            f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, None
        )
        if r != 0:
            return False
        try:
            r2 = winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
        finally:
            winmm.mciSendStringW(f'close {alias}', None, 0, None)
        return r2 == 0
    except Exception:
        return False


def _play_windows(path: Path, volume: float) -> bool:
    abs_path = str(path.resolve())
    ext      = path.suffix.lower()

    if ext == ".wav":
        # System.Media.SoundPlayer — built-in .NET, synchronous, WAV only
        ps_cmd = f'(New-Object System.Media.SoundPlayer "{abs_path}").PlaySync()'
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-WindowStyle", "Hidden", "-Command", ps_cmd],
            capture_output=True, timeout=15
        )
        return r.returncode == 0

    if ext in (".mp3", ".aiff"):
        # MCI API via ctypes — no COM, no subprocess, works in all session types
        return _play_mci(abs_path)

    return False


def _play_unix(path: Path) -> bool:
    """Try common Unix audio players in priority order."""
    import shutil
    for player, extra_args in [
        ("paplay",  []),
        ("aplay",   []),
        ("afplay",  []),
        ("mpg123",  ["-q"]),
        ("ffplay",  ["-nodisp", "-autoexit", "-loglevel", "quiet"]),
    ]:
        if shutil.which(player):
            r = subprocess.run(
                [player] + extra_args + [str(path)],
                capture_output=True, timeout=30
            )
            return r.returncode == 0
    return False


# ---------------------------------------------------------------------------
# Soundpack directory resolution
# ---------------------------------------------------------------------------

def get_soundpack_dir() -> Path:
    """
    Resolve the soundpack directory.
    Priority: WABBLE_SOUNDPACK_DIR env var -> .wabblespec/engine/shared/sounds/ -> silent fail.
    """
    env_dir = os.environ.get("WABBLE_SOUNDPACK_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.exists():
            return p

    # Walk up from this script to find the repo root (.wabblespec/engine/shared/sounds/)
    # Script lives at .wabblespec/engine/shared/scripts/wabble-sound.py
    # -> parent = .wabblespec/engine/shared/scripts/  -> parent = .wabblespec/engine/shared/  -> parent = repo root
    script_dir   = Path(__file__).resolve().parent       # .wabblespec/engine/shared/scripts/
    shared_dir   = script_dir.parent                     # .wabblespec/engine/shared/
    sounds_local = shared_dir / "sounds"
    if sounds_local.exists():
        return sounds_local

    # Fallback: cwd-relative (for callers that run from repo root)
    cwd_sounds = Path.cwd() / ".wabblespec" / "engine" / "shared" / "sounds"
    if cwd_sounds.exists():
        return cwd_sounds

    return sounds_local  # May not exist; resolve_sound handles silently


# ---------------------------------------------------------------------------
# Hook self-detach mode  (--hook)
# ---------------------------------------------------------------------------

def _run_hook_mode(args) -> None:
    """
    Non-blocking hook driver for settings.json registration.

    Sequence:
      1. Read all stdin (Claude Code sends hook JSON payload here).
      2. Write '{}' to stdout so Claude Code gets a valid response immediately.
      3. Write stdin data to a temp file.
      4. Spawn self as a detached worker with --stdin-file <path>.
      5. Exit.  Worker plays the sound independently.

    Never raises; always calls sys.exit(0).
    """
    import tempfile

    # Read stdin — drain the full payload before writing response
    try:
        data = sys.stdin.buffer.read()
    except Exception:
        data = b''

    # Respond to Claude Code immediately (valid JSON for all hook types)
    sys.stdout.write('{}')
    sys.stdout.flush()

    if not data.strip():
        sys.exit(0)

    # Write payload to temp file
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='.json', prefix='wabble-hook-'
        ) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
    except Exception:
        sys.exit(0)

    # Spawn detached worker
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        '--stdin-file', tmp_path,
        '--volume', str(args.volume),
    ]
    if args.soundpack:
        cmd += ['--soundpack', args.soundpack]

    try:
        if sys.platform == 'win32':
            flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
        else:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Respect global disable flag
    if os.environ.get("WABBLE_SOUND_ENABLED", "1") == "0":
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="WabbleSpec lifecycle audio feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--hook",
        action="store_true",
        help="Hook mode: read stdin, spawn detached worker, exit immediately. "
             "Register this in settings.json for non-blocking hook audio.",
    )
    parser.add_argument(
        "--stdin-file",
        metavar="PATH",
        help=argparse.SUPPRESS,  # Internal: used by detached worker spawned by --hook
    )
    parser.add_argument(
        "--event", "-e",
        metavar="NAME",
        help="WabbleSpec lifecycle event (session-start, archive-done, wave-complete, …). "
             "If omitted, reads Claude Code hook JSON from stdin.",
    )
    parser.add_argument(
        "--soundpack", "-s",
        metavar="PATH",
        help="Override soundpack directory path.",
    )
    parser.add_argument(
        "--volume", "-v",
        type=float,
        default=0.7,
        metavar="0.0-1.0",
        help="Playback volume (default 0.7).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved sound path; do not play.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="No-op mode; exit 0 immediately.",
    )
    args = parser.parse_args()

    if args.silent:
        sys.exit(0)

    # --hook: non-blocking mode for Claude Code hook registration.
    # Read stdin, write to temp file, spawn detached worker, exit immediately.
    if args.hook:
        _run_hook_mode(args)
        sys.exit(0)  # _run_hook_mode always exits; this is unreachable

    # Build EventContext
    if args.stdin_file:
        # Worker mode: spawned by --hook, reads from temp file
        try:
            with open(args.stdin_file, 'rb') as f:
                data = f.read()
            try:
                os.unlink(args.stdin_file)
            except Exception:
                pass
        except Exception:
            sys.exit(0)
        ctx = parse_hook_event(data)
        if ctx is None:
            sys.exit(0)
    elif args.event:
        ctx = make_lifecycle_context(args.event)
    else:
        # Direct stdin mode (testing / pipe usage)
        try:
            data = sys.stdin.buffer.read()
        except Exception:
            sys.exit(0)
        if not data.strip():
            sys.exit(0)
        ctx = parse_hook_event(data)
        if ctx is None:
            sys.exit(0)

    # Resolve soundpack directory
    soundpack_dir = Path(args.soundpack) if args.soundpack else get_soundpack_dir()

    # Build fallback chain and find first existing file
    paths    = map_sound(ctx)
    resolved = resolve_sound(paths, soundpack_dir)

    if resolved is None:
        sys.exit(0)  # No sound available; silent pass

    if args.dry_run:
        print(f"[wabble-sound] {ctx.category}/{ctx.sound_hint} -> {resolved}")
        sys.exit(0)

    play_sound(resolved, args.volume)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # Absolute silent-fail guarantee
