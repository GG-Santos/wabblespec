# wabblespec-statusline.ps1 — WabbleSpec purple HUD for Claude Code statusLine
# Delegates to wabblespec-hud.py for full 3-line ANSI output.
# Falls back to a plain badge if Python is unavailable or errors out.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$hudScript  = Join-Path $scriptDir "..\shared\scripts\wabblespec-hud.py"
$hudScript  = [System.IO.Path]::GetFullPath($hudScript)

if (Test-Path $hudScript) {
    $env:PYTHONUTF8 = "1"
    $output = python $hudScript 2>$null
    if ($LASTEXITCODE -eq 0 -and $output) {
        Write-Output $output
        exit
    }
}

# Fallback: minimal badge from flag file (original behavior)
$claudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $env:USERPROFILE ".claude" }
$flagPath  = Join-Path $claudeDir ".wabblespec-session"

if (-not (Test-Path $flagPath)) {
    Write-Output "[WABBLE -]"
    exit
}

$content = (Get-Content $flagPath -Raw 2>$null)
if (-not $content) { Write-Output "[WABBLE -]"; exit }

$content = $content.Trim()
if ($content -notmatch '^[a-zA-Z0-9:|_.\-]+$') { Write-Output "[WABBLE]"; exit }

if ($content -eq "idle") {
    Write-Output "[WABBLE idle]"
} else {
    $taskId = if ($content -match 'task:([^|]+)') { $Matches[1] } else { "?" }
    $waves  = if ($content -match 'waves:([^|]+)') { $Matches[1] } else { "?" }
    Write-Output "[WABBLE $taskId w:$waves]"
}
