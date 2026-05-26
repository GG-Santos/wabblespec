# wabblespec-statusline.ps1 — WabbleSpec statusline badge command
# Reads the session flag file written by wabblespec-session-start.js
# Output: short badge string for the Claude Code statusline

$claudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $env:USERPROFILE ".claude" }
$flagPath = Join-Path $claudeDir ".wabblespec-session"

if (-not (Test-Path $flagPath)) {
    Write-Output "[WS -]"
    exit
}

$content = (Get-Content $flagPath -Raw 2>$null)
if (-not $content) {
    Write-Output "[WS -]"
    exit
}

$content = $content.Trim()

# Whitelist: only alphanumeric, colon, pipe, hyphen, underscore, period
if ($content -notmatch '^[a-zA-Z0-9:|_.\-]+$') {
    Write-Output "[WS]"
    exit
}

if ($content -eq "idle") {
    Write-Output "[WS idle]"
} else {
    # task:some-id|waves:2|phase:execution -> "WS task some-id w:2"
    $taskId = if ($content -match 'task:([^|]+)') { $Matches[1] } else { "?" }
    $waves  = if ($content -match 'waves:([^|]+)') { $Matches[1] } else { "?" }
    Write-Output "[WS $taskId w:$waves]"
}
